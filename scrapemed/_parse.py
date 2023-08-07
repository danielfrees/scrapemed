
"""
Parse module for grabbing metadata, text, tables, figures, etc. 
from XML trees representing PMC articles.

DTD for the XML should be NLM articleset 2.0. 
Otherwise the behavior here may not be as expected.

Middleman between the "scrape" module and the "paper" module for scrapemed.

"""

from ast import IsNot
from copy import copy
from typing import Text, List, Dict, Tuple
from typing import Union
import scrapemed.scrape as scrape
import lxml.etree as ET
from scrapemed.utils import basicBiMap
from scrapemed._text import TextParagraph
from scrapemed._text import TextSection
from datetime import datetime
import pandas as pd
import warnings

#-----------Custom Warnings & Exceptions for Parsing------------
class unexpectedMultipleMatchWarning(Warning):
    """
    Warned when one match expected, but multiple found.
    """
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return repr(self.message)

class unexpectedZeroMatchWarning(Warning):
    """
    Warned when one or more matches expected, and none are found.
    """
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return repr(self.message)

class badTextFormattingWarning(Warning):
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return repr(self.message)
#-----------End Custom Warnings & Exceptions for Parsing------------

#--------------------GENERATE PAPER DICTIONARY GIVEN PMCID-------------------------------
def generate_paper_dict(pmcid:int, email:str, download:bool = False, validate:bool = True, verbose:bool = False)->dict:
    """TODO
    Wrapper that scrapes a PMC article specified by PMCID from the web (through scrape module),
    then parses the XML retrieved into a dictionary of useful values. 

    Middleman between scrape.py and paper.py.

    Paper objects in paper.py handle actual dictionary -> object conversion.
    """
    if verbose: 
        print(f"Generating Paper object for PMCID = {pmcid}...")
    #DOWNLOAD XML TREE AND GET ROOT
    paper_tree = scrape.get_xml(pmcid=pmcid, email=email, download=download, validate=validate, verbose=verbose)
    root = paper_tree.getroot()

    #KEEP TRACK OF XREFS, TABLES, FIGURES IN BIMAP
    #(THIS WILL BE MODIFIED DURING TEXT RETRIEVAL WHEN HTML REF TAGS ARE SPLIT OUT)
    ref_map = basicBiMap()

    #STORE EXTRACTED INFO IN PAPER DICT
    paper_dict = {
        'Title': gather_title(root),
        'Authors': gather_authors(root),
        'Non-Author Contributors': gather_non_author_contributors(root),
        'Abstract': gather_abstract(root, ref_map),
        'Body': gather_body(root, ref_map),
        'Journal ID': gather_journal_id(root),
        'Journal Title': gather_journal_title(root),
        'ISSN': gather_issn(root),
        'Publisher Name': gather_publisher_name(root),
        'Publisher Location': gather_publisher_location(root),
        'Article ID': gather_article_id(root),
        'Article Types': gather_article_types(root),
        'Article Categories': gather_article_categories(root),
        'Published Date': gather_published_date(root),
        'Volume': gather_volume(root),
        'Issue': gather_issue(root),
        'First Page': gather_fpage(root),
        'Last Page': gather_lpage(root),
        'Permissions': gather_permissions(root),
        'Copyright Statement': gather_copyright_statement(root),
        'License': gather_license(root),
        'Funding': gather_funding(root),
        'Footnote': gather_footnote(root),
        'Acknowledgements': gather_acknowledgements(root),
        'Notes': gather_notes(root),
        'Reference List': gather_reference_list(root),
        'Ref Map': ref_map
        }

    if verbose:
        print("Finished generating Paper object for PMCID = {pmcid}...")

    return paper_dict

def generate_data_dict()->dict:
    """
    Returns a static definition of each of the elements returned in a Paper dict.
    """
    data_dict = {
        'Title': "",
        'Authors': "",
        'Non-Author Contributors': "",
        'Abstract': "",
        'Body': "",
        'Journal ID': "",
        'Journal Title': "",
        'ISSN': "",
        'Publisher Name': "",
        'Publisher Location': "",
        'Article ID': "",
        'Article Types': "",
        'Article Categories': "",
        'Published Date': "",
        'Volume': "",
        'Issue': "",
        'Permissions': "",
        'Copyright Statement': "",
        'License': "",
        'Funding': "",
        'Footnote': "",
        'Acknowledgements': "",
        'Notes': "",
        'Reference List': "",
        'Ref Map': ""
        }
    
    return data_dict

def gather_title(root: ET.Element)->str:
    """
    Grab the title of a PMC paper from its XML root.
    """
    matches = root.xpath('//article-meta/title-group/article-title/text()')
    if len(matches) > 1: 
        warnings.warn("Warning! Multiple titles matched. Setting Paper.title to the first match.", unexpectedMultipleMatchWarning)
    title = matches[0]

    return title

def _get_contributor_tuples(root: ET.Element, contributors: List[ET.Element]) -> List[Tuple]:
    """
    Helper function to grab tuples of contributor information.

    Input:
    [root]: root of the XML tree to search
    [contributors]: list of lxml Element objects to grab information from

    Output:
    A list of tuples of contributor info in the form (contrib_type, first_name, last_name, address, affiliations).
    """
    contributor_tuples = []
    for contributor in contributors:
        contrib_type = contributor.get("contrib-type").capitalize()
        if contrib_type:
            contrib_type = contrib_type.strip()
        first_name = contributor.findtext(".//given-names")
        if first_name:
            first_name = first_name.strip()
        last_name = contributor.findtext(".//surname")
        if last_name:
            last_name = last_name.strip()
        address = contributor.findtext(".//address/email")
        if address:
            address = address.strip()
        affiliations = []
        aff_paths = contributor.xpath(".//xref[@ref-type='aff']")
        for aff in aff_paths:
            aff_id = aff.get('rid')
            aff_texts = root.xpath(f"//contrib-group/aff[@id='{aff_id}']/text()[not(parent::label)]")
            if len(aff_texts) > 1:
                warnings.warn("Multiple affiliations with the same ID found. Check XML Formatting.", unexpectedMultipleMatchWarning)
            
            institutions = root.xpath(f"//contrib-group/aff[@id='{aff_id}']/institution-wrap/institution/text()")
            institutions = ' '.join([str(inst) for inst in institutions])

            #Generate affiliation text
            affiliation = ""
            if institutions:
                affiliation = f"{aff_id.strip()}: {institutions}{aff_texts[0].strip()}"
            else:
                affiliation = f"{aff_id.strip()}: {aff_texts[0].strip()}"
            affiliations.append(affiliation)

        contributor_tuples.append((contrib_type, first_name, last_name, address, affiliations))
    return contributor_tuples


def gather_authors(root: ET.Element)-> pd.DataFrame:
    """
    Gather authors and their emails and affiliations from a PMC XML.

    Returns a DataFrame of author info.
    """
    authors = root.xpath(".//contrib[@contrib-type='author']")
    if not authors:
        warnings.warn("Warning! Authors could not be matched", unexpectedZeroMatchWarning)

    # Extract the first and last names of the authors and store them in a list
    author_tuples = _get_contributor_tuples(root=root, contributors=authors)

    authors_df = pd.DataFrame(author_tuples)
    authors_df.columns = ['Contributor_Type', 'First_Name', 'Last_Name', 'Email_Address', 'Affiliations']

    return authors_df

def gather_non_author_contributors(root: ET.Element) -> Union[str, pd.DataFrame]:
    """
    Gather non-author contributors from PMC XML.

    Returns either a string indicating none found, or a DataFrame of contributor info.
    """

    return_val = "No non-author contributors were found after parsing this paper."

    non_author_contributors = root.xpath(".//contrib[not(@contrib-type='author')]")
    if non_author_contributors:
        non_author_tuples = _get_contributor_tuples(root=root, contributors=non_author_contributors)
        non_authors_df = pd.DataFrame(non_author_tuples)
        non_authors_df.columns = ['Contributor_Type', 'First_Name', 'Last_Name', 'Email_Address', 'Affiliations']
        return_val = non_authors_df

    return return_val

def gather_abstract(root: ET.Element, ref_map:basicBiMap)->List[Union[TextSection, TextParagraph]]:
    """
    Extract all abstract text sections from an xml, output as a list of TextSections. 
    """
    abstract = []

    #get abstract subtree from XML
    matches = root.xpath('//abstract')
    if len(matches) > 1: 
        warnings.warn("Warning! Multiple abstracts matched. Filling in Paper.abstract with the first match.", unexpectedMultipleMatchWarning)
    abstract_root = matches[0]

    #iterate through abstract subtree and add in text sections (recursive) and text paragraphs (flat)
    for child in abstract_root.iterchildren():
        if child.tag == 'sec':
            abstract.append(TextSection(sec_root=child, ref_map=ref_map))
        elif child.tag == 'p':
            abstract.append(TextParagraph(child))
        else:
            warnings.warn(f"Warning! Unexpected child with of type {child.tag} found under an XML <abstract> tag.")

    return abstract

def gather_body(root: ET.Element, ref_map:basicBiMap)->List[TextSection]:
    """
    Extract all body text sections from an xml, output as a list of TextSections. 
    """
    body = []

    #get abstract subtree from XML
    matches = root.xpath('//body')
    if len(matches) > 1: 
        warnings.warn("Warning! Multiple 'body's matched. Filling in Paper.body with the first match.", unexpectedMultipleMatchWarning)
    body_root = matches[0]

    #iterate through abstract subtree and get dict of title, bodytext pairs
    for sec in body_root.iterchildren('sec'):
        body.append(TextSection(sec_root=sec, ref_map=ref_map))

    return body

def gather_journal_id(root: ET.Element) -> dict:
    """
    Gather Journal ID from PMC XML.
    """
    journal_ids = root.xpath("//journal-meta/journal-id")
    id_dict = {journal_id.get("journal-id-type"): journal_id.text for journal_id in journal_ids}

    return id_dict

def gather_journal_title(root: ET.Element) -> Union[List[str], str]:
    """
    Gather Journal Title from PMC XML.
    """
    return_val = None
    titles = []
    title_groups = root.xpath("//journal-meta/journal-title-group")
    for title_group in title_groups:
        titles.extend(title_group.getchildren())
    #might have multiple journals & journal titles
    if len(titles) > 1:
        return_val = [title.text for title in titles]
    else:
        return_val = titles[0].text
    return return_val

def gather_issn(root: ET.Element) -> dict:
    """
    Gather ISSN from PMC XML.
    """
    issns = root.xpath("//journal-meta/issn")
    issn_dict = {issn.get("pub-type"): issn.text for issn in issns}

    return issn_dict

def gather_publisher_name(root: ET.Element) -> Union[str, List[str]]:
    """
    Gather Publisher Name/s from PMC XML.
    """
    publisher_name_or_names = None
    publishers = root.xpath("//journal-meta/publisher/publisher-name")
    if len(publishers) == 1:
        publisher_name_or_names = publishers[0].text
    else:
        publisher_name_or_names = [publisher.text for publisher in publishers]
    return publisher_name_or_names

def gather_publisher_location(root: ET.Element) -> Union[str, List[str]]:
    """
    Gather Publisher Location/s from PMC XML.
    """
    publisher_loc_or_locs = None
    publisher_locs = root.xpath("//journal-meta/publisher/publisher-loc")
    if len(publisher_locs) == 1:
        publisher_loc_or_locs = publisher_locs[0].text
    else:
        publisher_loc_or_locs = [publisher_loc.text for publisher_loc in publisher_locs]
    return publisher_loc_or_locs

def gather_article_id(root: ET.Element) -> Dict[str, str]:
    """
    Gather Article IDs from PMC XML.
    """
    article_ids = root.xpath("//article-meta/article-id")
    id_dict = {article_id.get("pub-id-type"): article_id.text for article_id in article_ids}
    
    return id_dict

def gather_article_types(root: ET.Element) -> List[str]:
    """
    Gather Article Types from PMC XML. 

    Article Type(s) are article-categories marked by the subj-group-type 'heading'.
    """
    matches = root.xpath("//article-meta/article-categories")
    if len(matches) > 1: 
        warnings.warn("Warning! Multiple 'article-categories' lists matched. Filling in Paper.article_categories with the first match.", unexpectedMultipleMatchWarning)
    article_categories = matches[0]
    heading_categories = article_categories.xpath("subj-group[@subj-group-type='heading']/subject")
    heading_cats = [heading_cat.text for heading_cat in heading_categories]

    if not heading_cats:
        heading_cats = "No article type found (No article category with subject type 'heading')."
    return heading_cats

def gather_article_categories(root: ET.Element) -> List[str]:
    """
    Gather Other Article Categories from PMC XML.
    """
    matches = root.xpath("//article-meta/article-categories")
    if len(matches) > 1: 
        warnings.warn("Warning! Multiple 'article-categories' lists matched. Filling in Paper.article_categories with the first match.", unexpectedMultipleMatchWarning)
    article_categories = matches[0]
    other_categories = article_categories.xpath("subj-group[not(@subj-group-type='heading')]/subject")
    other_cats = [{other_cat.get("subj-group-type"): other_cat.text} for other_cat in other_categories]
    
    if not other_cats:
        other_cats = "No extra article categories found. Check .article_types for header categories."
    return other_cats

def gather_published_date(root: ET.Element) -> Dict[str, datetime]:
    """
    Gather Publishing Dates from PMC XML.

    Gathers electronic publishing, print publishing, etc. dates.
    """
    pdate_dict = {}
    matches = root.xpath("//article-meta/pub-date")
    for match in matches:
        pub_type = match.get("pub-type")

        year = 1 #default
        year_matches = match.xpath("year/text()")
        if year_matches:
            year = int(year_matches[0])
        else:
            warnings.warn("No year found for one of the publishing dates. Defaulting to year = 1!", unexpectedZeroMatchWarning)
        
        #if not month found, assume the 1st (standard practice - )
        month = 1
        month_matches = match.xpath("month/text()")
        if month_matches:
            month = int(month_matches[0])

        #if no day found, assume the 1st (standard practice)
        day = 1
        day_matches = match.xpath("day/text()")
        if day_matches:
            day = int(day_matches[0])

        full_date = datetime(year=year, month=month, day=day)
        pdate_dict[pub_type] = full_date
    return pdate_dict

def gather_volume(root: ET.Element) -> int:
    """
    Gather Volume # of Parent Publication from PMC XML.
    """
    matches = root.xpath("//article-meta/volume/text()")
    volume = None
    if not matches:
        warnings.warn("No Volume # found for Publication.", unexpectedZeroMatchWarning)
    else:
        volume = int(matches[0])

    return volume

def gather_issue(root: ET.Element) -> int:
    """
    Gather Issue # of Parent Publication from PMC XML.
    """

    matches = root.xpath("//article-meta/issue/text()")
    issue = None
    if not matches:
        warnings.warn("No Issue # found for Publication.", unexpectedZeroMatchWarning)
    else:
        issue = int(matches[0])

    return issue

def gather_fpage(root: ET.Element) -> int:
    """
    Gather First Page Number of this article in its parent publication.
    """
    matches = root.xpath("//article-meta/fpage/text()")
    fpage = None
    if not matches:
        warnings.warn("No First Page # found for Publication.", unexpectedZeroMatchWarning)
    else:
        fpage = int(matches[0])

    return fpage

def gather_lpage(root: ET.Element) -> int:
    """
    Gather Last Page Number of this article in its parent publication.
    """

    matches = root.xpath("//article-meta/lpage/text()")
    lpage = None
    if not matches:
        warnings.warn("No Last Page # found for Publication.", unexpectedZeroMatchWarning)
    else:
        lpage = int(matches[0])

    return lpage  

def gather_permissions(root: ET.Element) -> Dict[str, str]:
    """
    Gather Permissions from PMC XML.

    Copyright statement, license type, and license paragraph.
    """
    copyright_statement_matches = root.xpath("//article-meta/permissions/copyright-statement/text()")
    copyright_statement = "No copyright statement found."
    if not copyright_statement_matches:
        warnings.warn("No copyright statement found.", unexpectedZeroMatchWarning)
    elif len(copyright_statement_matches) > 1:
        warnings.warn("Multiple copyright statements found. Retrieving the first statement.", unexpectedMultipleMatchWarning)
    else:
        copyright_statement = copyright_statement_matches[0]

    license_matches = root.xpath("//article-meta/permissions/license")
    if not license_matches:
        warnings.warn("No license found.", unexpectedZeroMatchWarning)
    elif len(license_matches) > 1:
        warnings.warn("Multiple licenses found. Retrieving the first statement.", unexpectedMultipleMatchWarning)
    license = license_matches[0]
    license_type = license.get("license-type")
    if not license_type:
        license_type = "Not Specified"
    license_text = []
    for child in license.iterchildren():
        if child.tag == 'license-p':
            license_text.append(TextParagraph(p_root=child))
        else:
            warnings.warn(f"Warning! Unexpected child with of type {child.tag} found under an XML <license> tag.")
    license_text = '\n'.join([str(par) for par in license_text])

    permissions_dict = {"Copyright Statement" : copyright_statement,
                        "License Type": license_type,
                        "License Text": license_text
                        }
    return permissions_dict

def gather_copyright_statement(root: ET.Element) -> str:
    """
    Gather Copyright Statement from PMC XML.
    """
    return None

def gather_license(root: ET.Element) -> str:
    """
    Gather License from PMC XML.
    """
    return None

def gather_funding(root: ET.Element) -> str:
    """
    Gather Funding Data from PMC XML.
    """
    matches = root.xpath("//article-meta/funding-group")
    funding_institutions = []
    for match in matches:
        institutions = match.xpath('award-group/funding-source')

    return None


def gather_footnote(root: ET.Element) -> str:
    """
    Gather Footnote from PMC XML.
    """
    return None


def gather_acknowledgements(root: ET.Element) -> str:
    """
    Gather Acknowledgements from PMC XML.
    """
    return None


def gather_notes(root: ET.Element) -> str:
    """
    Gather Notes from PMC XML.
    """
    return None


def gather_reference_list(root: ET.Element) -> str:
    """
    Gather Reference List from PMC XML.
    """
    return None

#--------------------END GENERATE PAPER DICTIONARY GIVEN PMCID---------------------------
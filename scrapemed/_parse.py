
"""
Parse module for grabbing metadata, text, tables, figures, etc. 
from XML trees representing PMC articles.

DTD for the XML should be NLM articleset 2.0. 
Otherwise the behavior here may not be as expected.

Middleman between the "scrape" module and the "paper" module for scrapemed.

"""
import copy
from typing import Text, List, Dict, Tuple, Set
from typing import Union
import scrapemed.scrape as scrape
import lxml.etree as ET
from scrapemed.utils import basicBiMap
from scrapemed._text import TextParagraph, TextSection, TextTable, TextFigure
from datetime import datetime
import pandas as pd
import warnings
import textwrap
import uuid

#-----------Custom Warnings & Exceptions for Parsing------------
class unexpectedMultipleMatchWarning(Warning):
    """
    Warned when one match expected, but multiple found.
    """
    pass

class unexpectedZeroMatchWarning(Warning):
    """
    Warned when one or more matches expected, and none are found.
    """
    pass

class badTextFormattingWarning(Warning):
    pass

class unmatchedCitationWarning(Warning):
    """
    Warned when a citation reference is made but not matched to an actual <ref> tag.
    """
    pass

class unmatchedTableWarning(Warning):
    """
    Warned when a table reference is made but not matched to an actual <table-wrap> tag.
    """
    pass

class unmatchedFigureWarning(Warning):
    """
    Warned when a figure reference is made but not matched to an actual <fig> tag.
    """
    pass
        
#-----------End Custom Warnings & Exceptions for Parsing------------

#--------------------GENERATE PAPER DICTIONARY GIVEN PMCID-------------------------------
def paper_dict_from_pmc(pmcid:int, email:str, download:bool = False, validate:bool = True, verbose:bool = False, suppress_warnings:bool = False, suppress_errors:bool = False)->dict:
    """
    Wrapper that scrapes a PMC article specified by PMCID from the web (through scrape module),
    then parses the XML retrieved into a dictionary of useful values. 

    Middleman between scrape.py and Paper.from_pmc.

    Paper objects in paper.py handle actual dictionary -> object conversion.
    """
    if verbose: 
        print(f"Generating Paper object for PMCID = {pmcid}...")
    #DOWNLOAD XML TREE AND GET ROOT
    paper_tree = scrape.get_xml(pmcid=pmcid, email=email, download=download, validate=validate, verbose=verbose)
    root = paper_tree.getroot()

    return generate_paper_dict(pmcid=pmcid, paper_root = root, verbose=verbose, suppress_warnings=suppress_warnings, suppress_errors=suppress_errors)

def generate_paper_dict(pmcid:int, paper_root:ET.Element, verbose:bool = False, suppress_warnings:bool = False, suppress_errors:bool = False)->dict:
    """
    Given the root of an XML tree, parse through it and generate a flattened dictionary
    of relevant PMC paper XML information.

    Expects the XML to be in NLM articleset 2.0 DTD format.

    Optionally suppress warnings and/or errors.
    If errors are suppressed, None will be returned upon failed parsing.
    """
    paper_dict = None

    if suppress_warnings:
        warnings.simplefilter("ignore")
    
    if suppress_errors:
        try:
            paper_dict = _actually_generate_paper_dict(pmcid, paper_root, verbose)
        except Exception as e:
            print(f"An exception occurred: {str(e)}")
    else:
        paper_dict = _actually_generate_paper_dict(pmcid, paper_root, verbose)

    if suppress_warnings:
        warnings.simplefilter("default")

    return paper_dict

def _actually_generate_paper_dict(pmcid:int, paper_root:ET.Element, verbose:bool = False)->dict:
    """
    Actual paper dict generation function. Called by wrapper generate_paper_dict().
    """
    root = paper_root
    #KEEP TRACK OF XREFS, TABLES, FIGURES IN BIMAP
    #(THIS WILL BE UPDATED DURING TEXT RETRIEVAL WHEN HTML REF TAGS ARE SPLIT OUT)
    ref_map = basicBiMap()

    #STORE EXTRACTED INFO IN PAPER DICT
    paper_dict = {
        'PMCID': pmcid,
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
        'Funding': gather_funding(root),
        'Footnote': gather_footnote(root),
        'Acknowledgements': gather_acknowledgements(root),
        'Notes': gather_notes(root),
        'Custom Meta': gather_custom_metadata(root),
        'Ref Map With Tags': copy.deepcopy(ref_map),
        'Ref Map': _clean_ref_map(paper_root = root, ref_map = ref_map),
    }

    citations, tables, figures = _split_citations_tables_figs(paper_dict['Ref Map'])
    paper_dict['Citations'] = citations
    paper_dict['Tables'] = tables
    paper_dict['Figures'] = figures

    if verbose:
        print(f"Finished generating Paper object for PMCID = {paper_dict['PMCID']}...")
        
    return paper_dict

def define_data_dict()->dict:
    """
    Returns a static definition of each of the elements returned in a Paper dict.
    """
    data_dict = {
        'PMCID': "PMCID of the PMC article. Unique.",
        'Title': "Title of the PMC article.",
        'Authors': "Dataframe of the PMC Authors, including first names, last names, email addresses, and affiliations if provided.",
        'Non-Author Contributors': "Dataframe of the non-author contributors, including first names, last names, email addresses, and affiliations if provided.",
        'Abstract': "List of TextSections parsed from the abstract portion of the XML. Use Paper.print_abstract() or Paper.abstract_as_str() for a simple view of the text.",
        'Body': "List of TextSections parsed from the body portion of the XML. Use Paper.print_body() or Paper.body_as_str() for a simple view of the text.",
        'Journal ID': "Dict of ID Type, ID pairs for the Journal in which the article was published. ie. NLM-TA and ISO-ABBREV IDs.",
        'Journal Title': "Name of the journal in text.",
        'ISSN': "Dict of ISSN type, ISSN number values for the article.",
        'Publisher Name': "Name of the publisher in text.",
        'Publisher Location': "Location of the publisher in text.",
        'Article ID': "Dict of ID Type, ID Value pairs. ie. p.article_id['pmc'] gives the PMCID for the article.",
        'Article Types': "List of 'header' article types for the article.",
        'Article Categories': "List of 'non-header' article types for the article.",
        'Published Date': "Dict of various publishing dates of the paper (ie: electronic pub, print pub).",
        'Volume': "The Volume # in which this paper was published in its journal(s).",
        'Issue': "The Issue # in which this paper was grouped within the volume of the journal(s) in which it is published.",
        'FPage': "First page on which this paper was published in its journal.",
        "LPage": "Last page on which this paper was published in its journal.",
        'Permissions': "Summary of copyright statement, license type, and full license text for the paper.",
        'Copyright Statement': "Returns the Copyright statement. Usually a short phrase identifying the individuals who have copyrighted this research, under a copyright license type found via paper.license.",
        'License': "Returns the License Type the research is licensed under (ie: Open Access).",
        'Funding': "Returns a list of groups which funded the research. Important for bias detection.",
        'Footnote': "Text of any footnote statement provided with the article.",
        'Acknowledgements': "List of acknowledgement statements provided with the article.",
        'Notes': "List of notes included with the article.",
        'Custom Meta': "Dict of custom metadata key, value pairs provided with the article.",
        'Ref Map': """Dict of Index, Reference value pairs. Use p.ref_map to decode data references 
        within TextSection.text_with_refs text. ie. When working with the full text with 
        references, you may come across something like [MHTML::dataref::0]. This means 
        that the reference under p.ref_map[0] was extracted from this location in the text.
        This can be useful for linking text with tables, figures, and xrefs for more 
        detailed analysis."""
        }
    
    return data_dict

def gather_title(root: ET.Element)->str:
    """
    Grab the title of a PMC paper from its XML root.
    """
    matches = root.xpath('//article-title/text()')
    if len(matches) > 1: 
        warnings.warn("Warning! Multiple titles matched. Setting Paper.title to the first match.", unexpectedMultipleMatchWarning)
    elif len(matches) == 0:
        warnings.warn("No article title found in the retrieved XML.", unexpectedZeroMatchWarning)
        return None
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
        if first_name is not None:
            first_name = first_name.strip()
        last_name = contributor.findtext(".//surname")
        if last_name is not None:
            last_name = last_name.strip()
        address = contributor.findtext(".//address/email")
        if address is not None:
            address = address.strip()
        affiliations = []
        aff_paths = contributor.xpath(".//xref[@ref-type='aff']")
        for aff in aff_paths:
            aff_id = aff.get('rid')
            aff_texts = root.xpath(f"//contrib-group/aff[@id='{aff_id}']/text()[not(parent::label)]")
            if len(aff_texts) > 1:
                warnings.warn("Multiple affiliations with the same ID found. Check XML Formatting.", unexpectedMultipleMatchWarning)
            if len(aff_texts)==0:
                aff_texts = ["Affiliation data not found."]

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
    if len(authors) == 0:
        warnings.warn("Warning! Authors could not be matched", unexpectedZeroMatchWarning)
        return None

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
    if len(non_author_contributors) > 0:
        non_author_tuples = _get_contributor_tuples(root=root, contributors=non_author_contributors)
        non_authors_df = pd.DataFrame(non_author_tuples)
        non_authors_df.columns = ['Contributor_Type', 'First_Name', 'Last_Name', 'Email_Address', 'Affiliations']
        return_val = non_authors_df

    return return_val

def gather_abstract(root: ET.Element, ref_map:basicBiMap)->List[Union[TextSection, TextParagraph]]:
    """
    Extract all abstract text sections from an xml, output as a list of TextSections and/ord TextParagraphs. 
    """
    abstract = []

    #get abstract subtree from XML
    matches = root.xpath('//abstract')
    if len(matches) > 1: 
        warnings.warn("Warning! Multiple abstracts matched. Filling in Paper.abstract with the first match.", unexpectedMultipleMatchWarning)
    elif len(matches) == 0:
        warnings.warn("No abstract found.", unexpectedZeroMatchWarning)
        return None
    abstract_root = matches[0]

    #iterate through abstract subtree and add in text sections (recursive) and text paragraphs (flat)
    for child in abstract_root.iterchildren():
        if child.tag == 'sec':
            abstract.append(TextSection(sec_root=child, ref_map=ref_map))
        elif child.tag == 'p':
            abstract.append(TextParagraph(p_root = child, ref_map = ref_map))
        else:
            warnings.warn(f"Warning! Unexpected child with of type {child.tag} found under an XML <abstract> tag.")

    return abstract

def gather_body(root: ET.Element, ref_map:basicBiMap)->List[Union[TextSection, TextParagraph]]:
    """
    Extract all body text sections from an xml, output as a list of TextSections. 
    """
    body = []

    #get abstract subtree from XML
    matches = root.xpath('//body')
    if len(matches) > 1: 
        warnings.warn("Warning! Multiple 'body's matched. Filling in Paper.body with the first match.", unexpectedMultipleMatchWarning)
    elif len(matches) == 0:
        warnings.warn("Warning! No <body> tag found. This paper may be abstract only, or the Open Access portion may be abstract only. This also may happen with author manuscripts and other non-final editions.")
        return None
    body_root = matches[0]

    #iterate through body subtree and add in text sections (recursive) and text paragraphs (flat)
    for child in body_root.iterchildren():
        if child.tag == 'sec':
            body.append(TextSection(sec_root=child, ref_map = ref_map))
        elif child.tag == 'p':
            body.append(TextParagraph(p_root=child, ref_map = ref_map))
        else:
            warnings.warn(f"Warning! Unexpected child with of type {child.tag} found under an XML <body> tag.")

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
    title_matches = root.xpath("//journal-title")
    for title in title_matches:
        titles.append(title.text)
    #might have multiple journals & journal titles
    if len(titles) > 1:
        return_val = titles
    elif len(titles) == 0:
        warnings.warn("No journal title found.", unexpectedZeroMatchWarning)
        return_val = None
    else:
        return_val = titles[0]
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
    elif len(matches) == 0:
        warnings.warn("No 'article-categories' list found.", unexpectedZeroMatchWarning)
        return None

    article_categories = matches[0]
    heading_categories = article_categories.xpath("subj-group[@subj-group-type='heading']/subject")
    heading_cats = [heading_cat.text for heading_cat in heading_categories]

    if not heading_cats:
        heading_cats = "No article type found (No article category with subject type 'heading'). Check Paper.article_categories for other categories."
    return heading_cats

def gather_article_categories(root: ET.Element) -> List[str]:
    """
    Gather Other Article Categories from PMC XML.
    """
    matches = root.xpath("//article-meta/article-categories")
    if len(matches) > 1: 
        warnings.warn("Warning! Multiple 'article-categories' lists matched. Filling in Paper.article_categories with the first match.", unexpectedMultipleMatchWarning)
    elif len(matches) == 0:
        warnings.warn("No 'article-categories' list found.", unexpectedZeroMatchWarning)
        return None
    article_categories = matches[0]
    other_categories = article_categories.xpath("subj-group[not(@subj-group-type='heading')]/subject")
    other_cats = [{other_cat.get("subj-group-type"): other_cat.text} for other_cat in other_categories]
    
    if not other_cats:
        other_cats = "No extra article categories found. Check paper.article_types for header categories."
    return other_cats

def gather_published_date(root: ET.Element) -> Dict[str, datetime]:
    """
    Gather Publishing Dates from PMC XML.

    Gathers electronic publishing, print publishing, etc. dates.
    """
    #TODO: update for multi-publishing (need to find an example first)

    pdate_dict = {}
    matches = root.xpath("//article-meta/pub-date")
    for match in matches:
        pub_type = match.get("pub-type")

        year = 1 #default
        year_matches = match.xpath("year/text()")
        if len(year_matches) > 0:
            year = int(year_matches[0])
        else:
            warnings.warn("No year found for one of the publishing dates. Defaulting to year = 1!", unexpectedZeroMatchWarning)
        
        #if not month found, assume the 1st (standard practice - )
        month = 1
        month_matches = match.xpath("month/text()")
        if len(month_matches) > 0:
            month = int(month_matches[0])

        #if no day found, assume the 1st (standard practice)
        day = 1
        day_matches = match.xpath("day/text()")
        if len(day_matches) > 0:
            day = int(day_matches[0])

        full_date = datetime(year=year, month=month, day=day)
        pdate_dict[pub_type] = full_date
    return pdate_dict

def gather_volume(root: ET.Element) -> str:
    """
    Gather Volume # of Parent Publication from PMC XML.
    """
    #TODO: update for multi-publishing (need to find an example first)

    matches = root.xpath("//article-meta/volume/text()")
    volume = None
    if len(matches) == 0:
        warnings.warn("No Volume # found for Publication.", unexpectedZeroMatchWarning)
    else:
        volume = matches[0]

    return volume

def gather_issue(root: ET.Element) -> str:
    """
    Gather Issue # of Parent Publication from PMC XML.
    """
    #TODO: update for multi-publishing (need to find an example first)

    matches = root.xpath("//article-meta/issue/text()")
    issue = None
    if len(matches) == 0:
        warnings.warn("No Issue # found for Publication.", unexpectedZeroMatchWarning)
    else:
        issue = matches[0]

    return issue

def gather_fpage(root: ET.Element) -> str:
    """
    Gather First Page Number of this article in its parent publication.
    """
    #TODO: update for multi-publishing (need to find an example first)

    matches = root.xpath("//article-meta/fpage/text()")
    fpage = None
    if len(matches) == 0:
        warnings.warn("No First Page # found for Publication.", unexpectedZeroMatchWarning)
    else:
        fpage = matches[0]

    return fpage

def gather_lpage(root: ET.Element) -> str:
    """
    Gather Last Page Number of this article in its parent publication.
    """
    #TODO: update for multi-publishing (need to find an example first)

    matches = root.xpath("//article-meta/lpage/text()")
    lpage = None
    if len(matches) == 0:
        warnings.warn("No Last Page # found for Publication.", unexpectedZeroMatchWarning)
    else:
        lpage = matches[0]

    return lpage  

def gather_permissions(root: ET.Element) -> Dict[str, str]:
    """
    Gather Permissions from PMC XML.

    Copyright statement, license type, and license paragraph.
    """
    copyright_statement_matches = root.xpath("//article-meta/permissions/copyright-statement/text()")
    copyright_statement = "No copyright statement found."
    if len(copyright_statement_matches) == 0:
        warnings.warn("No copyright statement found.", unexpectedZeroMatchWarning)
    elif len(copyright_statement_matches) > 1:
        warnings.warn("Multiple copyright statements found. Retrieving the first statement.", unexpectedMultipleMatchWarning)
    else:
        copyright_statement = copyright_statement_matches[0]

    license_matches = root.xpath("//article-meta/permissions/license")
    if len(license_matches) == 0:
        warnings.warn("No license found.", unexpectedZeroMatchWarning)
        return None
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


def gather_funding(root: ET.Element) -> List[str]:
    """
    Gather Funding Data from PMC XML.
    """
    matches = root.xpath("//article-meta/funding-group")
    funding_institutions = []
    for match in matches:
        institutions = match.xpath('award-group/funding-source/institution/text()')
        funding_institutions.extend([inst for inst in institutions])

    if len(funding_institutions) == 0:
        funding_institutions = None
    return funding_institutions


def gather_footnote(root: ET.Element) -> str:
    """
    Gather Footnote from PMC XML.
    """
    matches = root.xpath("//back/fn-group/fn")
    footnote = ""
    for fn in matches:
        for child in fn:
            if child.tag == "p":
                if len(footnote) == 0:
                    footnote += str(TextParagraph(p_root=child))
                else:
                    footnote += " - " + str(TextParagraph(p_root=child))
            else:
                warnings.warn(f"Unexpected child of type {child.tag} under a footnote (<fn>) tag. Ignoring.")

    if len(footnote) == 0:
        footnote = None

    return footnote

def gather_acknowledgements(root: ET.Element) -> Union[List[str], str]:
    """
    Gather Acknowledgements from PMC XML.
    """
    matches = root.xpath("//ack")
    acknowledgements = [' '.join(match.itertext()).strip() for match in matches]

    return acknowledgements

def gather_notes(root: ET.Element) -> str:
    """
    Gather Notes from PMC XML.
    """
    notes = []
    matches = root.xpath("//notes")
    notes = [stringify_note(note) for note in matches if not note.getparent().tag == 'notes']

    return notes

def stringify_note(root: ET.Element) -> str:
    """
    Recursively stringify notes using their <title>, <p>, and child <notes> content.
    """
    note = ""
    for child in root.iterchildren():
        if child.tag == 'title':
            note += f"Title: {child.text}\n"
        elif child.tag == 'p':
            note += child.text
        elif child.tag == 'notes':
            note += "\n" + textwrap.indent(stringify_note(child), " " * 4) 
    note += "\n"
    return note

#def _get_note(note_root: ET.Element) -> 

def gather_custom_metadata(root: ET.Element)->Dict[str, str]:
    """
    Gather any custom metadata key-value pairs from the PMC XML.
    """
    custom = {}
    matches = root.xpath("//custom-meta")
    for custom_meta in matches:
        meta_name = custom_meta.find("meta-name")
        if meta_name is not None:
            meta_name = meta_name.text
        meta_value = custom_meta.find("meta-value")
        meta_data = None
        if meta_value is not None:
            meta_data = " ".join(meta_value.itertext())
        if meta_data:
            if meta_name is None:
                meta_name = uuid.uuid4() #give random unique identifier if no meta key found
            custom[meta_name] = meta_data
    
    if len(custom) == 0:
        custom = None
    return custom

def _parse_citation(citation_root: ET.Element) -> Union[Dict[str, Union[List[str], str]], str]:
    root = citation_root

    # Find authors in common element-citation format
    author_matches = root.xpath('.//person-group[@person-group-type="author"]/name')

    # If failed, try to find full citation in mixed-citation format---------------
    mixed_citation = None
    if len(author_matches) == 0:
        mixed_citation = root.xpath('//mixed-citation/text()')
        if len(mixed_citation) > 0:
            return str(mixed_citation[0])
    #------------------------------------------------------------------------

    # If still failed, raise a warning.
    if len(author_matches) == 0:
        warnings.warn(f"No authors found in citation {root.get('id')}", unexpectedZeroMatchWarning)

    #tries to retrieve all of the following info, fails silently if none found since many refs incomplete
    citation_dict = {
        'Authors': [f"{_try_get_xpath_text(name, 'given-names')} {_try_get_xpath_text(name, 'surname')}"
                    for name in author_matches if author_matches],
        'Title': _try_get_xpath_text(root, './/article-title'),
        'Source': _try_get_xpath_text(root, './/source'),
        'Year': _try_get_xpath_text(root, './/year'),
        'Volume': _try_get_xpath_text(root, './/volume'),
        'FirstPage': _try_get_xpath_text(root, './/fpage'),
        'LastPage': _try_get_xpath_text(root, './/lpage'),
        'DOI': _try_get_xpath_text(root, './/pub-id[@pub-id-type="doi"]'),
        'PMID': _try_get_xpath_text(root, './/pub-id[@pub-id-type="pmid"]'),
    }
        
    return citation_dict

def _try_get_xpath_text(root: ET.Element, xpath:str, verbose = False)-> str:
    """
    Given an lxml Element and an xpath, attempts to retrieve the first matched path's text.
    Failure warnings suppressed by default.

    Returns None on failure. 
    """
    return_text = None
    try:
        return_text = root.find(xpath).text
    except AttributeError:
        if verbose:
            warnings.warn(f"Failed xpath text retrieval while trying to find {xpath}.text(). Root ID: {root.get('id')}")

    return return_text


def _find_key_of_xpath(ref_map:basicBiMap, xpath_query:str)->int:
    """
    Searches through the ref_map and returns the first key where the xpath matches the value.
    """
    ref_map = copy.deepcopy(ref_map)
    # Iterate through the dictionary and find the key with matching value
    matching_key = None
    for key, value in ref_map.items():
        if len(ET.fromstring(value).xpath(xpath_query)) > 0:
            matching_key = key
            break

    return matching_key

def _clean_ref_map(paper_root: ET.Element, ref_map:basicBiMap)->basicBiMap:
    """
    Takes in a reference map and replaces each reference tag with:
        -bibr (bibliography) references replaced by actual bibliography citation
        -table-wrap tags replaced by actual tables
        -figure tags replaced by figure information
        -references to tables linked to actual table df in the ref_map
        -references to figs linked to actual figure info in the ref_map
    """
    cleaned_ref_map = {}

    for key, item in ref_map.items():
        root = ET.fromstring(item)

        #-------XREFS LINK TO ACTUAL ITEMS OR FILL WITH BIBR--------------
        #process xrefs to citations, tables, and figures
        if root.tag == "xref":
            if root.get("ref-type") == "bibr":
                ref_id = root.get("rid")
                if not ref_id:
                    warnings.warn(f"Citation without a reference id specified (Citation {root.text})!", unmatchedCitationWarning)
                    continue
                
                # XPath expression to find the <ref> element based on the reference ID
                matching_citation_expr = f"//ref[@id='{ref_id}']"
                matches = paper_root.xpath(matching_citation_expr)
                if len(matches) == 0:
                    warnings.warn(f"Citation without matching reference (Citation {root.text})!", unmatchedCitationWarning)
                    continue
                elif len(matches) > 1:
                    warnings.warn("Multiple references found for a single citation. Filling in with the first match.")
        
                reference_xml = matches[0]
                cleaned_reference = _parse_citation(reference_xml)
                cleaned_ref_map[key] = cleaned_reference

            elif root.get("ref-type") == "table":
                table_id = root.get("rid")
                if not table_id:
                    warnings.warn(f"Table ref without reference ID, no table will be matched!", unmatchedTableWarning)
                    continue
                
                table_xpath = f"//table-wrap[@id='{table_id}']"
                matches = paper_root.xpath(table_xpath)
                if len(matches) == 0:
                    warnings.warn(f"Table xref with rid={table_id} not matched in the XML!", unmatchedTableWarning)
                    continue
                elif len(matches) > 1:
                    warnings.warn("Multiple references found for a single table. Filling in with the first match.")
                table_root = matches[0]
                cleaned_ref_map[key] = TextTable(table_root = table_root)

            elif root.get("ref-type") == "fig":
                fig_id = root.get("rid")
                if not fig_id:
                    warnings.warn(f"Figure ref unmatched. Figure ref without matching figure (Figure {root.text})!", unmatchedFigureWarning)
                    continue
                
                fig_xpath = f"//fig[@id='{fig_id}']"
                matches = paper_root.xpath(fig_xpath)
                if len(matches)==0:
                    warnings.warn(f"Figure xref with rid={fig_id} not matched in the XML!", unmatchedFigureWarning)
                    continue
                elif len(matches) > 1:
                    warnings.warn("Multiple references found for a single figure. Filling in with the first match.")
                fig_root = matches[0]
                cleaned_ref_map[key] = TextFigure(fig_root = fig_root)

            elif root.get("ref-type"):
                warnings.warn(f"Unknown reference type: {root.get('ref_type')} found in ref_map.")
            else:
                warnings.warn(f"<xref> in ref_map with no ref-type specified. Ignoring. ({root.text})")

        #process tables that are directly in the ref map
        elif root.tag == "table-wrap":
            cleaned_ref_map[key] = TextTable(table_root = root)
        #process figures that are directly in the ref map
        elif root.tag == "fig":
            cleaned_ref_map[key] = TextFigure(fig_root = root)
        else:
            warnings.warn(f"Unexpected tag of type {root.tag} found in ref map. Leaving as is instead of cleaning.")
            cleaned_ref_map[key] = ET.tostring(root)
        
    #Final pass to set up links now that everything should be filled in 
    for key,item in cleaned_ref_map.items():
        if type(item) == int:
            link_index = item
            cleaned_ref_map[key] = cleaned_ref_map[link_index]

    return cleaned_ref_map

def _get_ref_type(value):
    """
    Determine the type of reference of a ref_map value. Either table, citation, or fig (figure). 
    Returns None if no known type is found.
    """
    ref_type = None
    if type(value) == dict:
        if 'Caption' in value:
            ref_type = 'fig'
        elif 'Authors' in value:
            ref_type = 'citation'
    elif type(value) == str:   #if string, probably a citation scraped via the mixed citation element parsing
        ref_type = 'citation'  
    elif isinstance(value, TextFigure):
        ref_type = 'fig'
    elif isinstance(value, TextTable):
        ref_type = 'table'

    return ref_type

def _get_unique_tables(table_list:List[pd.DataFrame]) -> List[dict]:
    """
    TODO: Given a set of tables (pd.DataFrame or Stylers), return a unique set.
    """
    return table_list

def _get_unique_citations(citation_list:List[dict]) -> List[dict]:
    """
    TODO: Given a set of citations, return a unique set based on citation['PMID']
    """
    return citation_list

def _get_unique_figures(fig_list:List[dict]) -> List[dict]:
    """
    TODO: Given a set of figures, return a unique set of figures based on fig['Label']
    """
    return fig_list

def _split_citations_tables_figs(ref_map:basicBiMap) -> Tuple[Set[Union[Dict[str, Union[List[str], str]], str]], Set[pd.DataFrame], Set[Dict[str, str]]]:
    """
    Split ref map into a citation set, table set, and figure set.
    """
    citations = []
    tables = []
    figures = []
    for i,ref in ref_map.items():
        if _get_ref_type(ref) == 'citation':
            citations.append(ref)
        elif _get_ref_type(ref) == 'table':
            tables.append(ref.df)
        elif _get_ref_type(ref) == 'fig':
            figures.append(ref.fig_dict)
        else:
            warnings.warn(f"Issue finding Reference type for index {i} in reference map.")

    return _get_unique_citations(citations), _get_unique_tables(tables), _get_unique_figures(figures)
#--------------------END GENERATE PAPER DICTIONARY GIVEN PMCID---------------------------
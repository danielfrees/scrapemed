
"""
Parse module for grabbing metadata, text, tables, figures, etc. 
from XML trees representing PMC articles.

Middleman between the "scrape" module and the "paper" module for scrapemed.

"""

from typing import Text, List
import scrapemed.scrape as scrape
import lxml.etree as ET
from scrapemed.utils import basicBiMap
from scrapemed._text import TextParagraph
from scrapemed._text import TextSection

#-----------Custom Warnings & Exceptions for Parsing------------
class unexpectedMultipleMatchWarning(Warning):
    """
    Raised when one match expected, but multiple found.
    """
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return repr(self.message)

class unexpectedZeroMatchWarning(Warning):
    """
    Raised when one or more matches expected, and none found.
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
    #STORE EXTRACTED INFO IN PAPER DICT
    paper_dict = {'Title': None,
        'Authors': None,
        'Article Type': None,
        'Journal ID': None,
        'Abstract': None,
        'Body': None,
        'Acknowledgements': None,
        'XRef_Map': None,
        'Fig_Map': None,  
        'Table_Map': None
    #...
    }

    #DOWNLOAD XML TREE AND GET ROOT
    paper_tree = scrape.get_xml(pmcid=pmcid, email=email, download=download, validate=validate, verbose=verbose)
    root = paper_tree.getroot()

    #KEEP TRACK OF XREFS, TABLES, FIGURES IN BIMAP
    #(THIS WILL BE MODIFIED DURING TEXT RETRIEVAL WHEN HTML REF TAGS ARE SPLIT OUT)
    ref_map = basicBiMap()

    paper_dict['Title'] = gather_title(root)
    paper_dict['Authors'] = gather_authors(root)
    #update abstract text and maps
    paper_dict['Abstract'] = gather_abstract_sections(root, ref_map)
    #update article body text and maps
    paper_dict['Body'] = gather_body_sections(root, ref_map)

    #append final data reference map
    paper_dict['Ref_Map'] = ref_map

    return paper_dict

def gather_title(root: ET.Element)->str:
    """
    Grab the title of a PMC paper from its XML root.
    """
    matches = root.xpath('//article-meta/title-group/article-title/text()')
    if len(matches) > 1: 
        raise unexpectedMultipleMatchWarning("Warning! Multiple titles matched. Setting Paper.title to the first match.")
    title = matches[0]

    return title

def gather_authors(root: ET.Element)->list[str]:
    authors = root.xpath(".//contrib[@contrib-type='author']")
    if not authors:
        raise unexpectedZeroMatchWarning("Warning! Authors could not be matched")

    # Extract the first and last names of the authors and store them in a list
    author_names = []
    for author in authors:
        first_name = author.findtext(".//given-names")
        last_name = author.findtext(".//surname")
        author_names.append(f"{first_name} {last_name}")

    return author_names

def gather_abstract_sections(root: ET.Element, ref_map:basicBiMap)->List[TextSection]:
    """
    Extract all abstract text sections from an xml, output as a list of TextSections. 
    """
    abstract = []

    #get abstract subtree from XML
    matches = root.xpath('//abstract')
    if len(matches) > 1: 
        raise unexpectedMultipleMatchWarning("Warning! Multiple abstracts matched. Filling in Paper.abstract with the first match.")
    abstract_root = matches[0]

    #iterate through abstract subtree and get dict of title, bodytext pairs
    for sec in abstract_root.iterchildren('sec'):
        abstract.append(TextSection(sec_root=sec, ref_map=ref_map))

    return abstract

def gather_body_sections(root: ET.Element, ref_map:basicBiMap)->dict[str, str]:
    """
    Extract all body text sections from an xml, output as a list of TextSections. 
    """
    body = []

    #get abstract subtree from XML
    matches = root.xpath('//body')
    if len(matches) > 1: 
        raise unexpectedMultipleMatchWarning("Warning! Multiple 'body's matched. Filling in Paper.body with the first match.")
    body_root = matches[0]

    #iterate through abstract subtree and get dict of title, bodytext pairs
    for sec in body_root.iterchildren('sec'):
        body.append(TextSection(sec_root=sec, ref_map=ref_map))

    return body

def gather_acknowledgements():
    return
#--------------------END GENERATE PAPER DICTIONARY GIVEN PMCID---------------------------
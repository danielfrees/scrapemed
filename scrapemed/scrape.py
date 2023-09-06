"""
ScrapeMed's "scrape" module handles PubMed Central data searching and downloading.
This module also handles conversion of raw XML data to lxml.etree.ElementTree objects.
"""

import scrapemed._clean as _clean
import scrapemed._validate as _validate
import lxml.etree as ET
from Bio import Entrez 
import warnings
from typing import List

class validationWarning(Warning):
    """
    Warned when downloading PMC XML without validating.
    """
    pass

#---------------------Download Funcs for PubMed Central-------------------------------
def search_pmc(email:str, term:str, retmax:int = 10, verbose:bool = False)->dict:
    """Wrapper for Bio.Entrez's esearch function, 
    get a list of xmls and other info, provided a PMC search term.
    
    [email] - use your email to auth with PMC
    [term] - search term
    [retmax] - max number of PMCIDs to return    
    """
    
    DB = 'pmc'
    Entrez.email = email
    handle = Entrez.esearch(db=DB, retmax=retmax, term=term, idtype='pmc')
    record = Entrez.read(handle)
    handle.close()

    if verbose:
        print(f"\nSearching {DB}...\n")
        print(f"Number of results found: {record['Count']}")

    return record

def get_xmls(pmcids: List[int], email: str, download = False, validate = True, strip_text_styling = True, verbose = False) -> List[ET.ElementTree]:
    """
    Retrieve XMLs of research papers from PMC, given a list of PMCIDs.
    Also validates and cleans the XMLs by default.

    Input:
    [pmcid] = pmcid of article to retrieve.
    [email] = use your email to auth with PMC
    [validate] - whether or not to validate the XML retrieved (HIGHLY RECOMMENDED)
    [strip_text_styling] - whether or not to clean common HTML text styling from the text (HIGHLY RECOMMENDED)

    Output: List of ElementTrees of the XMLs corresponding to the provided PMCIDs. 
    """
    return [get_xml(pmcid, email, download, validate, strip_text_styling, verbose) for pmcid in pmcids]

def get_xml(pmcid: int, email: str, download = False, validate = True, strip_text_styling = True, verbose = False) -> ET.ElementTree:
    """
    Retrieve XML of a research paper from PMC, given a PMCID.
    Also validates and cleans the XML by default.

    Input:
    [pmcid] = pmcid of article to retrieve.
    [email] = use your email to auth with PMC
    [validate] - whether or not to validate the XML retrieved (HIGHLY RECOMMENDED)
    [strip_text_styling] - whether or not to clean common HTML text styling from the text (HIGHLY RECOMMENDED)

    Output: ElementTree of the validated xml record. 
    """
    xml_text = _get_xml_string(pmcid, email, download, verbose)
    tree = xml_tree_from_string(xml_string=xml_text, strip_text_styling=strip_text_styling, verbose=verbose)

    if validate:
        #Validate tags, attrs, values are supported for parsing by the scrapemed package.
        _validate.validate_xml(tree)
    else:
        warnings.warn(f"Warning! Scraping XML for PMCID {pmcid} from PMC without validating.", validationWarning)

    return tree

def _get_xml_string(pmcid: int, email: str, download = False, verbose = False) -> str:
    """'
    Retrieve XML text of a research paper from PMC.

    Input:
    [pmcid] = pmcid of article to retrieve.
    [email] = email of user requesting data from PMC

    Output: XML Text of the record.

    WARNING: THIS FUNCTION DOES NOT VALIDATE THE XML.
    """
    DB = 'pmc'
    RETTYPE = 'full'
    RETMODE = 'xml'
    Entrez.email = email

    #Actually fetch from PMC
    handle = Entrez.efetch(db = DB, id = pmcid, rettype = RETTYPE, retmode = RETMODE)
    xml_record = handle.read()
    xml_text = xml_record.decode(encoding = "utf-8")
    handle.close()
    
    if verbose:
        print(f"\nGetting {RETMODE.upper()} string from {DB}...\n")
        print(f"XML Record First 100 bytes: {xml_record[0:100]}")
        print(f"XML Text First 100 Chars: {xml_text[0:100]}")

    if download:
        with open(f"data/entrez_download_PMCID={pmcid}.{RETMODE}", "w+") as f:
            f.write(xml_text)

    return xml_text
#---------------------End Download Funcs for PubMed Central-------------------------------


#--------------------Convert XML strings -> Trees---------------------
def xml_tree_from_string(xml_string:str, strip_text_styling, verbose=False)->ET.ElementTree:
    """
    Converts string representing xml to an lxml ElementTree. 
    By default, strips html text styling.

    Input:
    [xml_string]: string/bytestream representing XML
    [strip_text_styling]: boolean, whether to remove HTML text styling tags or not
    
    Output: lxml.etree.ElementTree of the passed string.
    """
    xml_string = _clean.clean_xml_string(xml_string, strip_text_styling)
    tree = ET.ElementTree(ET.fromstring(xml_string))
    return tree
#--------------------End Convert XML strings -> Trees---------------------







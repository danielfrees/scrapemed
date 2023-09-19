"""
ScrapeMed's Scrape Module
============================

ScrapeMed's `scrape` module handles PubMed Central data searching
and downloads.

This module also handles conversion of raw XML data to
lxml.etree.ElementTree objects.

..warnings::
    - :class:`validationWarning` - Warned when downloading PMC XML without
        validating.
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


# ---------------------Download Funcs for PubMed Central-----------------------
def search_pmc(email: str, term: str, retmax: int = 10, verbose: bool = False) -> dict:
    """
    Wrapper for Bio.Entrez's esearch function to retrieve PMC search results.

    :param str email: Use your email to authenticate with PMC.
    :param str term: The search term.
    :param int retmax: The maximum number of PMCIDs to return. Default is 10.
    :param bool verbose: Whether to display verbose output. Default is False.

    :return: A dictionary containing search results, including PMCIDs.
    :rtype: dict
    """

    DB = "pmc"
    Entrez.email = email
    handle = Entrez.esearch(db=DB, retmax=retmax, term=term, idtype="pmc")
    record = Entrez.read(handle)
    handle.close()

    if verbose:
        print(f"\nSearching {DB}...\n")
        print(f"Number of results found: {record['Count']}")

    return record


def get_xmls(
    pmcids: List[int],
    email: str,
    download=False,
    validate=True,
    strip_text_styling=True,
    verbose=False,
) -> List[ET.ElementTree]:
    """
    Retrieve XMLs of research papers from PMC, given a list of PMCIDs.
    Also validates and cleans the XMLs by default.

    :param List[int] pmcids: List of PMCIDs of articles to retrieve.
    :param str email: Use your email to authenticate with PMC.
    :param bool download: Whether or not to download the XMLs. Default is False.
    :param bool validate: Whether or not to validate the retrieved XMLs
        (HIGHLY RECOMMENDED). Default is True.
    :param bool strip_text_styling: Whether or not to clean common HTML text
        styling from the text (HIGHLY RECOMMENDED). Default is True.
    :param bool verbose: Whether to display verbose output. Default is False.

    :return: List of ElementTrees of the XMLs corresponding to
        the provided PMCIDs.
    :rtype: List[ET.ElementTree]
    """
    return [
        get_xml(pmcid, email, download, validate, strip_text_styling, verbose)
        for pmcid in pmcids
    ]


def get_xml(
    pmcid: int,
    email: str,
    download=False,
    validate=True,
    strip_text_styling=True,
    verbose=False,
) -> ET.ElementTree:
    """
    Retrieve XML of a research paper from PMC, given a PMCID.
    Also validates and cleans the XML by default.

    :param int pmcid: PMCID of the article to retrieve.
    :param str email: Use your email to authenticate with PMC.
    :param bool download: Whether or not to download the XML. Default is False.
    :param bool validate: Whether or not to validate the retrieved XML
        (HIGHLY RECOMMENDED). Default is True.
    :param bool strip_text_styling: Whether or not to clean common HTML
        text styling from the text (HIGHLY RECOMMENDED). Default is True.
    :param bool verbose: Whether to display verbose output. Default is False.

    :return: ElementTree of the validated XML record.
    :rtype: ET.ElementTree
    """
    xml_text = _get_xml_string(pmcid, email, download, verbose)
    tree = xml_tree_from_string(
        xml_string=xml_text, strip_text_styling=strip_text_styling, verbose=verbose
    )

    if validate:
        # Validate tags, attrs, values are supported for
        # parsing by the scrapemed package.
        _validate.validate_xml(tree)
    else:
        warnings.warn(
            (
                f"Warning! Scraping XML for PMCID {pmcid} from "
                "PMC without validating."
            ),
            validationWarning,
        )

    return tree


def _get_xml_string(pmcid: int, email: str, download=False, verbose=False) -> str:
    """
    Retrieve XML text of a research paper from PMC.

    :param int pmcid: PMCID of the article to retrieve.
    :param str email: Email of the user requesting data from PMC.
    :param bool download: Whether or not to download the XML. Default is False.
    :param bool verbose: Whether to display verbose output. Default is False.

    :return: XML Text of the record.
    :rtype: str

    WARNING: THIS FUNCTION DOES NOT VALIDATE THE XML.
    """
    DB = "pmc"
    RETTYPE = "full"
    RETMODE = "xml"
    Entrez.email = email

    # Actually fetch from PMC
    handle = Entrez.efetch(db=DB, id=pmcid, rettype=RETTYPE, retmode=RETMODE)
    xml_record = handle.read()
    xml_text = xml_record.decode(encoding="utf-8")
    handle.close()

    if verbose:
        print(f"\nGetting {RETMODE.upper()} string from {DB}...\n")
        print(f"XML Record First 100 bytes: {xml_record[0:100]}")
        print(f"XML Text First 100 Chars: {xml_text[0:100]}")

    if download:
        with open(f"data/entrez_download_PMCID={pmcid}.{RETMODE}", "w+") as f:
            f.write(xml_text)

    return xml_text


# ----------------End Download Funcs for PubMed Central---------------------


# --------------------Convert XML strings -> Trees---------------------
def xml_tree_from_string(
    xml_string: str, strip_text_styling, verbose=False
) -> ET.ElementTree:
    """
    Converts a string representing XML to an lxml ElementTree.

    :param str xml_string: A string or bytestream representing XML.
    :param bool strip_text_styling: Whether to remove HTML text styling tags or not.
    :param bool verbose: Whether to display verbose output. Default is False.

    :return: An lxml.etree.ElementTree of the passed string.
    :rtype: ET.ElementTree
    """
    xml_string = _clean.clean_xml_string(xml_string, strip_text_styling)
    tree = ET.ElementTree(ET.fromstring(xml_string))
    return tree


# --------------------End Convert XML strings -> Trees---------------------

import scrapemed._validate as _validate
import scrapemed._clean as _clean
import scrapemed.scrape as scrape
import scrapemed._morehtml as mhtml
import lxml.etree as ET
import pytest
import filecmp
import os
import re


def test_xml_validation():
    """
    Tests the XML Validation Function:

    (1) Validation function does not alter XML other than html unescaping of non-markup-significant encodings
    (2) Warnings and exceptions for unknown PMC XML/HTML are raised correctly
    (3) Capitalization doesn't matter when validating XML (Other than proper XML syntax & symmetry)

    TODO:
    (4) HTML Cleaning doesn't affect XML Validation

    """
    path_to_testdata = os.path.join(os.path.dirname(__file__), "testdata")

    #Check that lxml parsing & validation does not modify xml (other than prologs, comments/markup, and html unescaping)
    #NOTE: test was manually modified to have the same prolog,markup, and have html unescaped (auto performed by lxml)
    #I merely want to check that the xml contents are not manipulated by validator, lxml library

    XML_TEST = _get_xml_from_file(os.path.join(path_to_testdata, "test.xml"))
    #save a version of test.xml with html encodings unescaped
    _generate_nms_html_unescaped_file(os.path.join(path_to_testdata, "test.xml"))
    #run the validation function
    _validate.validate_xml(XML_TEST)
    #write to file again and the test xml should be unmodified by validation other than html unescaping
    XML_TEST.write(os.path.join(path_to_testdata, "should_be_unmodified_test.xml"), xml_declaration = True, encoding = "utf-8")
    assert filecmp.cmp(os.path.join(path_to_testdata, "test_html_unescaped.xml"), os.path.join(path_to_testdata, "should_be_unmodified_test.xml"), shallow=True) == True

    #check that capitalization breaks the DTD validations
    XML_WEIRD_CAPS = _get_xml_from_file(os.path.join(path_to_testdata, "weird_caps.xml"))
    assert not _validate.validate_xml(XML_WEIRD_CAPS)

    #check that accepted wildcard values don't matter when validating otherwise valid xml
    XML_WITH_WILDCARDS = _get_xml_from_file(os.path.join(path_to_testdata, "test_wildcarding_1.xml"))
    assert _validate.validate_xml(XML_WITH_WILDCARDS) == True

    #Check that cleaning html styling does not mess with validation of xml
    xml_test_text = ET.tostring(XML_TEST, encoding = "unicode")
    styling_removed_tree = scrape.xml_tree_from_string(xml_test_text, strip_text_styling=True)
    assert _validate.validate_xml(styling_removed_tree)

    #check that unrelated xml does not validate 
    XML_BOOKS = _get_xml_from_file((os.path.join(path_to_testdata, "book_doc.xml")))
    assert not _validate.validate_xml(XML_BOOKS)

    #check that validation works on sample entrez download PMCID = 7067710 (straight from source)
    XML_7067710 = scrape.get_xml(pmcid=7067710, email="danielfrees247@gmail.com")
    assert _validate.validate_xml(XML_7067710)

    return None  #output for a passing test in pytest
    

###-----------HELPER FUNCTIONS-------------------
def _get_xml_from_file(filename: str, encoding: str ='utf-8') -> ET.ElementTree:
    """
    Grab XML tree by parsing the provided filename.
    """
    xml = ET.parse(filename, parser=ET.XMLParser(encoding=encoding))
    return xml

def _generate_nms_html_unescaped_file(filename: str) -> None:
    """
    Unescapes html encodings of the provided file (other than markup-language 
    significant encodings), and places the result in a new file.

    In: 
    [filename]: file to be html unescaped.

    Out:
    None, unescaped file will be saved under filename_html_escaped.file_ext

    """
    #split filename and extension
    filename_only, file_extension = os.path.splitext(filename)

    #holds text for unescaping
    text = None

    #open file and get html unescaped str representation of file
    with open(filename, 'r') as f:
        #read file as text
        text = f.read()

        #REMOVE HTML ENCODINGS (ie: "&xA9;" -> "©") OTHER THAN MARKUP-SIGNIFICANT HTML ENCODINGS
        """
        MARKUP SIGNIFICANT HTML ENCODINGS:

        left_angle -----   "&lt;" | "&#60;"
        right_angle -----   "&gt;" | "&#62;"
        ampersand -----   "&amp;" | "&#38;"
        quote_mark -----   "&quot;" | "&#34;"
        """
        text = mhtml.unescape_except(text, la = "&lt;", la2 = "&#60;", 
            ra = "&gt;", ra2 = "&#62;", 
            amp = "&amp;", amp2 = "&#38;", 
            qm = "&quot;", qm2 = "&#34;")
        

    #save html unescaped version of file in filename_html_unescaped
    with open(f"{filename_only}_html_unescaped{file_extension}", 'w') as f:
        f.write(text)

    return
#-------------------END HELPER FUNCTIONS-----------------------------


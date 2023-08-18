"""
Validation module for determining whether XML conforms to a format
supported by the scrapemed package.
"""

import re
import lxml.etree as ET
import os
import json 
import pandas as pd
import warnings
import scrapemed.trees as trees
from io import StringIO

SUPPORTED_DTD_URLS = ['https://dtd.nlm.nih.gov/ncbi/pmc/articleset/nlm-articleset-2.0.dtd']
#Regex DTD URL Patterns
DTD_URL_PATTERN = re.compile(r'"(https?://\S+)"')
END_OF_URL_PATTERN = re.compile(r'[^/]+$')

class noDTDFoundError(Exception):
    """
    Raised when no DTD can be found in a downloaded XML, preventing validation.
    """
    pass

#---------------------------DATA VALIDATION---------------------------------------------------
def validate_xml(xml : ET.ElementTree) -> bool:
    """
    Input:
    [xml] = an xml ElementTree

    Output:
    True or False, depending whether the file was validated. 

    Current support is defined by the files in scrapemed/data/DTDs.
    """
    #Find DTD and confirm its supported
    match = DTD_URL_PATTERN.search(xml.docinfo.doctype)
    url = None
    if match:
        url = match.group(1)
        assert url in SUPPORTED_DTD_URLS
    else:
        raise noDTDFoundError(f"A DTD must be specified for validation. Set validate=false if you want to proceeed without validation.")
    
    match = END_OF_URL_PATTERN.search(url)
    dtd_filename = match.group(0)
    dtd_filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "DTDs", dtd_filename)
    
    dtd_doc = None
    with open(dtd_filepath, 'r') as f:
        dtd_doc = f.read()
    
    dtd = ET.DTD(StringIO(dtd_doc))

    return dtd.validate(xml)
#---------------------------END DATA VALIDATION---------------------------------------------------

"""
Wrapper on basic functions for HTML manipulation.
Added: Non-markup significant unescape
"""

import re
import html

def unescape_except(s, **kwargs):
    """
    Convert all named and numeric character references (e.g. &gt;, &#62;,
    &x3e;) in the provided stringto the corresponding unicode characters, 
    excluding any provided encodings to be ignored.

    Input:
    [s] - string
    [**kwargs] - keyword arguments of form: key = encoding. 
                These encodings will be ignored when unescaping.

    Output: string with encodings unescaped other than those to be ignored

    For keys with multiple encodings, pass as 
    {keyname} = encoding1, {keyname}2 = encoding2.
    The keynames do not matter for functionality, but they must be unique.
    Encodings must be single code strings. 

    This function uses the rules defined by the HTML 5 standard
    for both valid and invalid character references, and the list of
    HTML 5 named character references defined in html.entities.html5.
    """

    #no need to do anything if there are no html encodings
    if "&" not in s:
        return s

    encoding_dict = {}

    #Translate keys to MHTML placeholder codes
    for key, encoding in kwargs.items():
        placehold_str = generate_mhtml_tag(key)
        encoding_dict[placehold_str] = encoding
    
    #Convert encodings to MHTML placeholder codes 
    for placehold_str, encoding in encoding_dict.items():
        code_to_save = re.compile(re.escape(encoding))
        s = code_to_save.sub(placehold_str, s)
   
    #Unescape everything else
    s = html.unescape(s)

    #Convert placeheld items back to their original html encodings
    for placehold_str, encoding in encoding_dict.items():
        placehold_r = re.compile(re.escape(placehold_str))
        s = placehold_r.sub(encoding, s)

    return s

def generate_mhtml_tag(string:str)->str:
    """
    Generates an MHTML tag from the provided string.

    Input:
    [string]: text to be tagged in MHTML format: "[MHTML::string]"

    Output: MTHML tag of string
    """
    return f"[MHTML::{string}]"

def generate_typed_mhtml_tag(tag_type:str, string:str)->str:
    """
    Generates a typed MHTML tag from the provided string.

    Input:
    [string]: text to be tagged in MHTML format: "[MHTML::type::string]"

    Output: MTHML tag of string
    """
    return f"[MHTML::{tag_type}::{string}]"

def remove_mhtml_tags(text:str)->str:
    """
    Removes all MHTML tags and typed MHTML tags found in the provided text. 
    """
    #match MHTML tags
        #group1 = tag type for typed MHTML tags
        #group2 = tag value for typed MHTML tags
        #group3 = tag for non-typed MHTML tags
    mhtml_pattern = r'\[MHTML::([^:\[\]]+)::([^:\[\]]+)\]|\[MHTML::([^:\[\]]+)\]'
    mhtml_r = re.compile(mhtml_pattern)
    #remove MHTML tags and return result
    return mhtml_r.sub('', text)
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

#-----------------WARNINGS & EXCEPTIONS------------------------------------
class markupLanguageAttributeException(Exception):
    """
    Raised when XML/HTML is downloaded which includes attributes not handled by the scrape module.
    """
class markupLanguageTagException(Exception):
    """
    Raised when XML/HTML is downloaded which includes tags not handled by the scrape module.
    """
class markupLanguageValueWarning(Warning):
    """
    Warned when a new value is encountered for a certain tag and attribute in the markup language.
    """
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return repr(self.message)

#-----------------END WARNINGS & EXCEPTIONS------------------------------------

#---------------------------DATA VALIDATION---------------------------------------------------
def validate_xml(xml : ET.ElementTree) -> bool:
    """
    Input:
    [xml] = an xml ElementTree

    Output:
    True or False, depending whether the file was perfectly validated. 
    Perfect validation occurs when all tags, attributes, and values are explicitly
    supported by scrapemed for parsing into Paper objects.

    May also hit an exception if a tag or attribute is unknown. 
    Unknown values will only raise warnings, and the return value will be false.

    Current support is defined by the files in scrapemed/data.
    """
    #track whether the xml is perfectly supported (all tags, attrs, vals known). Imperfect support without raised exceptions means some values are unknown.
    perfectly_valid = True
    #all tag-attr-val combos for the passed xml
    data_dict = trees._generate_data_dictionary(xml)

    #-----------------LOAD IN SUPPORTED DATA REFERENCES----------------------------------
    #load the supported xml, html tag dataframe
    supported_xml_html_filepath = os.path.join(os.path.dirname(__file__), "data", "supported_xml_html.json")
    supported_data_dict = None
    with open(supported_xml_html_filepath, 'r') as f:
        supported_data_dict = json.load(f)
    #load supported tag list
    supported_tags_filepath = os.path.join(os.path.dirname(__file__), "data", "supported_tag_list.txt")
    supported_tag_list = None
    with open(supported_tags_filepath, 'r') as f:
        supported_tag_list = [line.strip() for line in f.readlines()]
    #-----------------END LOAD IN SUPPORTED DATA REFERENCES----------------------------------

    #iterate through xml and ID if each combo is supported
    for tag in data_dict.keys():
        if not tag.lower() in supported_tag_list:
            raise markupLanguageTagException(f"Tag {tag} not in supported tag list.")
        for attr in data_dict[tag].keys():
            #there should be no properly formatted xml where an attribute is without 
            # a value list (even if the only value is '', the empty value)
            if not data_dict[tag][attr] or data_dict[tag][attr] == []:
                raise markupLanguageAttributeException(f"Attribute {attr} with no value. Check XML formatting.")
            for val in data_dict[tag][attr]:
                #convert to lowercase to check against supported. All supported vals in lowercase for consistency.
                tag = tag.lower()
                attr = attr.lower()
                val = val.lower()

                #CHECK VALUE WILDCARDING
                #TODO: move to other TODO below
                if _is_valid_sequence_attribute(tag, attr, val) or _is_supported_wildcard_html(tag, attr, val):
                    continue

                #CHECK SUPPORTED DATA DICT
                try:
                    if val in supported_data_dict[tag][attr]:
                        pass
                    #TODO: Add elif statements with the wildcarding checks to try to make the function more efficient
                    #Shouldnt be running the slower wildcarding scripts as the default check
                    else:
                        warnings.warn(f"Value {val} unknown to scrape module, for "
                                    f"tag {tag} and attribute {attr}. Proceed with caution."
                                    f" This XML may not be parsed perfectly into a Paper object.\n",
                                    markupLanguageValueWarning)
                        perfectly_valid = False
                #EITHER TAG OR ATTR IS NOT KNOWN
                except KeyError as e:
                    try: 
                        supported_data_dict[tag]
                        raise markupLanguageAttributeException(f"Attribute {attr} for tag {tag} unknown to scrapemed package.")
                    except KeyError as e2:
                        raise markupLanguageTagException(f"Tag {tag} unknown to scrapemed package.")

    return perfectly_valid 
#---------------------------END DATA VALIDATION---------------------------------------------------

def _is_valid_sequence_attribute(tag, attribute, value):
    """
    Returns true if the tag, attribute, value passed are any of the following allowed patterns.

    Allow {tag,attr} with any value of {value}:
    -------------------------------------------
    Allow xref,rid with any value aff{#}
    Allow xref,rid with any value cr{#}
    Allow xref,rid with any value tab{#}
    Allow xref,rid with any value fig{#}

    Allow sec,id with any value sec{#}

    Allow p,id with any value par{#}
    """
    if tag == 'xref':
        if attribute == 'rid':
            xref_rid_val_pattern =  re.compile(r'^(aff|cr|tab|fig)\d+$')
            return xref_rid_val_pattern.fullmatch(value)
    if tag == 'sec':
        if attribute == 'id':
            sec_id_val_pattern = re.compile(r'^sec\d+$')
            return sec_id_val_pattern.fullmatch(value)
    if tag == 'p':
        if attribute == 'id':
            p_id_val_pattern = re.compile(r'^par\d+$')
            return p_id_val_pattern.fullmatch(value)
    
    #not a supported wildcard sequence tag
    return False
    

#-------------------HTML wildcard validations----------------------------------
def _is_supported_wildcard_html(tag, attribute, value):
    if tag == 'table':
        return _is_valid_table_attribute(attribute, value)
    if tag == 'td':
        return _is_valid_td_attribute(attribute, value)
    if tag == 'table-wrap':
        return _is_valid_table_wrap_attribute(attribute, value)
    
    #not a supported wildcard HTML tag 
    return False

def _is_valid_table_attribute(attribute, value):
    """
    Check if an attribute and value are valid for an HTML 'table' tag.
    """
    valid_attributes = {
        'border': r'^\d+$',
        'cellpadding': r'^\d+$',
        'cellspacing': r'^\d+$',
        'width': r'^\d+(%|px)?$',
        'height': r'^\d+(%|px)?$',
        'align': r'^(left|center|right)$',
        'bgcolor': r'^#[0-9a-fA-F]{3,6}$',
        'summary': r'^[^\n\r]*$',
        'caption': r'^[^\n\r]*$',
        'frame': r'^(void|above|below|hsides|lhs|rhs|vsides|box)$',
        'rules': r'^(none|groups|rows|cols|all)$'
    }
    
    # Check if the attribute is valid for a table tag
    if attribute not in valid_attributes:
        return False
    
    # Check if the value matches the pattern for the attribute
    pattern = valid_attributes[attribute]
    if not re.fullmatch(pattern, value):
        return False
    
    return True

def _is_valid_td_attribute(attribute, value):
    # Define a dictionary of valid attributes and their corresponding regex patterns
    valid_attributes = {
        "abbr": r"^[a-zA-Z0-9]+$",
        "align": r"^(left|center|right|justify|char)$",
        "bgcolor": r"^#[a-fA-F0-9]{6}$",
        "colspan": r"^\d+$",
        "headers": r"^[a-zA-Z][a-zA-Z0-9\s_-]*$",
        "rowspan": r"^\d+$",
        "scope": r"^(row|col|rowgroup|colgroup)$",
        "char": r"^.$",
        "charoff": r"^\d+$"
    }
    
    # Check if the attribute is valid and its value matches the corresponding regex pattern
    if attribute in valid_attributes and re.fullmatch(valid_attributes[attribute], value):
        return True
    
    # If the attribute is not in the valid attributes dictionary or its value does not match the regex pattern, return False
    return False

def _is_valid_table_wrap_attribute(attribute, value):
    # Define a dictionary of valid attributes and their corresponding regex patterns
    valid_attributes = {
        "align": r"^(left|center|right)$",
        "frame": r"^(void|above|below|hsides|lhs|rhs|vsides|box|border)$",
        "rules": r"^(none|groups|rows|cols|all)$",
        "id": r"^id\d+$"
    }
    
    # Check if the attribute is valid and its value matches the corresponding regex pattern
    if attribute in valid_attributes and re.fullmatch(valid_attributes[attribute], value):
        return True
    
    # If the attribute is not in the valid attributes dictionary or its value does not match the regex pattern, return False
    return False
#-------------------End HTML wildcard validations----------------------------------


#-------------------Modification of Supported Markup Language Files----------------
def _update_supported_xml_html(data_dict) -> None:
    """
    Update the data files representing what data is supported by the scrapemed package.
    Passed data dictionary should be a complete set of the tags, attrs, vals supported.

    Input:
    [data_dict]: Dictionary representing the tags, attrs, vals in a XML data.
                Representation of data_dict format: 
                    {tag: 
                        {attr: 
                            [val1, val2], 
                        attr2: 
                            [val]
                        }
                    }
                
    Output: None. 

    Tags, attrs, and vals are always stored in lowercase so that 
    validation can be performed consistenly, regardless of case. 

    WARNING: Updates the functionality of the _validate_xml function. Use with caution!
    """
    update_bool = None
    counter = 0

    #FILENAMES FOR SUPPORTED XML AND HTML DATA-----------------------------------------
    csv_filepath = (os.path.join(os.path.dirname(__file__), "data", "supported_xml_html.csv"))
    json_filepath = (os.path.join(os.path.dirname(__file__), "data", "supported_xml_html.json"))
    tags_filepath = os.path.join(os.path.dirname(__file__), "data", "supported_tag_list.txt")
    #--------------------------------------------------------------------------------

    while update_bool not in ["y", "n"]:
        if counter > 2:
            print("Press ESC if you need to exit. Otherwise you need to type either y (yes) or n (no) in response to the prompt, and press enter.\n\n")
        update_bool = input(f"Are you sure you want to update the supported xml/html files? [y/n]\n"
            f"\nIf the data_dict provided does not correspond exactly to scrapemed's"
            f"supported tags, attributes, and values, this will break the validation"
            f"behavior of scrapemed.")
        counter +=1

    if update_bool == "y":
        #convert dictionary to lowercase
        data_dict = dict((k1.lower(),
                        dict((k2.lower(),
                            [s.lower() for s in v2]) for k2, v2 in v1.items()))
                    for k1, v1 in data_dict.items())

        #SAVE TO JSON
        with open(json_filepath, 'w+') as handle:
            json.dump(data_dict, handle)

        #SAVE TAG-ATTR-VALS TO CSV, SAVE TAG LIST TO TXT
        header_names = ["tag", "attr", "val"]
        multi_indexed_tuples = [] #keep track of tag-attr-val combos
        tag_list = [] 
        
        for tag in data_dict.keys():
            tag_list.append(tag.lower()) #make a list of all tags (LOWERCASE), 
                                        #regardless of whether they have attrs
            for attr in data_dict[tag].keys():
                #TODO: how to deal with attrs without value?
                for val in data_dict[tag][attr]:
                    multi_indexed_tuples.append(tuple([tag, attr, val])) #keep track of all tag-attr-val combos
        
        with open(tags_filepath, 'w+') as f:
            for tag in tag_list:
                f.write(f"{tag}\n")

        m_index = pd.MultiIndex.from_tuples(multi_indexed_tuples)
        supported_df = m_index.to_frame(name = header_names)
        supported_df["supported"] = 1
        supported_df = supported_df["supported"]
        supported_df.to_csv(csv_filepath, index_label = header_names)

    else:
        print("Not updating supported xml csv. Exiting.")

    return

def _strip_wildcard_tags(data_dict_df):
    """
    TODO

    Strips out wildcard tags supported already by the xml validation function. 
    ie: The validation function allows <xred rid="CR{int}"> where int is any integer for citation references.

    Purpose: Prevent massive supported_xml_html.csv where indeterminate value lists might occur. 
    """
#-------------------End Modification of Supported Markup Language Files----------------
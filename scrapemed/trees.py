"""
Scrapemed's "trees" module handles PMC article tree visualizations,
statistics, and descriptions.
"""

import copy
from graphviz import Digraph
import lxml.etree as ET

def investigate_xml_tree(root: ET.Element)->None:
    """
    Print some basic statistics and info about your xml, provided its root)

    Input: 
    [root] = Root of an ElementTree of your xml

    Output:
    None, all work is printed to stdout.
    """

    elem_list = [elem.tag for elem in root.iter()]
    num_elements = len(elem_list)
    all_element_types = set(elem_list)

    #PRINT UNIQUE ELEMENTS
    print(f"Num Elements: {num_elements}")
    print(f"Unique Element Types: {all_element_types}")
    print("--------------------------------------------\n")

    #PRINT OVERALL DATA DICTIONARY
    print(f"Tag Dictionary:\n {_generate_tag_dictionary(root)}\n")
    print("--------------------------------------------\n")
    return

def visualize_element_tree(root: ET.Element, title = 'data/element_tree.gv', test_mode=False)->None:
    """Visualize an XML element tree using Graphviz."""
    root = copy.copy(root)
    dot = Digraph()
    _add_elements(dot, root)
    if not test_mode:
        dot.render(title, view=True)
    return

def _add_elements(dot: Digraph, element: ET.Element, parent=None):
    """Recursively add elements to a Graphviz dot graph."""
    if parent is not None:
        dot.edge(parent, element.tag)
    dot.node(element.tag, element.tag)
    for child in element:
        _add_elements(dot, child, element.tag)
    return

def _generate_tag_dictionary(root: ET.Element) -> dict:
    """
    Generate a dictionary of all tags, each with a subdictionary of attributes, and lists of values seen for each attribute. 

    Helps define the scope of tags for a given xml/html tree. 

    Input: 
    [root] = root of an ElementTree of xml, html, other tagged language, or combo thereof

    Output:
    A dictionary of tags: attr-val dictionaries.
    Attr-val dictionaries are a dict of attribute: value lists.

    The structure of the overall dictionary is visualized below: 
       {
        tag_0
         |___attr_0
               |_____[value_0, ..., value_n]
         |___attr_1
               |_____[value_0, ...., value_n]
       
        ....
        tag_n
       }
    """
    data_dict = {}

    for element in root.iter():
        #ignore processing instructions
        if type(element) == ET._ProcessingInstruction: 
            continue
        attr_values_dict = {}     #dictionary of key-value pairs such that we have {attr: list of values the attribute can take on}
        try:
            #grab existing attr-val dict if we've seen this tag before
            attr_values_dict = data_dict[element.tag] #grab reference to the existing attr-val dict, intentionally not copied
            for attr, val in element.attrib.items():
                try:
                    #if weve seen the attribute before, add the value if its new
                    if not val in attr_values_dict[attr]:
                        attr_values_dict[attr].append(val)
                #we havent seen the attribute before at all
                except KeyError as e:
                    attr_values_dict[attr] = [val]
        except KeyError as e:
            #create new attr-val dict, we haven't seen this tag before
            data_dict[element.tag] = None
            #add attributes if they exist
            data_dict[element.tag] = copy.copy(element.attrib)
            #now put values into lists so they can be appended to later if needed
            attr_values_dict = data_dict[element.tag]
            for attr, val in attr_values_dict.items():
                attr_values_dict[attr] = [attr_values_dict[attr]]
    
    return data_dict
#---------------------------END DESCRIBE / CONVERT DATA----------------------------------------
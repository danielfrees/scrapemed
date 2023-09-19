"""
ScrapeMed's Trees Module
============================

Scrapemed's `trees` module handles PMC article tree visualizations,
statistics, and descriptions.
"""

import copy
from graphviz import Digraph
import lxml.etree as ET


def investigate_xml_tree(root: ET.Element) -> None:
    """
    Print basic statistics and information about an XML tree provided its root.

    :param ET.Element root: The root of an ElementTree of your XML.

    This function prints the following information to stdout:
    - Number of elements in the XML tree.
    - Unique element types in the XML tree.
    - A dictionary with tag frequencies in the XML tree.
    """

    elem_list = [elem.tag for elem in root.iter()]
    num_elements = len(elem_list)
    all_element_types = set(elem_list)

    # PRINT UNIQUE ELEMENTS
    print(f"Num Elements: {num_elements}")
    print(f"Unique Element Types: {all_element_types}")
    print("--------------------------------------------\n")

    # PRINT OVERALL DATA DICTIONARY
    print(f"Tag Dictionary:\n {_generate_tag_dictionary(root)}\n")
    print("--------------------------------------------\n")
    return


def visualize_element_tree(
    root: ET.Element, title="data/element_tree.gv", test_mode=False
) -> None:
    """
    Visualize an XML element tree using Graphviz.

    :param ET.Element root: The root of the XML element tree to visualize.
    :param str title: The title or filename for the output visualization.
        Default is "data/element_tree.gv".
    :param bool test_mode: Whether to render the visualization in test mode or not.

    This function creates a visualization of the XML element tree using Graphviz
    and optionally renders it.
    """
    root = copy.copy(root)
    dot = Digraph()
    _add_elements(dot, root)
    if not test_mode:
        dot.render(title, view=True)
    return


def _add_elements(dot: Digraph, element: ET.Element, parent=None):
    """
    Recursively add elements to a Graphviz dot graph.

    :param Digraph dot: The Graphviz dot graph.
    :param ET.Element element: The XML element to add to the graph.
    :param str parent: The parent element's tag. Default is None.

    This function is used internally to recursively add XML elements and their
    relationships to the Graphviz dot graph.
    """
    if parent is not None:
        dot.edge(parent, element.tag)
    dot.node(element.tag, element.tag)
    for child in element:
        _add_elements(dot, child, element.tag)
    return


def _generate_tag_dictionary(root: ET.Element) -> dict:
    """
    Generate a dictionary of all tags, each with a subdictionary of attributes,
    and lists of values seen for each attribute.

    This function helps define the scope of tags for a given XML, HTML, or
    other tagged language tree.

    :param ET.Element root: The root of an ElementTree of XML, HTML, or other
    tagged language.

    :return: A dictionary of tags, each with a subdictionary of attributes and
    lists of values for each attribute.
    :rtype: dict

    The structure of the overall dictionary is as follows:
    {
        tag_0:
        {
            attr_0: [value_0, ..., value_n],
            attr_1: [value_0, ..., value_n],
            ...
        },
        tag_1:
        {
            attr_0: [value_0, ..., value_n],
            attr_1: [value_0, ..., value_n],
            ...
        },
        ...
    }
    """
    data_dict = {}

    for element in root.iter():
        # ignore processing instructions
        if isinstance(element, ET._ProcessingInstruction):
            continue

        # dictionary of key-value pairs such that we have
        # {attr: list of values the attribute can take on}
        attr_values_dict = {}

        try:
            # grab existing attr-val dict if we've seen this tag before
            # grab reference to the existing attr-val dict,
            # intentionally not copied
            attr_values_dict = data_dict[element.tag]

            for attr, val in element.attrib.items():
                try:
                    # if weve seen the attribute before,
                    # add the value if its new
                    if val not in attr_values_dict[attr]:
                        attr_values_dict[attr].append(val)
                # we havent seen the attribute before at all
                except KeyError:
                    attr_values_dict[attr] = [val]
        except KeyError:
            # create new attr-val dict, we haven't seen this tag before
            data_dict[element.tag] = None
            # add attributes if they exist
            data_dict[element.tag] = copy.copy(element.attrib)
            # now put values into lists so they can be
            # appended to later if needed
            attr_values_dict = data_dict[element.tag]
            for attr, val in attr_values_dict.items():
                attr_values_dict[attr] = [attr_values_dict[attr]]

    return data_dict


# ----------------END DESCRIBE / CONVERT DATA-------------------

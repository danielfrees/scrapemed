"""
ScrapeMed's ``_text`` Module
==============================

The ``_text`` module of ScrapeMed is designed for organizing text found in
markup languages.

In the context of the ScrapeMed package, this module is used to facilitate the
organization of text found within paragraph (``<p>``) and section (``<sec>``)
tags in downloaded XML from PubMedCentral (PMC).

.. warnings::

   - :class:`multipleTitleWarning`: Warned when one title is expected but
        multiple are found.
   - :class:`unhandledTextTagWarning`: Warned when a tag is encountered in a
        text section of the XML but is not explicitly handled by ScrapeMed.
        The tag contents will be ignored if not handled manually. Feel free
        to submit a PR if you add a non-breaking code addition to handle these
        types of tags.
   - :class:`readHTMLFailure`: Warned when the pandas `read_html` function
        fails (rare). This may happen with tables void of readable data,
        such as tables that contain only graphics.
"""


import lxml.etree as ET
import textwrap
import scrapemed._clean as _clean
from scrapemed.utils import basicBiMap
import scrapemed._morehtml as mhtml
from itertools import chain
import warnings
import pandas as pd


# -------------------------------Warnings----------------------------
class multipleTitleWarning(Warning):
    """
    Warned when one title expected, but multiple found.
    """

    pass


class unhandledTextTagWarning(Warning):
    """
    Warned when a tag is encountered in a text section of the XML,
    but is not explicitly handled by ScrapeMed.

    The tag contents will be ignored if not handled manually.

    Feel free to submit a PR if you add a non-breaking code addition to handle
    these types of tags.
    """

    pass


class readHTMLFailure(Warning):
    """
    Warned when pandas read_html function fails (rare). May happen with
    tables void of readable data (ie. tables that contain only graphics).
    """

    pass


# ----------------------TextElement---------------------------------
class TextElement:
    """
    Base class for elements parsed from XML/HTML markup language.

    This class is initialized with a root element of the XML text element,
    as well as a reference map to populate with references found in the text,
    (and used to generate the replacement MHTML tags).

    :param ET.Element root: The root element of the XML text element.
    :param TextElement parent: The parent TextElement if applicable.
    :param basicBiMap ref_map: The reference map for storing references
        found in the text.

    Attributes:
        - root (ET.Element): The root element of the XML text element.
        - parent (TextElement, optional): The parent TextElement if applicable.
        - ref_map (basicBiMap): The reference map for storing references
            found in the text.

    Methods:
        - get_ref_map(): Return the shared BiMap for reference data.
        - set_ref_map(ref_map: basicBiMap): Set the shared BiMap for reference data.

    This class serves as the base class for more complex text classes.
    """

    def __init__(
        self,
        root: ET.Element,
        parent: "TextElement" = None,
        ref_map: basicBiMap = basicBiMap(),
    ):
        """
        Initialize a TextElement object.

        :param ET.Element root: The root element of the XML text element.
        :param TextElement parent: The parent TextElement if applicable.
        :param basicBiMap ref_map: The reference map for storing references
            found in the text
        """
        self.root = root
        self.parent = parent
        self.ref_map = ref_map

    # ------------------Getters and Setters for shared BiMap-------------------
    def get_ref_map(self) -> basicBiMap:
        """
        Return the shared BiMap for reference data.

        :returns: The shared BiMap containing reference data.
        :rtype: basicBiMap
        """
        ref_map = None
        if self.parent:
            ref_map = self.parent.get_ref_map()
        else:
            ref_map = self.ref_map
        return ref_map

    def set_ref_map(self, ref_map: basicBiMap):
        """
        Set the shared BiMap for reference data.

        :param basicBiMap ref_map: The BiMap containing reference data to be set.
        """
        if self.parent:
            self.parent.set_ref_map(ref_map)
        else:
            self.ref_map = ref_map
        return None

    # --------------End Getters and Setters for shared BiMap-----------------


# -------------------end TextElement-----------------------------------------


# ---------------------------TextParagraph----------------------------
class TextParagraph(TextElement):
    """
    Class representation of the data found in an XML <p> tag.

    :param ET.Element p_root: The root element of the XML <p> tag.
    :param TextElement parent: The parent TextElement if applicable.
    :param basicBiMap ref_map: The reference map for storing references
        found in the text.

    Attributes:
        - id (str): The identifier for the <p> tag.
        - text_with_refs (str): The text content of the <p> tag with references.
        - text (str): The clean text content of the <p> tag without references.

    Methods:
        - __str__(): Return the clean text content as a string.
        - __eq__(other): Check if two TextParagraph objects are equal based
            on their text content.
    """

    def __init__(
        self, p_root: ET.Element, parent=None, ref_map: basicBiMap = basicBiMap()
    ):
        """
        Initialize a TextParagraph object.

        :param ET.Element p_root: The root element of the XML <p> tag.
        :param TextElement parent: The parent TextElement if applicable.
        :param basicBiMap ref_map: The reference map for storing references
            found in the text.
        """
        super().__init__(
            root=p_root, parent=parent, ref_map=ref_map
        )  # initialize TextElement

        self.id = p_root.get("id")
        p_subtree = stringify_children(self.root)

        # split text and HTML tag references
        self.text_with_refs = _clean.split_text_and_refs(
            tree_text=p_subtree,
            ref_map=self.get_ref_map(),
            id=self.id,
            on_unknown="keep",
        )
        self.text = mhtml.remove_mhtml_tags(
            self.text_with_refs
        )  # clean text for str() and printing

    def __str__(self):
        """
        Return the clean text content of the TextParagraph object as a string.

        :returns: The clean text content.
        :rtype: str
        """
        return self.text

    def __eq__(self, other):
        """
        Check if two TextParagraph objects are equal based on their text
        content (including refs).

        :param TextParagraph other: The other TextParagraph object to compare with.

        :returns: True if the text content is equal, False otherwise.
        :rtype: bool
        """
        return self.text_with_refs == other.text_with_refs


# ------------------------end TextParagraph----------------------


# ----------------------------------TextSection------------------------------
class TextSection(TextElement):
    """
    Class representation of the data found in an XML <sec> tag.

    :param ET.Element sec_root: The root element of the XML <sec> tag.
    :param TextElement parent: The parent TextElement if applicable.
    :param basicBiMap ref_map: The reference map for storing references found
        in the text.

    Attributes:
        - title (str): The title of the section if available.
        - children (list): A list of TextSection, TextParagraph, TextTable, or
            TextFigure objects representing subsections, paragraphs, tables,
            or figures within the section.
        - text (str): The clean text content of the section without references.
        - text_with_refs (str): The text content of the section with references.

    Methods:
        - __str__(): Return a string representation of the section with proper
            indentation.
        - get_section_text(): Get a text representation of the entire section
            without references.
        - get_section_text_with_refs(): Get a text representation of the entire
            section with references.
        - __eq__(other): Check if two TextSection objects are equal based on
            their title and children.
    """

    def __init__(
        self, sec_root: ET.Element, parent=None, ref_map: basicBiMap = basicBiMap()
    ):
        """
        Initialize a text section from the root of a <sec> tree.

        Optionally provide reference BiMap storing links to reference data.
        Reference BiMap used to link text to table & figure data.

        Handles <title>, <p>, and <sec> children under the root <sec> tag.
        Anything else will be ignored and raise a warning.

        :param ET.Element sec_root: The root element of the XML <sec> tag.
        :param TextElement parent: The parent TextElement if applicable.
        :param basicBiMap ref_map: The reference map for storing references
            found in the text.
        """
        # initialize root, parent, and bimaps
        super().__init__(root=sec_root, parent=parent, ref_map=ref_map)

        self.title = None

        self.children = []  # section and paragraph children
        for child in sec_root.iterchildren():
            if child.tag == "title":
                if self.title:
                    warnings.warn(
                        multipleTitleWarning(
                            (
                                "Warning: Multiple Titles found for a single "
                                "TextSection. Check markup file formatting. "
                                "Using first title found."
                            )
                        )
                    )
                    continue
                self.title = child.text
            elif child.tag == "sec":
                self.children.append(
                    TextSection(child, parent=self, ref_map=self.get_ref_map())
                )
            elif child.tag == "p":
                self.children.append(
                    TextParagraph(child, parent=self, ref_map=self.get_ref_map())
                )
            elif child.tag == "table-wrap":
                self.children.append(
                    TextTable(child, parent=self, ref_map=self.get_ref_map())
                )
            elif child.tag == "fig":
                self.children.append(
                    TextFigure(child, parent=self, ref_map=self.get_ref_map())
                )
            else:
                warnings.warn(
                    (
                        f"Warning! Unexpected child with of type {child.tag} "
                        "found under an XML <sec> tag."
                    ),
                    unhandledTextTagWarning,
                )

        # after building the TextSection tree, get textual representations
        self.text = self.get_section_text()
        self.text_with_refs = self.get_section_text_with_refs()

    def __str__(self):
        """
        Return a string representation of the TextSection.

        The representation begins with the title if the section has one.
        Subsections will be indented, and body text will be printed without indentation.

        :returns: The string representation of the section.
        :rtype: str
        """
        s = ""
        if self.title is not None:
            s += f"SECTION: {self.title}:\n"
        for child in self.children:
            if isinstance(child, TextSection):
                s += "\n" + textwrap.indent(str(child), " " * 4)
                s += "\n"
            elif isinstance(child, TextParagraph):
                s += "\n" + str(child)
                s += "\n"
        return s

    def get_section_text(self):
        """
        Get a text representation of the entire text section, without references.

        :returns: The text content of the section.
        :rtype: str
        """
        return str(self)

    def get_section_text_with_refs(self):
        """
        Get a text representation of the entire text section, with references.

        :returns: The text content of the section with references.
        :rtype: str
        """
        s = ""
        if self.title is not None:
            s += f"SECTION: {self.title}:\n"
        for child in self.children:
            if isinstance(child, TextSection):
                s += "\n" + textwrap.indent(child.get_section_text_with_refs(), " " * 4)
                s += "\n"
            elif isinstance(child, TextParagraph):
                s += "\n" + child.text_with_refs
                s += "\n"
        return s

    def __eq__(self, other):
        """
        Check if two TextSection objects are equal based on their title and children.

        :param TextSection other: The other TextSection object to compare with.
        :returns: True if the titles and children are equal, False otherwise.
        :rtype: bool
        """

        # TODO: Test if this actually works for comparing TextSections.
        return self.title == other.title and self.children == other.children


# ----------------------end TextSection----------------------------------


# ---------------------------TextTable-------------------------------------
class TextTable(TextElement):
    """
    Initialize and process a table-wrap found in a text element of PMC XML.

    Uses pandas' `read_html` function (which relies on lxml and falls
    back to html5lib) to process the HTML tables into dataframes.

    Adds labels and captions if notated in the XML under
    //table-wrap/label and //table-wrap/caption/p tags.

    :param ET.Element table_root: The root element of the table-wrap found in PMC XML.
    :param TextElement parent: The parent TextElement if applicable.
    :param basicBiMap ref_map: The reference map for storing references found
        in the text.

    Attributes:
        - df (pandas.DataFrame): The dataframe representation of the table.
    """

    def __init__(
        self, table_root: ET.Element, parent=None, ref_map: basicBiMap = basicBiMap()
    ):
        """
        Initialize and process table-wrap found in a text element of PMC XML.

        Use pandas' read_html function (which relies on lxml and falls
        back to html5lib) to process the HTML tables into dataframes.

        Adds labels and captions if notated in the XML under
        //table-wrap/label and //table-wrap/caption/p tags.

        :param ET.Element table_root: The root element of the table-wrap found
            in PMC XML.
        :param TextElement parent: The parent TextElement if applicable.
        :param basicBiMap ref_map: The reference map for storing references
            found in the text.
        """
        # initialize root, parent, and bimaps
        super().__init__(root=table_root, parent=parent, ref_map=ref_map)

        # find label if any
        label_matches = table_root.xpath("label")
        label = None
        if len(label_matches) > 0:
            label = label_matches[0].text
        # find caption if any
        caption_matches = table_root.xpath("caption/p")
        caption = None
        if len(caption_matches) > 0:
            caption = caption_matches[0].text

        table_xml_str = ET.tostring(table_root)
        try:
            table_df = pd.read_html(table_xml_str)[0]
        except ValueError:
            warnings.warn(
                (
                    f"Table with label {label} and caption {caption} could not "
                    "be parsed with pd.read_html."
                ),
                readHTMLFailure,
            )
            self.df = None
            return None

        # build title for styled df, if relevant
        title = None
        if label and caption:
            title = f"{label}: {caption}"
        elif label:
            title = label
        elif caption:
            title = caption

        if title:
            table_df = table_df.style.set_caption(title)

        self.df = table_df

        return None

    def __str__(self):
        """
        Return a string representation of the table using member `.df`.

        :returns: The string representation of the table.
        :rtype: str
        """
        return str(self.df)

    def __repr__(self):
        """
        Return a string representation of the table using member `.df`.

        :returns: The string representation of the table.
        :rtype: str
        """
        return repr(self.df)


# ---------------------end TextTable-------------------------------------


# ---------------------------TextFigure-----------------------------------
class TextFigure(TextElement):
    """
    Initialize and parse a figure found in a text element of a PMC XML.

    Parses figures into a dictionary with their information
    (label, caption, and link).
    Unfortunately, the links are relative and cannot be reliably
    traced to a public URI.
    This means I have not found a way to download the actual
    figures to store via Pillow, etc.

    :param ET.Element fig_root: The root element of the figure found in PMC XML.
    :param TextElement parent: The parent TextElement if applicable.
    :param basicBiMap ref_map: The reference map for storing references found
        in the text.

    Attributes:
        - fig_dict (dict): A dictionary containing figure information with keys:
            - 'Label': The label of the figure.
            - 'Caption': The caption of the figure.
            - 'Link': The link (relative) to the figure.
    """

    def __init__(
        self, fig_root: ET.Element, parent=None, ref_map: basicBiMap = basicBiMap()
    ):
        """
        Initialize and parse a figure found in a text element of a PMC XML.

        Parses figures into a dictionary with their information
        (label, caption, and link).
        Unfortunately, the links are relative and cannot be reliably
        traced to a public URI.
        This means I have not found a way to download the actual
        figures to store via Pillow, etc.

        :param ET.Element fig_root: The root element of the figure found in
            PMC XML.
        :param TextElement parent: The parent TextElement if applicable.
        :param basicBiMap ref_map: The reference map for storing references
            found in the text.
        """

        # TODO: Find a way to grab actual figures. May be impossible with PMC
        # based on the research I've done so far.

        # initialize root, parent, and bimaps
        super().__init__(root=fig_root, parent=parent, ref_map=ref_map)

        root = fig_root
        label = root.find(".//label")
        if label is not None:
            label = label.text
        caption = root.find(".//caption")
        if caption is not None:
            caption = "".join(caption.itertext())
        graphic_href = root.find(".//graphic").get("{http://www.w3.org/1999/xlink}href")

        fig_dict = {"Label": label, "Caption": caption, "Link": graphic_href}

        self.fig_dict = fig_dict

        return None

    def __str__(self):
        """
        Return a string representation of the figure based on dict info in `.fig_dict`.

        :returns: The string representation of the figure.
        :rtype: str
        """
        return str(self.fig_dict)

    def __repr__(self):
        """
        Return a string representation of the figure  based on dict info in `.fig_dict`.

        :returns: The string representation of the figure.
        :rtype: str
        """
        return repr(self.fig_dict)


# --------------------------end TextFigure----------------------------------


# -------------------------------End Classes----------------------------


# ---------------------------------Helpers---------------------------------
def stringify_children(node, encoding="utf-8"):
    """
    Returns a string representation of a node and all its children
    (recursively), including markup language tags.

    Turns any byte strings in the subtree representation to regular strings,
    following the provided encoding.

    :param node: The XML node to stringify.
    :type node: ET.Element
    :param str encoding: The encoding to use for decoding byte strings
        (default is 'utf-8').

    :returns: A string representation of the node and its children,
        including markup language tags.
    :rtype: str
    """
    subtree = [
        chunk
        for chunk in chain(
            (node.text,),
            chain(
                *(
                    (ET.tostring(child, with_tail=False), child.tail)
                    for child in node.getchildren()
                )
            ),
            (node.tail,),
        )
        if chunk
    ]
    # decode any bytestrings
    for i in range(len(subtree)):
        if isinstance(subtree[i], bytes):
            subtree[i] = subtree[i].decode(encoding)
    return "".join(subtree).strip()

"""
ScrapeMed's "_text" module is aimed at organizing text found in markup language.

In the context of the ScrapeMed package, this supports the organization of text 
found within paragraph (<p>) and section (<sec>) tags in downloaded XML from 
PubMedCentral (PMC).
"""


import lxml.etree as ET
import textwrap
import scrapemed._clean as _clean
from scrapemed.utils import basicBiMap    
import scrapemed._morehtml as mhtml
from itertools import chain
import warnings
import re
import pandas as pd

#-------------------------------Warnings----------------------------
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

class readHTMLFailure(Warning):
    """
    Warned when pandas read_html function fails (rare). May happen with tables void of readable data (ie. tables that contain only graphics).
    """


#-----------------------------------------TextElement---------------------------------------------------
class TextElement():
    """
    Base class for elements parsed from XML/HTML markup language. 
    """        
    def __init__(self, root:ET.Element, parent:'TextElement'=None, ref_map:basicBiMap=basicBiMap()):
        self.root = root
        self.parent = parent
        self.ref_map = ref_map

    #---------------------Getters and Setters for shared BiMap-------------------------------------
    def get_ref_map(self)->basicBiMap:
        """
        Return the shared BiMap for reference data.
        """
        ref_map = None
        if self.parent:
            ref_map = self.parent.get_ref_map()
        else:
            ref_map = self.ref_map
        return ref_map
    
    def set_ref_map(self, ref_map:basicBiMap):
        """
        Set the shared BiMap for reference data.
        """
        if self.parent:
            self.parent.set_ref_map(ref_map)
        else:
            self.ref_map = ref_map
        return None
     #---------------------End Getters and Setters for shared BiMap-------------------------------------
#-------------------------end TextElement---------------------------------------------------

#---------------------------------------------TextParagraph---------------------------------------------------
class TextParagraph(TextElement):
    """
    Class representation of the data found in an XML <p> tag.
    """
    def __init__(self, p_root:ET.Element, parent=None, ref_map:basicBiMap=basicBiMap()):
        """
        
        """
        super().__init__(root=p_root,parent=parent,ref_map=ref_map) #initialize TextElement

        self.id = p_root.get('id')
        p_subtree = stringify_children(self.root)

        #split text and HTML tag references
        self.text_with_refs = _clean.split_text_and_refs(tree_text=p_subtree, 
                            ref_map=self.get_ref_map(), id=self.id, on_unknown='keep')
        self.text = mhtml.remove_mhtml_tags(self.text_with_refs) #clean text for str() and printing

    def __str__(self):
        return self.text
    
    def __eq__(self, other):
        return self.text_with_refs == other.text_with_refs
#------------------------------------------end TextParagraph---------------------------------------------------

#---------------------------------------------TextSection---------------------------------------------------
class TextSection(TextElement):
    """
    Class representation of the data found in an XML <sec> tag
    """
    def __init__(self, sec_root:ET.Element, parent=None, ref_map:basicBiMap=basicBiMap()):
        """
        Initialize a text section from the root of a <sec> tree. 

        Optionally provide reference BiMap storing links to reference data.
        Reference BiMap used to link text to table & figure data.

        Handles <title>, <p>, and <sec> children under the root <sec> tag. Anything else will be ignored and raise a warning.
        """
        #initialize root, parent, and bimaps
        super().__init__(root=sec_root,parent=parent,ref_map=ref_map)

        self.title = None

        self.children = []  #section and paragraph children
        for child in sec_root.iterchildren():
            if child.tag == 'title':
                if self.title:
                    warnings.warn(multipleTitleWarning("Warning: Multiple Titles found for a single TextSection. Check markup file formatting. Using first title found."))
                    continue
                self.title = child.text
            elif child.tag == 'sec':
                self.children.append(TextSection(child, parent=self, ref_map=self.get_ref_map()))
            elif child.tag == 'p':
                self.children.append(TextParagraph(child, parent=self, ref_map=self.get_ref_map()))
            elif child.tag == 'table-wrap':
                self.children.append(TextTable(child, parent=self, ref_map=self.get_ref_map()))
            elif child.tag == 'fig':
                self.children.append(TextFigure(child, parent=self, ref_map=self.get_ref_map()))
            else:
                warnings.warn(f"Warning! Unexpected child with of type {child.tag} found under an XML <sec> tag.", unhandledTextTagWarning)
        
        #after building the TextSection tree, get textual representations
        self.text = self.get_section_text()
        self.text_with_refs = self.get_section_text_with_refs()

    def __str__(self):
        """
        String representation of a TextSection. 

        Begins with title if the section has a title.

        Subsections will be indented. 

        Body text will be printed without indent.
        
        """
        s = ""
        if not self.title == None:
            s += f"SECTION: {self.title}:\n"
        for child in self.children:
            if type(child) == TextSection:
                s += "\n" + textwrap.indent(str(child), " " * 4) 
                s += "\n"
            elif type(child) == TextParagraph:
                s += "\n" + str(child)
                s += "\n"
        return s

    def get_section_text(self):
        """
        Gets a text representation of the entire text section, 
        using paragraphs with refs removed.
        """
        return str(self)
    
    def get_section_text_with_refs(self):
        """
        Gets a text representation of the entire text section, 
        using paragraphs with references retained.
        """
        s = ""
        if not self.title == None:
            s += f"SECTION: {self.title}:\n"
        for child in self.children:
            if type(child) == TextSection:
                s += "\n" + textwrap.indent(child.get_section_text_with_refs(), " " * 4) 
                s += "\n"
            elif type(child) == TextParagraph:
                s += "\n" + child.text_with_refs
                s += "\n"
        return s

    def __eq__(self, other):
        """
        TODO: Test if this actually works for comparing TextSections
        """
        return self.title==other.title and self.children==other.children
#-----------------------------------------end TextSection---------------------------------------------------

#-----------------------------TextTable----------------------------------------
class TextTable(TextElement):
    def __init__(self, table_root:ET.Element, parent=None, ref_map:basicBiMap=basicBiMap()):
        """
        Initialize and process table-wrap found in a text element of PMC XML.

        Use panda's read_html function (which relies on lxml and falls back to html5lib)
        to process the HTML tables into dataframes.

        Adds labels and captions if notated in the xml under //table-wrap/label and //table-wrap/caption/p tags.
        """
        #initialize root, parent, and bimaps
        super().__init__(root=table_root,parent=parent,ref_map=ref_map)
    
        #find label if any
        label_matches = table_root.xpath("label")
        label = None
        if len(label_matches) > 0:
            label = label_matches[0].text
        #find caption if any
        caption_matches = table_root.xpath("caption/p")
        caption = None
        if len(caption_matches) > 0:
            caption = caption_matches[0].text

        table_xml_str = ET.tostring(table_root)
        try:
            table_df = pd.read_html(table_xml_str)[0]
        except ValueError as e:
            warnings.warn(f"Table with label {label} and caption {caption} could not be parsed with pd.read_html.", readHTMLFailure)
            self.df = None
            return None

        #build title for styled df, if relevant
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
        return str(self.df)

    def __repr__(self):
        return repr(self.df)
#-----------------------------end TextTable----------------------------------------

#-----------------------------TextFigure---------------------------------------------
class TextFigure(TextElement):
    def __init__(self, fig_root:ET.Element, parent=None, ref_map:basicBiMap=basicBiMap()):
        """
        Initialize and parse figure found in a text element of a PMC XML.

        Parses figures into a dictionary with their information (label, caption, and link).
        Unforunately, the links are relative and cannot be reliably traced to a public URI.
        This means I have not found a way to download the actual figures to store via Pillow etc.

        TODO: Find a way to grab actual figures. May be impossible.
        """
        #initialize root, parent, and bimaps
        super().__init__(root=fig_root,parent=parent,ref_map=ref_map)

        root = fig_root
        label = root.find('.//label')
        if label is not None:
            label = label.text
        caption = root.find('.//caption')
        if caption is not None:
            caption = ''.join(caption.itertext())
        graphic_href = root.find('.//graphic').get('{http://www.w3.org/1999/xlink}href')

        fig_dict = {
            'Label': label,
            'Caption': caption,
            'Link': graphic_href
        }

        self.fig_dict = fig_dict

        return None

    def __str__(self):
        return str(self.fig_dict)

    def __repr__(self):
        return repr(self.fig_dict)
#-----------------------------end TextFigure---------------------------------------------


#-------------------------------End Classes----------------------------   


#---------------------------------Helpers---------------------------------
def stringify_children(node, encoding = "utf-8"):
    """
    Returns a string representation of a node and all its children (recursively),
    including markup language tags. 

    Turns any bytestrings in the subtree representation to regular strings, following
    the provided encoding.
    """
    subtree = [chunk for chunk in chain(
            (node.text,),
            chain(*((ET.tostring(child, with_tail=False), child.tail) for child in node.getchildren())),
            (node.tail,)) if chunk]
    #decode any bytestrings
    for i in range(len(subtree)):
        if type(subtree[i]) == bytes:
            subtree[i] = subtree[i].decode(encoding)
    return ''.join(subtree).strip()
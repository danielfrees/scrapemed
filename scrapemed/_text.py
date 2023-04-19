"""
ScrapeMed's "_text" module is aimed at organizing text found in markup language.

In the context of the scrapemed package, this supports the organization of text 
found within paragraphs (<p>) and sections (<sec>) tags in downloaded XML from 
PubMedCentral.
"""


import lxml.etree as ET
import textwrap
import scrapemed._clean as _clean
from scrapemed.utils import basicBiMap    
import scrapemed._morehtml as mhtml
from itertools import chain
import warnings

#-------------------------------Classes----------------------------
class multipleTitleWarning(Warning):
    """
    Raised when one title expected, but multiple found.
    """
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return repr(self.message)

#-----------------------------------------TextElement---------------------------------------------------
class TextElement():
    """
    Base class for elements parsed from XML/HTML markup language. 
    """        
    def __init__(self, root:ET.Element, parent:'TextElement'=None, ref_map:basicBiMap=None):
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

    TODO: Deal with xrefs, tables, etc. found within p tags.
    """
    def __init__(self, p_root:ET.Element, parent=None, ref_map:basicBiMap=None):
        """
        
        """
        super().__init__(root=p_root,parent=parent) #initialize TextElement

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
                    raise multipleTitleWarning("Warning: Multiple Titles found for a single TextSection. Check markup file formatting.")
                self.title = child.text
            elif child.tag == 'sec':
                self.children.append(TextSection(child, parent=self, ref_map=self.get_ref_map()))
            elif child.tag == 'p':
                self.children.append(TextParagraph(child, parent=self, ref_map=self.get_ref_map()))
            else:
                raise Warning(f"Warning! Unexpected child with of type {child.tag} found under an XML <sec> tag.")

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
    
    def __eq__(self, other):
        """
        TODO: Test if this actually works for comparing TextSections
        """
        return self.title==other.title and self.children==other.children
#-----------------------------------------end TextSection---------------------------------------------------

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
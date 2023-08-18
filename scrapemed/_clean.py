"""
Scrapemed module for markup language cleaning utilities.
"""
import warnings
import re
from scrapemed.utils import basicBiMap
import scrapemed._morehtml as mhtml

#monkeypatch warnings.formatwarning for cleaner warnings
warnings.formatwarning = lambda msg, category, *args, **kwargs: f'{category.__name__}: {msg}\n\n'

class unexpectedTagWarning(Warning):
    """
    Raised when an unexpected tag enclosed in angle brackets is found. 
    """
    pass

def clean_xml_string(xml_string:str, strip_text_styling=True, verbose=False):
    """
    Wrapper function to clean xml string.

    Input:
    [xml_string]: string representing xml to be cleaned
    [strip_text_styling]: whether to remove/replace HTML text styling tags
    
    Output: Cleaned xml string
    """
    #Strip html styling if requested
    if strip_text_styling:
        xml_string = _remove_text_styling(xml_string, verbose = verbose)
    return xml_string

def _remove_text_styling(text: str, verbose=False) -> str:
    """
    Removes italic, bold, underline html text styling tags from provided text.
    Replaces sub and sup tags with _ and ^, respectively. 

    Input:
    [text] string from which to remove html text stylings

    Output: text with html text stylings removed/ replaced

    DEFAULT BEHAVIOR:
    Removals:
        <italic>,<i>,<bold>,<b>,<underline>,<u> opening and closing tags.
    Replacements (Note: all corresponding closing tags removed unless otherwise specified): 
        <sub> replaced with "_"
        <sup> replaced with "^"
        <ext-link> replaced with [External URI:]
    """
    #remove italic, bold, underline styling
    REMOVALS = ["<italic>", "<i>", "<bold>", "<b>", "<underline>", "<u>"]
    REPLACES = {"<sub>": "_", "<sup>": "^", "<ext-link>": "[External URI:]"}

    return _remove_html_styling(text, removals=REMOVALS, replaces=REPLACES, verbose=verbose)


def _remove_html_styling(text: str, removals:list[str], replaces:dict, verbose = False) -> str:
    """
    Removes specified html stylings. Helpful for cleaning up xml. 

    Input:
    [text]: str of the xml
    [removals]: list of opening tags to be removed. 
                Their closing tag equivalents will also be removed. 
                Tags will be removed regardless of attributes.
    [replaces]: dict of find, replace values. 
                Finds should be html opening tags. 
                They will be matched regardless of attributes.
    Output: XML string with HTML text styling tags removed
    """
    
    #ADD IN CLOSING TAGS FOR REMOVAL TAGS
    to_remove = removals.copy()
    more_to_remove = []
    for tag in to_remove:
        more_to_remove.append(tag[0] + "/" + tag[1:]) 
    to_remove.extend(more_to_remove)
    #ADD IN CLOSING TAGS FOR REPLACEMENT TAGS
    to_replace_basic = replaces.copy()
    for tag in to_replace_basic.keys():
        to_remove.append(tag[0] + "/" + tag[1:]) 

    #MATCH REGARDLESS OF HTML ATTRIBUTES
    #Sample of what removals should look like for tag matching regardless of attributes
    #/<head\b[^>]*>/i
    for i in range(len(to_remove)):
        to_remove[i] = to_remove[i][0:-1] + "\\b[^>]*" + to_remove[i][-1]
    to_replace = {}
    for find, replace in to_replace_basic.items():
        new_find = find[0:-1] + "\\b[^>]*" + find[-1]
        to_replace[new_find] = replace
        
    #REPORT REQUESTED BEHAVIOR AT RUNTIME
    if verbose:
        print(f"Removing the following tags:\n{to_remove}\n")
        print("Making the following replacements:\n")
        for find, replace in to_replace.items():
            print(f"{find} replaced with {replace}\n")

    #REMOVALS
    removal_pattern = '|'.join(to_remove)
    r = re.compile(removal_pattern, re.IGNORECASE)
    text = r.sub('', text)

    #REPLACEMENTS
    for find, replace in to_replace.items():
        text = re.sub(find, replace, text)

    #RETURN THE CLEANED TEXT
    return text

def split_text_and_refs(tree_text:str, ref_map:basicBiMap, id=None, on_unknown='keep'):
    """
    Split HTML tags out of text. 
    • HTML text styling tags will be removed if they aren't already.
    • <xref>, <table-wrap>, and <fig> tags will be converted to MHTML tags containing the key
    to use when searching for these references, tables, and figures. 

    Returns the cleaned text. Modifies the passed BiMap for any new key-tag pairs found.

    Input:
    [tree_text]: string representing a markup language tree, containing html tags
    [ref_map]: basicBiMap containing keys connected to reference tag values

            BiMap forward keys should be reference keys to place into the text
            in lieu of the tag for later BiMap table lookup.

            BiMap forward values should be the actual tags.

            The provided BiMap will be modified to reflect any new tag values found, and
            keys will be appended as necessary.
    [id]: Optionally provide an id for traceback of any issues.
    [on_unknown]: Behavior when encountering an unknown tag. Determines what happens to the tag contents. Default = 'keep'. 
            Options: ['drop', 'keep']

    Output: The cleaned text, and updated BiMap.
    """
    XREF_TAG_NAME = 'xref'
    FIGURE_TAG_NAME = 'fig'
    TABLE_TAG_NAME = 'table'
    TABLEWRAP_TAG_NAME = 'table-wrap'
    ALLOWED_TAG_NAMES = [XREF_TAG_NAME, FIGURE_TAG_NAME, TABLEWRAP_TAG_NAME]
    IGNORED_TAG_NAMES = []
    #regex pattern string to match tags through to closing tag or self closing
    #should match any HTML or XML tag
    XML_HTML_TAG_PATTERN = r'<([a-zA-Z][\w-]*)\b[^>]*>(.*?)</\1>|<([a-zA-Z][\w-]*)\b[^/>]*/?>'
    tag_r = re.compile(XML_HTML_TAG_PATTERN, re.DOTALL) #DOTALL used in case of multiline tag spans

    text = tree_text.strip()
    text = _remove_text_styling(text)
    cleaned_text = ""
 
    while len(text) > 0:
        match = tag_r.search(text)
        if match: #found a tag, append the text prior to the tag and deal w tag

            #EAT NEXT TAG AND MATCH PARTS
            tag_name = match.group(1)
            tag_contents = match.group(2)
            full_tag = match.group()
            

            #ADD CONTENTS PRIOR TO TAG 
            tag_start_index = match.start()
            cleaned_text += text[0:tag_start_index] 
            
            #UNKNOWN TAG PROCESSING, WARN AND PERFORM SPECIFIED BEHAVIOR
            if not tag_name in ALLOWED_TAG_NAMES:
                warning_msg = (f"Tag of type {tag_name} found in a text portion of the provided markup language. "
                f"Expected only HTML styling tags, or tags from the following list: {ALLOWED_TAG_NAMES}."
                f" Specified unknown tag behavior: {on_unknown}.")
                if id:
                    warning_msg += f" Warning occured in a text section with id: {id}."
                warnings.warn(warning_msg, unexpectedTagWarning)
                if on_unknown == 'keep':
                    cleaned_text += tag_contents
                #eat through the text that was just processed
                text = text[match.end():]

            #KNOWN TAG PROCESSING, UPDATE DATA REF
            else:  
                #add tag contents if it is an xref.
                if tag_name == 'xref':
                    cleaned_text += tag_contents
                #Get reference number for data reference
                ref_num = None
                if full_tag in ref_map.reverse:
                    #have we generated a map for this tag before?
                    ref_num = ref_map.reverse[full_tag]
                else:
                    ref_num = len(ref_map) #new tag, append a new key
                    ref_map[ref_num] = full_tag #and fill in the tag value

                data_ref_tag = mhtml.generate_typed_mhtml_tag(tag_type="dataref", string=str(ref_num))
                cleaned_text += f"{data_ref_tag}"

                #eat through the text that was just processed
                text = text[match.end():]

        else: #no more tags to deal with, add the last bits to our output text
            cleaned_text += text
            text = ""

    return cleaned_text

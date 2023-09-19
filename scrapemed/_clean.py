"""
ScrapeMed's Markup Language Cleaning Utilities
===============================================

Scrapemed module for markup language cleaning utilities.

.. warns::

   unexpectedTagWarning
       Warned when an unexpected tag enclosed in angle brackets is found.

"""

import warnings
import re
from scrapemed.utils import basicBiMap
import scrapemed._morehtml as mhtml

# monkeypatch warnings.formatwarning for cleaner warnings
warnings.formatwarning = (
    lambda msg, category, *args, **kwargs: f"{category.__name__}: {msg}\n\n"
)


class unexpectedTagWarning(Warning):
    """
    Warned when an unexpected tag enclosed in angle brackets is found.
    """

    pass


def clean_xml_string(xml_string: str, strip_text_styling=True, verbose=False):
    """
    Clean an XML string.

    :param str xml_string: The XML string to be cleaned.
    :param bool strip_text_styling: Whether to remove or replace HTML text styling tags.
    :param bool verbose: Whether to print verbose output.

    :return: The cleaned XML string.
    :rtype: str
    """
    # Strip html styling if requested
    if strip_text_styling:
        xml_string = _remove_text_styling(xml_string, verbose=verbose)
    return xml_string


def _remove_text_styling(text: str, verbose=False) -> str:
    """
    Remove specified HTML stylings from the provided text.

    This function removes specified HTML stylings from the input text. It can
    remove opening tags and their corresponding closing tags and replace
    specific opening tags with desired values.

    **Specifically:**
    This overloaded wrapper function removes italic, bold, underline HTML text
    styling tags from the input text. Additionally, it replaces <sub> with "_"
    and <sup> with "^". <ext-link> is replaced with "[External URI:]".

    :param str text: The text containing HTML stylings to be removed or replaced.
    :param list[str] removals: A list of opening tags to be removed. Their
        corresponding closing tags will also be removed. Tags will be removed
        regardless of attributes.
    :param dict replaces: A dictionary of find, replace values. The find values
        should be HTML opening tags. They will be matched regardless of attributes.
    :param bool verbose: Whether to print verbose output.

    :return: The XML string with default HTML text styling tags (`REMOVALS`, `REPLACES`)
        removed or replaced.
    :rtype: str
    """

    # remove italic, bold, underline styling
    REMOVALS = ["<italic>", "<i>", "<bold>", "<b>", "<underline>", "<u>"]
    REPLACES = {"<sub>": "_", "<sup>": "^", "<ext-link>": "[External URI:]"}

    return _remove_html_styling(
        text, removals=REMOVALS, replaces=REPLACES, verbose=verbose
    )


def _remove_html_styling(
    text: str, removals: list[str], replaces: dict, verbose=False
) -> str:
    """
    Remove specified HTML stylings from the provided text.

    :param str text: The text containing HTML stylings to be removed.
    :param list[str] removals: A list of opening tags to be removed. Their
        corresponding closing tags will also be removed. Tags will be removed
        regardless of attributes.
    :param dict replaces: A dictionary of find, replace values. The find values
        should be HTML opening tags. They will be matched regardless of attributes.
    :param bool verbose: Whether to print verbose output.

    :return: The XML string with specified HTML text styling tags removed.
    :rtype: str
    """

    # ADD IN CLOSING TAGS FOR REMOVAL TAGS
    to_remove = removals.copy()
    more_to_remove = []
    for tag in to_remove:
        more_to_remove.append(tag[0] + "/" + tag[1:])
    to_remove.extend(more_to_remove)
    # ADD IN CLOSING TAGS FOR REPLACEMENT TAGS
    to_replace_basic = replaces.copy()
    for tag in to_replace_basic.keys():
        to_remove.append(tag[0] + "/" + tag[1:])

    # MATCH REGARDLESS OF HTML ATTRIBUTES
    # Sample of what removals should look like for tag matching
    # regardless of attributes
    # /<head\b[^>]*>/i
    for i in range(len(to_remove)):
        to_remove[i] = to_remove[i][0:-1] + "\\b[^>]*" + to_remove[i][-1]
    to_replace = {}
    for find, replace in to_replace_basic.items():
        new_find = find[0:-1] + "\\b[^>]*" + find[-1]
        to_replace[new_find] = replace

    # REPORT REQUESTED BEHAVIOR AT RUNTIME
    if verbose:
        print(f"Removing the following tags:\n{to_remove}\n")
        print("Making the following replacements:\n")
        for find, replace in to_replace.items():
            print(f"{find} replaced with {replace}\n")

    # REMOVALS
    removal_pattern = "|".join(to_remove)
    r = re.compile(removal_pattern, re.IGNORECASE)
    text = r.sub("", text)

    # REPLACEMENTS
    for find, replace in to_replace.items():
        text = re.sub(find, replace, text)

    # RETURN THE CLEANED TEXT
    return text


def split_text_and_refs(
    tree_text: str, ref_map: basicBiMap, id=None, on_unknown="keep"
):
    """
    Split HTML tags out of text.

    - HTML text styling tags will be removed if they aren't already.
    - <xref>, <table-wrap>, and <fig> tags will be converted to MHTML tags containing
      the key to use when searching for these references, tables, and figures.

    Returns the cleaned text and updates the passed BiMap for any new key-tag
    pairs found.

    :param str tree_text: A string representing a markup language tree containing
        HTML tags.
    :param ref_map: A BiMap containing keys connected to reference tag values. BiMap
        forward keys should be reference keys to place into the text in lieu of the
        tag for later BiMap table lookup. BiMap forward values should be the
        actual tags. The provided BiMap will be modified to reflect any new tag
        values found, and keys will be appended as necessary.
    :type ref_map: basicBiMap
    :param id: Optionally provide an id for traceback of any issues.
    :type id: Any, optional
    :param str on_unknown: Behavior when encountering an unknown tag. Determines
        what happens to the tag contents.
        Default is 'keep'. Options: ['drop', 'keep']

    :return: A tuple containing the cleaned text and the updated BiMap.
    :rtype: Tuple[str, basicBiMap]
    """
    XREF_TAG_NAME = "xref"
    FIGURE_TAG_NAME = "fig"
    TABLEWRAP_TAG_NAME = "table-wrap"
    ALLOWED_TAG_NAMES = [XREF_TAG_NAME, FIGURE_TAG_NAME, TABLEWRAP_TAG_NAME]

    # regex pattern string to match tags through to closing tag or self closing
    # should match any HTML or XML tag
    XML_HTML_TAG_PATTERN = (
        r"<([a-zA-Z][\w-]*)\b[^>]*>(.*?)</\1>|<([a-zA-Z][\w-]*)\b[^/>]*/?>"
    )
    tag_r = re.compile(
        XML_HTML_TAG_PATTERN, re.DOTALL
    )  # DOTALL used in case of multiline tag spans

    text = tree_text.strip()
    text = _remove_text_styling(text)
    cleaned_text = ""

    while len(text) > 0:
        match = tag_r.search(text)
        if match:
            # found a tag, append the text prior to the tag
            # and deal w tag
            # EAT NEXT TAG AND MATCH PARTS
            tag_name = match.group(1)
            tag_contents = match.group(2)
            full_tag = match.group()

            # ADD CONTENTS PRIOR TO TAG
            tag_start_index = match.start()
            cleaned_text += text[0:tag_start_index]

            # UNKNOWN TAG PROCESSING, WARN AND PERFORM SPECIFIED BEHAVIOR
            if tag_name not in ALLOWED_TAG_NAMES:
                warning_msg = (
                    f"Tag of type {tag_name} found in a text portion of "
                    "the provided markup language. "
                    "Expected only HTML styling tags, or tags from the "
                    f"following list: {ALLOWED_TAG_NAMES}."
                    f" Specified unknown tag behavior: {on_unknown}."
                )
                if id:
                    warning_msg += (
                        " Warning occured in a text section " f"with id: {id}."
                    )
                warnings.warn(warning_msg, unexpectedTagWarning)
                if on_unknown == "keep":
                    cleaned_text += tag_contents
                # eat through the text that was just processed
                text = text[match.end() :]

            # KNOWN TAG PROCESSING, UPDATE DATA REF
            else:
                # add tag contents if it is an xref.
                if tag_name == "xref":
                    cleaned_text += tag_contents
                # Get reference number for data reference
                ref_num = None
                if full_tag in ref_map.reverse:
                    # have we generated a map for this tag before?
                    ref_num = ref_map.reverse[full_tag]
                else:
                    ref_num = len(ref_map)  # new tag, append a new key
                    ref_map[ref_num] = full_tag  # and fill in the tag value

                data_ref_tag = mhtml.generate_typed_mhtml_tag(
                    tag_type="dataref", string=str(ref_num)
                )
                cleaned_text += f"{data_ref_tag}"

                # eat through the text that was just processed
                text = text[match.end() :]

        else:
            # no more tags to deal with, add the last bits to our output text
            cleaned_text += text
            text = ""

    return cleaned_text

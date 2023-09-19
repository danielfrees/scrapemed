"""
ScrapeMed's Custom Markup Language - MoreHTML (MHTML)
======================================================

Wrapper on basic functions for HTML manipulation.

**Added on top of core html functionality:**
Non-markup significant unescape function, custom MHTML tag encoding and removal.
"""

import re
import html


def unescape_except(s, **kwargs):
    """
    Convert all named and numeric character references in the provided string to
    the corresponding Unicode characters, excluding any provided encodings to be
    ignored.

    :param str s: The input string containing character references.
    :param kwargs: Keyword arguments of the form key=encoding. These encodings
            will be ignored when unescaping.
                    For keys with multiple encodings, use unique keynames.
                   Encodings must be single code strings.
    :type kwargs: dict
    :return: A string with character references unescaped, except for the
        specified encodings to be ignored.
    :rtype: str

    This function uses the rules defined by the HTML 5 standard for both valid
    and invalid character references, and the list of HTML 5 named character
    references defined in html.entities.html5.
    """

    # no need to do anything if there are no html encodings
    if "&" not in s:
        return s

    encoding_dict = {}

    # Translate keys to MHTML placeholder codes
    for key, encoding in kwargs.items():
        placehold_str = generate_mhtml_tag(key)
        encoding_dict[placehold_str] = encoding

    # Convert encodings to MHTML placeholder codes
    for placehold_str, encoding in encoding_dict.items():
        code_to_save = re.compile(re.escape(encoding))
        s = code_to_save.sub(placehold_str, s)

    # Unescape everything else
    s = html.unescape(s)

    # Convert placeheld items back to their original html encodings
    for placehold_str, encoding in encoding_dict.items():
        placehold_r = re.compile(re.escape(placehold_str))
        s = placehold_r.sub(encoding, s)

    return s


def generate_mhtml_tag(string: str) -> str:
    """
    Generates an MHTML tag from the provided string.

    :param str string: The text to be tagged in MHTML format.
    :return: An MHTML tag containing the input string, in format
        `f"[MHTML::{string}]"`
    :rtype: str
    """
    return f"[MHTML::{string}]"


def generate_typed_mhtml_tag(tag_type: str, string: str) -> str:
    """
    Generates a typed MHTML tag from the provided string.

    :param str tag_type: The type of the MHTML tag.
    :param str string: The text to be tagged in MHTML format.
    :return: A typed MHTML tag containing the input string, in format
        `[MHTML::type::string]`.
    :rtype: str
    """
    return f"[MHTML::{tag_type}::{string}]"


def remove_mhtml_tags(text: str) -> str:
    """
    Removes all MHTML tags and typed MHTML tags found in the provided text.

    :param str text: The text from which to remove MHTML tags.
    :return: The text with MHTML tags removed.
    :rtype: str
    """
    # match MHTML tags
    # group1 = tag type for typed MHTML tags
    # group2 = tag value for typed MHTML tags
    # group3 = tag for non-typed MHTML tags
    mhtml_pattern = r"\[MHTML::([^:\[\]]+)::([^:\[\]]+)\]" r"|\[MHTML::([^:\[\]]+)\]"
    mhtml_r = re.compile(mhtml_pattern)
    # remove MHTML tags and return result
    return mhtml_r.sub("", text)

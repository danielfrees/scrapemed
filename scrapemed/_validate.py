"""
ScrapeMed's ``_validate`` Module
=================================

Validation module for determining whether XML conforms to a format
supported by the scrapemed package (NLM Articleset 2.0 DTD).

**Custom Exception**:
    - ``noDTDFoundError``: Raised when no DTD specification can be found in the
        downloaded XML.
"""

import re
import lxml.etree as ET
import os
from io import StringIO
from scrapemed.utils import cleanerdoc

SUPPORTED_DTD_URLS = [
    "https://dtd.nlm.nih.gov/ncbi/pmc/articleset/nlm-articleset-2.0.dtd"
]
# Regex DTD URL Patterns
DTD_URL_PATTERN = re.compile(r'"(https?://\S+)"')
END_OF_URL_PATTERN = re.compile(r"[^/]+$")


class noDTDFoundError(Exception):
    """
    Raised when no DTD specification can be found in a downloaded XML,
    preventing validation.
    """

    pass


# ---------------------------DATA VALIDATION-------------------------------
def validate_xml(xml: ET.ElementTree) -> bool:
    """
    Validate an XML ElementTree against a supported Document Type Definition
    (DTD).

    This function validates the provided XML ElementTree against a supported
    DTD (Document Type Definition). The supported DTDs are defined by the files
    in the 'scrapemed/data/DTDs' directory. Currently only NLM Articleset 2.0
    (The DTD used by PubMed Central) is supported.

    :param ET.ElementTree xml: An XML ElementTree to be validated.

    :return: True if the XML is validated successfully against a supported DTD,
        False otherwise.
    :rtype: bool

    :raises noDTDFoundError: If no DTD is specified for validation in the
        XML doctype.
    """
    # Find DTD and confirm its supported
    match = DTD_URL_PATTERN.search(xml.docinfo.doctype)
    url = None
    if match:
        url = match.group(1)
        assert url in SUPPORTED_DTD_URLS
    else:
        raise noDTDFoundError(
            cleanerdoc(
                """A DTD must be specified for validation. Set
                       validate=false if you want to proceeed without
                       validation."""
            )
        )

    match = END_OF_URL_PATTERN.search(url)
    dtd_filename = match.group(0)
    dtd_filepath = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "data", "DTDs", dtd_filename
    )

    dtd_doc = None
    with open(dtd_filepath, "r") as f:
        dtd_doc = f.read()
    if dtd_doc is None:
        raise noDTDFoundError(
            cleanerdoc(
                """DTD not found in scrapemed package. Ensure you are using the
                latest package version."""
            )
        )

    dtd = ET.DTD(StringIO(dtd_doc))

    return dtd.validate(xml)


# -------------------------END DATA VALIDATION-------------------------------

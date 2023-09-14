"""Test ScrapeMed's custom Markup Language MHTML, used primarily for
placeholders on data references within text."""

import scrapemed._morehtml as mhtml


def test_mhtml():
    SAMPLE_TEXT1 = (
        "Hello, this is a test for removal of regular "
        "MHTML tags such as [MHTML::tag], and also typed MHTML tags "
        "such as [MHTML::tag_type::tag_value]. "
        "Anyway, that's about all."
    )

    assert mhtml.remove_mhtml_tags(SAMPLE_TEXT1) == (
        "Hello, this is a test for removal of regular MHTML "
        "tags such as , and also typed MHTML tags such as . "
        "Anyway, that's about all."
    )

    return None

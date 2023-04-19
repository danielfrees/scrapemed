import pytest
from xml.etree.ElementTree import ProcessingInstruction
import scrapemed.trees as trees
import scrapemed.scrape as scrape

def test_scrape():
    STYLED_TEST_TEXT = ("<paper>Hello my name is Daniel, my <italic attr='Whatever' color = 'Blue'>favorite</italic> chemical is <i>C</i><sub>4</sub>. "
    "<b hello = 'dan' haha = 'whatever'>I</b> also <italic attr ='something'>wanted</italic> to say that <underline>you</underline> should use this code as a<sup>1</sup> test to make sure "
    "html tagging removal is going as expected.</paper>")

    ##generate_data_dictionary without stripping html styling
    test_tree = scrape.xml_tree_from_string(STYLED_TEST_TEXT, strip_text_styling=False)
    CORRECT_DATA_DICT = {'paper': {}, 'italic': {'attr': ['Whatever', 'something'], 
                    'color': ['Blue']}, 'i': {}, 'sub': {}, 'b': {'hello': ['dan'], 
                    'haha': ['whatever']}, 'underline': {}, 'sup': {}}
    assert trees._generate_data_dictionary(test_tree) == CORRECT_DATA_DICT 

    return None
import scrapemed._text as _text
from scrapemed._text import TextParagraph, TextSection
import lxml.etree as ET
from scrapemed.utils import basicBiMap
import warnings


def test_text():
    #test getters and setters
    text1 = ("<sec> <title>Test of the scrapemed._text Module</title> "
    "<p attr='ok'> Testing paragraph 1 </p> <p> Testing paragraph 2 </p> "
    "<sec attr='oksec'><title>Testing Subsection</title><p>Grandchild test</p> </sec> </sec>")
    text1_root = ET.fromstring(text1.encode('utf-8'))

    text1_ts = TextSection(text1_root)

    #test child and title collection
    text1_p1 = text1_ts.children[0]
    text1_p2 = text1_ts.children[1]
    text1_sec1 = text1_ts.children[2]
    text1_grandchild = text1_sec1.children[0]
    assert type(text1_p1) == TextParagraph
    assert type(text1_p2) == TextParagraph
    assert type(text1_sec1) == TextSection
    assert text1_ts.title == "Test of the scrapemed._text Module"
    assert text1_sec1.title == "Testing Subsection"
    assert text1_grandchild.text == "Grandchild test"

    #test getters and setters for maps. 
    # #Getters and setters should work from anywhere in the tree
    test_ref_map = basicBiMap({'ref':'test'})
    
    text1_ts.set_ref_map(test_ref_map)
    assert text1_ts.ref_map == test_ref_map
    assert text1_ts.get_ref_map() == test_ref_map
    for child in text1_ts.children:
        assert child.get_ref_map() == test_ref_map
    
    test_ref_map2 = basicBiMap({'ref':'test2'})
    text1_p1.set_ref_map(test_ref_map2)
    assert text1_ts.get_ref_map() == test_ref_map2
    text1_sec1.set_ref_map(test_ref_map)
    assert text1_ts.get_ref_map() == test_ref_map
    for child in text1_ts.children:
        assert child.get_ref_map() == test_ref_map

    #test helpers
    text2 = ("<sec> <title>Test of the scrapemed._text Module</title> "
    "<p attr='ok'>Testing <xref>reference <italic>test</italic></xref> paragraph <italic>1</italic></p> <p> Testing paragraph 2 </p> "
    "<sec attr='oksec'><title>Testing Subsection</title><p>Grandchild test</p> </sec> </sec>")
    text2_root = ET.fromstring(text2.encode('utf-8'))
    text2_ts = TextSection(text2_root)
    test2_p1 = text2_ts.children[0]
    full_test2_p1_subtree_text = _text.stringify_children(test2_p1.root)
    print(full_test2_p1_subtree_text)
    assert full_test2_p1_subtree_text.strip() == "Testing <xref>reference <italic>test</italic></xref> paragraph <italic>1</italic>".strip()

    return None
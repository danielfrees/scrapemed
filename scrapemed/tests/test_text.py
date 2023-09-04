import scrapemed._text as _text
from scrapemed._text import TextParagraph, TextSection, TextTable, TextFigure
from scrapemed.paper import Paper
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

    tables_and_figs_xml = """<article>
  <body>
    <table-wrap id="tab1">
      <table>
        <thead>
          <tr>
            <th>Header 1</th>
            <th>Header 2</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>Data 1</td>
            <td>Data 2</td>
          </tr>
          <tr>
            <td>Data 3</td>
            <td>Data 4</td>
          </tr>
        </tbody>
      </table>
    </table-wrap>
    
    <figure id="fig1">
      <caption>Figure 1: Sample Figure</caption>
      <!-- Your figure content goes here -->
    </figure>
    
    <xref rid="fig1" ref-type="figure">Figure 1</xref>
    <xref rid="tab1" ref-type="table">Table 1</xref>
  </body>
</article>"""

    tables_and_figs_root = ET.fromstring(tables_and_figs_xml.encode('utf-8'))
    
    table_root = tables_and_figs_root.xpath("//table-wrap")[0]
    print(TextTable(table_root))
    print(type(TextTable(table_root)))


    return None
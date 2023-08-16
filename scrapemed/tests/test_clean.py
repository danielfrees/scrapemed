import pytest
import scrapemed._clean as _clean
from scrapemed.utils import basicBiMap

def test_clean():
    ##_remove_text_styling
    STYLED_TEST_TEXT = ("<paper>Hello my name is Daniel, my <italic attr='Whatever' color = 'Blue'>favorite</italic> chemical is <i>C</i><sub>4</sub>. "
    "<b hello = 'dan' haha = 'whatever'>I</b> also <italic attr ='something'>wanted</italic> to say that <underline>you</underline> should use this code as a<sup>1</sup> test to make sure "
    "html tagging removal is going as expected. "
    "I also want to make sure that external links are parsed correctly, such as this link to "
    "the URI found at <ext-link attr='attr'>www.test.com</ext-link>.</paper>"
    )
    CORRECT_CLEAN_TEXT = ("<paper>Hello my name is Daniel, my favorite chemical is C_4."
    " I also wanted to say that you should use this code as a^1 test "
    "to make sure html tagging removal is going as expected. "
    "I also want to make sure that external links are parsed correctly, such as this link to "
    "the URI found at [External URI:]www.test.com.</paper>"
    )
    assert _clean._remove_text_styling(STYLED_TEST_TEXT, verbose=True) == CORRECT_CLEAN_TEXT 


    #test tag parsing of paragraph text
    SAMPLE_PAR_2 = ('Baseline characteristics for the three studies are shown '
    'in Table&#xA0;<xref rid="Tab1" ref-type="table">1</xref>. A total of 35 subjects were '
    'randomized in Study 1 and 46 in Study 2. '
    """
    <table-wrap id="Tab1">
        <label>Table 1</label>
        <caption>Sample Table Caption</caption>
        <table>
            <thead>
                <tr>
                    <th>Column A</th>
                    <th>Column B</th>
                    <th>Column C</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Data 1A</td>
                    <td>Data 1B</td>
                    <td>Data 1C</td>
                </tr>
                <tr>
                    <td>Data 2A</td>
                    <td>Data 2B</td>
                    <td>Data 2C</td>
                </tr>
            </tbody>
        </table>
    </table-wrap>
    """
    )

    ref_map = basicBiMap()
    cleaned_text = _clean.split_text_and_refs(SAMPLE_PAR_2, ref_map)
    print("SAMPLE PAR CLEANED FROM REFS: " + cleaned_text)
    print("RESULTING REF MAP: " + str(ref_map))


    return None
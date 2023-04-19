import pytest
import scrapemed._clean as _clean

def test_clean():
    ##_remove_text_styling
    STYLED_TEST_TEXT = ("<paper>Hello my name is Daniel, my <italic attr='Whatever' color = 'Blue'>favorite</italic> chemical is <i>C</i><sub>4</sub>. "
    "<b hello = 'dan' haha = 'whatever'>I</b> also <italic attr ='something'>wanted</italic> to say that <underline>you</underline> should use this code as a<sup>1</sup> test to make sure "
    "html tagging removal is going as expected.</paper>")
    CORRECT_CLEAN_TEXT = ("<paper>Hello my name is Daniel, my favorite chemical is C_4."
    " I also wanted to say that you should use this code as a^1 test "
    "to make sure html tagging removal is going as expected.</paper>")
    assert _clean._remove_text_styling(STYLED_TEST_TEXT, verbose=True) == CORRECT_CLEAN_TEXT 


    #test tag parsing of paragraph text
    SAMPLE_PAR = ('<p id="Par22">Baseline characteristics for the three studies are shown '
    'in Table&#xA0;<xref rid="Tab1" ref-type="table">1</xref>. A total of 35 subjects were '
    'randomized in Study 1 and 46 in Study 2. In Study 3, 21 subjects were assigned to treatment. '
    'In all three studies, the proportion of males and females was approximately 50%. In Study 3, '
    'the majority (62%) of subjects were White, whereas in Studies 1 and 2, the largest proportion '
    'of subjects were Black (54% and 41%, respectively). One subject in Study 1 discontinued study '
    'drug during the first treatment period due to an inability to swallow study medication, and '
    'two subjects in Study 2 discontinued study drug during the first treatment period due to '
    'difficulties in collecting PK samples; no PK profiling was possible for these two subjects. '
    'All 21 subjects in Study 3 completed treatment and were analyzed for PK metrics and safety.'
    '<table-wrap id="Tab1"><label>Table&#xA0;1</label><caption><p>Baseline characteristics</p>'
    '</caption><table frame="hsides" rules="groups"><thead><tr><th align="left"/><th align="left">'
    'Study 1 [<italic>N&#x2009;</italic>=&#x2009;35]</th><th align="left">Study 2 '
    '[<italic>N&#x2009;</italic>=&#x2009;46]</th><th align="left">Study 3 '
    '[<italic>N&#x2009;</italic>=&#x2009;21]</th></tr></thead><tbody><tr><td align="left">'
    'Sex, male</td><td align="left">18 (51.4)</td><td align="left">25 (54.3)</td><td align="left">'
    '10 (47.6)</td></tr><tr><td align="left">Mean age, (years) (SD)</td><td align="left">35.6 (9.4)'
    '</td><td align="left">39.3 (9.2)</td><td align="left">14.7 (1.8)</td></tr><tr><td align="left">'
    '&#xA0;Age 12&#x2013;14&#xA0;years</td><td align="left">&#x2013;</td><td align="left">&#x2013;'
    '</td><td align="left">10 (47.6)</td></tr><tr><td align="left">&#xA0;Age 15&#x2013;17&#xA0;years'
    '</td><td align="left">&#x2013;</td><td align="left">&#x2013;</td><td align="left">11 (52.4)'
    '</td></tr><tr><td align="left" colspan="4">Race</td></tr><tr><td align="left">&#xA0;White'
    '</td><td align="left">4 (11.4)</td><td align="left">9 (19.6)</td><td align="left">13 (61.9)'
    '</td></tr><tr><td align="left">&#xA0;Black</td><td align="left">19 (54.3)</td><td align="left">'
    '19 (41.3)</td><td align="left">3 (14.3)</td></tr><tr><td align="left">&#xA0;Other</td>'
    '<td align="left">12 (34.3)</td><td align="left">18 (39.1)</td><td align="left">'
    '5 (23.8)</td></tr><tr><td align="left" colspan="4">Ethnicity</td></tr><tr><td align="left">'
    '&#xA0;Hispanic/Latino</td><td align="left">14 (40.0)</td><td align="left">18 (39.1)'
    '</td><td align="left">4 (19.0)</td></tr><tr><td align="left">&#xA0;Non-Hispanic/Latino</td>'
    '<td align="left">21 (60.0)</td><td align="left">28 (60.9)</td><td align="left">17 (81.0)'
    '</td></tr><tr><td align="left">Mean weight, (kg) (SD)</td><td align="left">78.5 (14.1)'
    '</td><td align="left">75.4 (12.5)</td><td align="left">56.2 (9.2)</td></tr><tr><td align="left">'
    'Mean height, (cm) (SD)</td><td align="left">171.2 (11.4)</td><td align="left">169.9 (8.6)</td>'
    '<td align="left">164.3 (7.4)</td></tr><tr><td align="left">Mean BMI, (kg/m<sup>2</sup>) (SD)'
    '</td><td align="left">26.6 (3.0)</td><td align="left">26.0 (3.0)</td><td align="left">&#x2013;'
    '</td></tr></tbody></table><table-wrap-foot><p>Data are expressed as <italic>n'
    '</italic> (%) unless otherwise specified</p><p><italic>BMI</italic> body mass index, '
    '<italic>SD</italic> standard deviation</p></table-wrap-foot></table-wrap></p>')


    return None
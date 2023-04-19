import scrapemed.utils as smutils
from scrapemed.utils import reversedBiMapComparisonWarning
import pytest

def test_utils():

    #test basic behavior and reverse member
    bimap = smutils.basicBiMap()
    bimap['one'] = 'hello'
    bimap['three'] = 'daniel'
    assert bimap.reverse['hello'] == 'one' and bimap['one'] == 'hello'
    assert bimap['three'] == 'daniel' and bimap.reverse['daniel'] == 'three'

    #test __eq__ behavior
    bimap2 = smutils.basicBiMap(one='hello', three='daniel')
    assert bimap == bimap2
    bimap3 = smutils.basicBiMap(hello='one', daniel='three')
    
    with pytest.warns(reversedBiMapComparisonWarning) as w:
        assert not bimap == bimap3, "Exactly reversed bimaps raise warning, and are not equal."

    return None #success
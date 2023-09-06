import pytest
import sys
sys.path.insert(0, "../../scrapemed")
import scrapemed.paper as paper
import scrapemed.scrape as scrape
from scrapemed.paperSet import paperSet
import pandas as pd
import lxml
from dotenv import load_dotenv
import os
load_dotenv()

def test_paperset():
    EMAIL = os.getenv("PMC_EMAIL")
    pset = paperSet.from_search(EMAIL, term = "brain[ti] AND surgery[ti]", retmax = 3)
    assert len(pset.papers) == 3
    assert len(pset.df) == 3
    assert len(pset.to_df()) == 3
    pset.visualize()
    pset.add_pmcids(pmcids= [7067710, 7067711], email = EMAIL)
    assert len(pset.papers) == 5
    assert len(pset.df) == 5
    assert len(pset.to_df()) == 5

    pset = paperSet.from_pmcid_list([7067710, 7067711], EMAIL)
    assert len(pset.papers) == 2
    assert len(pset.df) == 2
    assert len(pset.to_df()) == 2
        
    return None
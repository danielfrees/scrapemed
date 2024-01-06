"""
Test ScrapeMed's scrape module.
"""

import scrapemed.scrape as scrape
from dotenv import load_dotenv
from Bio import Entrez
import os
import lxml

load_dotenv()


def test_scrape():
    EMAIL = os.getenv("PMC_EMAIL")
    Entrez.email = EMAIL

    # test pmc scraping
    brain_surgery_articles = scrape.search_pmc(
        EMAIL, "brain[ti] AND surgery[ti]", retmax=10, verbose=False
    )["IdList"]
    assert brain_surgery_articles == [
        "10744829",
        "10711149",
        "10710589",
        "10698442",
        "10692402",
        "10749855",
        "10742002",
        "10714222",
        "10681104",
        "10680896",
    ]

    # check that get_xmls func works properly
    xmls = scrape.get_xmls(brain_surgery_articles[0:2], email=EMAIL)
    assert isinstance(xmls[0], lxml.etree._ElementTree)

    return None

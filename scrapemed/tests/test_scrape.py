import pytest
import scrapemed.scrape as scrape
from dotenv import load_dotenv
import os
import lxml
load_dotenv()

def test_scrape():
    EMAIL = os.getenv("PMC_EMAIL")

    #test pmc scraping
    brain_surgery_articles = scrape.search_pmc(EMAIL, "brain[ti] AND surgery[ti]", retmax = 10, verbose = False)['IdList']
    assert brain_surgery_articles == ['10445649', '9889004', '9888923', '10423256', '10417431', '10414059', '10410636', '10406254', '10402651', '10372448']

    #check that get_xmls func works properly
    xmls = scrape.get_xmls(brain_surgery_articles[0:2], email=EMAIL)
    assert(type(xmls[0]) == lxml.etree._ElementTree)

    return None
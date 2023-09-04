import pytest
import scrapemed.paper as paper
import pandas as pd
import warnings
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def test_paper():
    path_to_testdata = os.path.join(os.path.dirname(__file__), "testdata")

    #Specify creds and PMCID
    PMCID = 7067710#------------------------------------------------------------------
    email = os.getenv("PMC_EMAIL")

    warnings.filterwarnings("ignore")
    p = paper.Paper.from_pmc(PMCID, email, download=True, verbose=True)
    warnings.filterwarnings("default")

    assert p.title == 'Phase I Pharmacokinetic Study of Fixed-Dose Combinations of Ibuprofen and Acetaminophen in Healthy Adult and Adolescent Populations'
    AUTHORS_DATA = {
        'Contributor_Type': ['Author', 'Author', 'Author', 'Author', 'Author', 'Author', 'Author', 'Author', 'Author'],
        'First_Name': ['Sanela', 'Debra', 'Bradley', 'Rina', 'Dongweon', 'Kyle', 'David E.', 'Suzanne', 'Mario'],
        'Last_Name': ['Tarabar', 'Kelsh', 'Vince', 'Leyva', 'Song', 'Matschke', 'Kellstein', 'Meeves', 'Cruz-Rivera'],
        'Email_Address': ['Sanela.Tarabar@pfizer.com', None, None, None, None, None, None, None, None],
        'Affiliations': [
            ['Aff1: Pfizer New Haven Clinical Research Unit, New Haven, CT USA', 'Aff6: Clinical Research and Development, KS1, 1 Portland Street, Cambridge, MA 02139 USA'],
            ['Aff2: Altasciences/Vince and Associates Clinical Research, Overland Park, KS USA'],
            ['Aff2: Altasciences/Vince and Associates Clinical Research, Overland Park, KS USA'],
            ['Aff3: Pfizer Consumer Healthcare, Madison, NJ USA'],
            ['Aff4: Pfizer Inc., Collegeville, PA USA'],
            ['Aff4: Pfizer Inc., Collegeville, PA USA'],
            ['Aff5: Pfizer Consumer Healthcare, Madison, NJ USA'],
            ['Aff5: Pfizer Consumer Healthcare, Madison, NJ USA'],
            ['Aff5: Pfizer Consumer Healthcare, Madison, NJ USA']
        ]
    }
    AUTHORS_DF = pd.DataFrame(AUTHORS_DATA)
    assert p.authors.equals(AUTHORS_DF)
    assert p.non_author_contributors == "No non-author contributors were found after parsing this paper."
    #TODO: add abstract and body tests, couldn't get them working before
    assert p.journal_id == {'nlm-ta': 'Drugs R D', 'iso-abbrev': 'Drugs R D'}
    assert p.issn == {'ppub': '1174-5886', 'epub': '1179-6901'}
    assert p.journal_title == 'Drugs in R&D'
    assert p.publisher_name == 'Springer International Publishing'
    assert p.publisher_location == 'Cham'
    assert p.article_id == {'pmid': '32130679',
                            'pmc': '7067710',
                            'publisher-id': '293',
                            'doi': '10.1007/s40268-020-00293-5'}
    assert p.article_types == ['Original Research Article']
    assert p.article_categories == 'No extra article categories found. Check paper.article_types for header categories.'
    assert p.published_date == {'epub': datetime(2020, 3, 4, 0, 0),
                                'pmc-release': datetime(2020, 3, 4, 0, 0),
                                'ppub': datetime(2020, 3, 1, 0, 0)}
    assert p.volume == '20'
    assert p.issue == '1'
    assert p.fpage == '23'
    assert p.lpage == '37'
    assert p.permissions == {'Copyright Statement': '© The Author(s) 2020',
                            'License Type': 'OpenAccess',
                            'License Text': "Open AccessThis article is licensed under a Creative Commons Attribution-NonCommercial 4.0 International License, which permits any non-commercial use, sharing, adaptation, distribution and reproduction in any medium or format, as long as you give appropriate credit to the original author(s) and the source, provide a link to the Creative Commons licence, and indicate if changes were made. The images or other third party material in this article are included in the article's Creative Commons licence, unless indicated otherwise in a credit line to the material. If material is not included in the article's Creative Commons licence and your intended use is not permitted by statutory regulation or exceeds the permitted use, you will need to obtain permission directly from the copyright holder.To view a copy of this licence, visit [External URI:]http://creativecommons.org/licenses/by-nc/4.0/."}

    #end 7067710------------------------------------------------------------------

    PMCID = 7067711#------------------------------------------------------------------makes sure flat abstracts work too
    email = "danielfrees247@gmail.com"

    warnings.filterwarnings("ignore")
    p = paper.Paper.from_pmc(PMCID, email)
    warnings.filterwarnings("default")

    assert p.title == 'Decline and diversity in Swedish seas: Environmental narratives in marine history, science and policy'
    ABSTRACT_7067711 = ""
    with open(os.path.join(path_to_testdata, "7067711_abstract.txt")) as f:
        ABSTRACT_7067711 = f.read()
    assert str(p.abstract[0]) == ABSTRACT_7067711 #makes sure the retrieved abstract is a flat string matching the abstract on PMC

                            
    return None
import pytest
import scrapemed.paper as paper
import pandas as pd
import warnings

def test_paper():
    #Specify creds and PMCID
    PMCID = 7067710
    email = "danielfrees247@gmail.com"

    warnings.filterwarnings("ignore")
    p = paper.Paper(PMCID, email)
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
            ['Aff4: Collegeville, PA USA'],
            ['Aff4: Collegeville, PA USA'],
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
                            
    return None
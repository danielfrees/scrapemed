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

    p = paper.Paper.from_pmc(PMCID, email, download=False, suppress_warnings=True)

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
    assert p.copyright == '© The Author(s) 2020'
    assert p.license == 'OpenAccess'
    assert p.funding == ['Pfizer Consumer Healthcare']
    assert p.footnote == 'The authors David E. Kellstein, Suzanne Meeves and Mario Cruz-Rivera were Employees of Pfizer Consumer Healthcare, Madison, NJ, USA at the time this research was conducted.'
    assert p.acknowledgements == ['Acknowledgements \n       Medical writing support was provided by John H. Simmons, MD, of Peloton Advantage, LLC, an OPEN Health company, and was funded by Pfizer. On 1 August 2019, PCH became part of GSK Consumer Healthcare. The authors would like to thank Zhongwei Zhou, lead programmer, and all the programmers who supported these studies, as well as the study participants.']
    assert p.notes == ['Title: Author Contributions\nStudy design: All authors; Study investigator: Sanela Tarabar, Debra Kelsh; Enrolled subjects: Sanela Tarabar, Debra Kelsh; Collection and assembly of data: All authors; Data analysis: Rina Leyva (Lead Statistician); Data interpretation: All authors; Manuscript preparation: All authors; Manuscript review and revisions: All authors; Final approval of manuscript: All authors.\n',
                    'Title: Data Sharing Statement\nUpon request, and subject to certain criteria, conditions and exceptions (see [External URI:]https://www.pfizer.com/science/clinical-trials/trial-data-and-results for more information), Pfizer will provide access to individual de-identified\xa0participant data from Pfizer-sponsored global interventional clinical studies conducted for medicines, vaccines and medical devices (1) for indications that have been approved in the US and/or EU, or (2) in programs that have been terminated (i.e. development for all indications has been discontinued).\xa0Pfizer will also consider requests for the protocol, data dictionary, and statistical analysis plan.\xa0Data may be requested from Pfizer trials 24\xa0months after study completion.\xa0The de-identified\xa0participant data will be made available to researchers whose proposals meet the research criteria and other conditions, and for which an exception does not apply, via a secure portal. To gain access, data requestors must enter into a data access agreement with Pfizer. On 1 August 2019, PCH became part of GSK Consumer Healthcare.\n',
                    'Title: Compliance with Ethical Standards\n\n    Title: Funding\n    These studies were funded by PCH. On 1 August 2019, PCH became part of GSK Consumer Healthcare.\n\n    Title: Conflict of interest\n    Sanela Tarabar, Rina Leyva, Dongweon Song, and Kyle Matschke are employees of and may own stock/stock options in Pfizer Inc. David E. Kellstein and Mario Cruz-Rivera were employees of Pfizer Inc. at the time this research was conducted and may own stock/stock options in Pfizer Inc. Suzanne Meeves was an employee of Pfizer Inc. at the time this research was conducted. Debra Kelsh and Bradley Vince declare they have no conflicts of interest.\n\n    Title: Ethical Approval\n    All procedures performed in studies involving human participants were in accordance with the ethical standards of the Pfizer Clinical Research Unit, New Haven, CT, USA (Studies 1 and 2); WCCT Global, Costa Mesa, CA, USA, Pharmaceutical Research Associates, Salt Lake City, UT, USA, and Altasciences/Vince and Associates Clinical Research, Overland Park, KS, USA (Study 3) and with the 1964 Helsinki declaration and its later amendments or comparable ethical standards.\n\n    Title: Informed Consent\n    Informed consent was obtained from all individual participants (or parents or guardians in the adolescent study) included in the studies; informed assent was obtained from each minor subject.\n\n']
    assert p.custom_meta == {'issue-copyright-statement': '© The Author(s) 2020'}

    #Test paper functions
    assert p.full_text()[0:2730] == 'Abstract: \n\nSECTION: Introduction:\n\nA fixed-dose combination (FDC) of ibuprofen and acetaminophen has been developed that provides greater analgesic efficacy than either agent alone at the same doses without increasing the risk for adverse events.\n\nSECTION: Methods:\n\nWe report three clinical phase I studies designed to assess the pharmacokinetics (PK) of the FDC of ibuprofen/acetaminophen 250/500\xa0mg (administered as two tablets of ibuprofen 125\xa0mg/acetaminophen 250\xa0mg) in comparison with its individual components administered alone or together, and to determine the effect of food on the PK of the FDC. Two studies in healthy adults aged 18–55\xa0years used a crossover design in which subjects received a single dose of each treatment with a 2-day washout period between each. In the third study, the bioavailability of ibuprofen and acetaminophen from a single oral dose of the FDC was assessed in healthy adolescents aged 12–17\xa0years, inclusive.\n\nSECTION: Results:\n\nA total of 35 and 46 subjects were enrolled in the two adult studies, respectively, and 21 were enrolled in the adolescent study. Ibuprofen and acetaminophen in the FDC were bioequivalent to the monocomponents administered alone or together. With food, the maximum concentration (C_max) for ibuprofen and acetaminophen from the FDC was reduced by 36% and 37%, respectively, and time to C_max (i.e. t_max) was delayed. Overall drug exposure to ibuprofen or acetaminophen in the fed versus fasted states was similar. In adolescents, overall exposure to acetaminophen and ibuprofen was comparable with that in adults, with a slightly higher overall exposure to ibuprofen. Exposure to acetaminophen and ibuprofen in adolescents aged 12–14\xa0years was slightly higher versus those aged 15–17\xa0years. Adverse events were similar across all treatment groups.\n\nSECTION: Conclusions:\n\nThe FDC of ibuprofen/acetaminophen 250/500\xa0mg has a PK profile similar to its monocomponent constituents when administered separately or coadministered, indicating no drug–drug interactions and no formulation effects. Similar to previous findings for the individual components, the rates of absorption of ibuprofen and acetaminophen from the FDC were slightly delayed in the presence of food. Overall, adolescents had similar exposures to acetaminophen and ibuprofen as adults, while younger adolescents had slightly greater exposure than older adolescents, probably due to their smaller body size. The FDC was generally well tolerated.\nBody: \n\nSECTION: Key Points:\n\n\n\nSECTION: Introduction:\n\nIbuprofen and acetaminophen are among the most widely used non-prescription over-the-counter (OTC) analgesic/antipyretic drugs, both in the US and globally [1, 2]. The efficacy of these agents'
    assert p.query("absorption") == {'Match on pmcid-7067710-chunk-26': '...similar to its monocomponent constituents when administered separately or coadministered, indicating no drug–drug interactions and no formulation effects. Similar to previous findings for the individual components, the rates of absorption of ibuprofen and acetaminophen from the FDC were slightly delayed in the presence of food. Overall, adolescents had similar exposures to acetaminophen and ibuprofen...'}
    assert p.to_relational()['Title'] == 'Phase I Pharmacokinetic Study of Fixed-Dose Combinations of Ibuprofen and Acetaminophen in Healthy Adult and Adolescent Populations'
    assert p.to_relational()['Authors'] == ['Sanela Tarabar',
                                            'Debra Kelsh',
                                            'Bradley Vince',
                                            'Rina Leyva',
                                            'Dongweon Song',
                                            'Kyle Matschke',
                                            'David E. Kellstein',
                                            'Suzanne Meeves',
                                            'Mario Cruz-Rivera']
    #end 7067710------------------------------------------------------------------

    PMCID = 7067711#------------------------------------------------------------------makes sure flat abstracts work too
    email = "danielfrees247@gmail.com"

    p = paper.Paper.from_pmc(PMCID, email, download=False, suppress_warnings=True)

    assert p.title == 'Decline and diversity in Swedish seas: Environmental narratives in marine history, science and policy'
    ABSTRACT_7067711 = ""
    with open(os.path.join(path_to_testdata, "7067711_abstract.txt")) as f:
        ABSTRACT_7067711 = f.read()
    assert str(p.abstract[0]) == ABSTRACT_7067711 #makes sure the retrieved abstract is a flat string matching the abstract on PMC

    PMCID = 8460637#-----------------------------makes sure empty XMLs (XML that can't be retreived from PMC) work too. Worst case scenario
    #For now, just make sure it can be grabbed without breaking

    p = paper.Paper.from_pmc(PMCID, email, download=False, suppress_warnings=True)

                            
    return None
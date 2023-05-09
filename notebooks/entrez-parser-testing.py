import sys
sys.path.insert(0, "../../scrapemed")

import pandas as pd
import numpy as np
import re
import lxml.etree as ET
import scrapemed.scrape as scrape
import scrapemed.trees as trees
import scrapemed._clean as _clean
import scrapemed._validate as _validate
from Bio import Entrez 
from urllib.error import HTTPError

EMAIL = "danielfrees247@gmail.com"
Entrez.email = EMAIL
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

def view_record_index(records, i, verbose = False):
    record = records[i]
    print(f"----------Record #{i} Returned:-------------------\n{record}")
    try:
        p = record['body']['sec']['p']
        print(f"\nSample paragraph: {p}")
        print(f"\nParagraph items: {p.items()}")
        print(f"\nParagraph values: {p.values()}")
        if verbose:
            print(f"\n...Iterating Paragraph Attrs...\n")
            for attr in dir(p):
                if not attr.startswith("__"):
                    attr_value = getattr(p, attr)
                    if not callable(attr_value):
                        print("\nNon-Callable Attr:\n")
                        print(f"{attr}: {attr_value}")

            for attr in dir(p):
                if not attr.startswith("__"):
                    if callable(attr_value):
                        print(f"\nCallable Attr {attr}:\n")
                        try:
                            attr_value()
                        except TypeError as e:
                            print(f"{attr_value} gave Type Error: {e}")
                        except KeyError as e:
                            print(f"{attr_value} gave Key Error: {e}")
    except TypeError as e:
        pass
    except KeyError as e:
        pass
    print(f"---------------------------------------------\n")


def get_records_and_view(pmcid_list):
    #Specify creds and PMCID
    
    DB = 'pmc'
    RETTYPE = 'full'
    RETMODE = 'xml'

    #Actually fetch from PMC
    handle = Entrez.efetch(db = DB, id = pmcid_list, rettype = RETTYPE, retmode = RETMODE)
    records = Entrez.read(handle)

    for i in range(len(records)):
        view_record_index(records, i)

handle = Entrez.esearch(db="pmc", retmax=10000, term="drug")
search_record = Entrez.read(handle)
handle.close()
drug_article_sample = search_record['IdList']

dtd_list = []

#Specify creds and PMCID
EMAIL = "danielfrees247@gmail.com"
DB = 'pmc'
RETTYPE = 'full'
RETMODE = 'xml'
Entrez.email = EMAIL

#Actually fetch from PMC
pmcid_list = drug_article_sample
handle.close()

#track bad xml and http error counts
num_bad_xmls = 0
num_http_errors = 0
dtd_url_pattern = re.compile(r'"(https?://\S+)"')
for pmcid in pmcid_list:
    record = None
    match = None
    try:
        record = scrape.get_xml(pmcid = pmcid, email = EMAIL, validate = False)
        match = dtd_url_pattern.search(record.docinfo.doctype)
    except ET.XMLSyntaxError as e:
        print("Found a bad XML.")
        num_bad_xmls += 1
    except HTTPError as e:
        print("HTTP Error with Entrez servers.")
        num_http_errors += 1

    if match:
        url = match.group(1)
        dtd_list.append(url)
    else:
        print("Failed to find DTD!")

#WRITE OUT SCAN RESULTS
print(f"# of Bad XMLS: {num_bad_xmls}")
print(f"# of HTTP Errors: {num_http_errors}")
print(f"# of DTDs found: {len(dtd_list)}\n")
dtd_set = set(dtd_list)
print(f"Unique DTDs: {dtd_set}\n")
with open('data/dtd_list.txt', 'w') as f:
    f.write(f"# of DTDs found: {len(dtd_list)}\n")
    f.write(f"# of Bad XMLS: {num_bad_xmls}\n")
    f.write(f"# of HTTP Errors: {num_http_errors}\n")
    f.write(str(dtd_list))
with open('data/dtd_set.txt', 'w') as f:
    f.write(str(dtd_set))
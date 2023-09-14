# ScrapeMed
### Data Scraping for PubMed Central

![GitHub CI](https://github.com/mediboard/scrapemed/actions/workflows/test-scrapemed.yml/badge.svg)
[![codecov](https://codecov.io/gh/danielfrees/scrapemed/branch/main/graph/badge.svg?token=VZ5UO1YB93)](https://codecov.io/gh/danielfrees/scrapemed)
[![Documentation Status](https://readthedocs.org/projects/scrapemed/badge/?version=latest)](https://scrapemed.readthedocs.io/en/latest/?badge=latest)

[![HitCount](https://img.shields.io/endpoint?url=https%3A%2F%2Fhits.dwyl.com%2Fmediboard%2Fscrapemed.json%3Fcolor%3Dpink)](http://hits.dwyl.com/mediboard/scrapemed)

![PyPI](https://img.shields.io/pypi/v/scrapemed?label=pypi%20package)
![PyPI - Downloads](https://img.shields.io/pypi/dm/scrapemed)

⭐ **Used by Duke University** to power medical generative AI research.

⭐ Enables pythonic object-oriented access to a **massive amount of research data**. PMC constitutes over 14% of [The Pile](https://www.arxiv-vanity.com/papers/2101.00027/).

⭐ Natural language Paper querying and Paper embedding, powered via LangChain and ChromaDB

⭐ Easy to integrate with pandas for data science workflows

## Installation

Available on PyPI! Simply `pip install scrapemed`.

## Feature List

- Scraping API for PubMed Central (PMC) ✅
- Data Validation ✅
- Markup Language Cleaning ✅
- Processes all PMC XML into `Paper` objects ✅
- Dataset building functionality (`paperSets`) ✅
- Semantic paper vectorization with `ChromaDB` ✅
- Natural language `Paper` querying ✅
- Integration with `pandas` ✅
- `paperSet` visualization ✅
- Direct Search for Papers by PMCID on PMC ✅
- Advanced Term Search for Papers on PMC ✅

## Introduction

ScrapeMed is designed to make large-scale data science projects relying on PubMed Central (PMC) easy. The raw XML that can be downloaded from PMC is inconsistent and messy, and ScrapeMed aims to solve that problem at scale. ScrapeMed downloads, validates, cleans, and parses data from nearly all PMC articles into `Paper` objects which can then be used to build datasets (`paperSet`s), or investigated in detail for literature reviews.

Beyond the heavy-lifting performed behind the scenes  by ScrapeMed to standardize data scraped from PMC, a number of features are included to make data science and literature review work easier. A few are listed below:

- `Paper`s can be queried with natural language [`.query()`], or simply chunked and embedded for storage in a vector DB [`.vectorize()`]. `Paper`s can also be converted to pandas Series easily [`.to_relational()`] for data science workflows.

- `paperSet`s can be visualized [`.visualize()`], or converted to pandas DataFrames [`.to_relational()`]. `paperSet`s can be generated not only via a list of PMCIDs, but also via a search term using PMC [advanced search](https://www.ncbi.nlm.nih.gov/pmc/advanced) [`.from_search()`].

- *Useful for advanced users:* `TextSection`s and `TextParagraph`s found within `.abstract` and `.body` attributes of `Paper` objects contain not only text [`.text`], but also text with attached reference data [`.text_with_refs`]. Reference data includes tables, figures, and citations. These are processed into DataFrames and data dicts and can be found within the `.ref_map` attribute of a `Paper` object. Simply decode references based on their MHTML index. ie. an MHTML tag of "MHTML::dataref::14" found in a `TextSection` of paper `p` corresponds to the table, fig, or citation at `p.ref_map[14]`.

## Documentation

The [docs](https://scrapemed.readthedocs.io/en/latest/) are hosted on Read The Docs!

## Sponsorship

***Package sponsored by Daceflow.ai!***

If you'd like to sponsor a feature or donate to the project, reach out to me at danielfrees@g.ucla.edu.

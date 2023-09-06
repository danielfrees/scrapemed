# ScrapeMed
### Data Scraping for PubMed Central

![GitHub CI](https://github.com/mediboard/scrapemed/actions/workflows/test-scrapemed.yml/badge.svg)

[![HitCount](https://img.shields.io/endpoint?url=https%3A%2F%2Fhits.dwyl.com%2Fmediboard%2Fscrapemed.json%3Fcolor%3Dpink)](http://hits.dwyl.com/mediboard/scrapemed)

[![codecov](https://codecov.io/gh/danielfrees/scrapemed/branch/main/graph/badge.svg?token=VZ5UO1YB93)](https://codecov.io/gh/danielfrees/scrapemed)

⭐ **Used by Duke University** to power medical generative AI research.

⭐ Enables pythonic object-oriented access to a **massive amount of research data**. PMC constitutes over 14% of [The Pile](https://www.arxiv-vanity.com/papers/2101.00027/).

⭐ Natural language Paper querying and Paper embedding, powered via LangChain and ChromaDB

### Shoutout: 

Package sponsored by Daceflow.ai!

## Feature List

- Scraping API for PubMed Central (PMC) ✅
- Full Adanced Term Search for Papers on PMC ✅
- Direct Search for Papers by PMCID on PMC ✅
- Data Validation ✅
- Markup Language Cleaning ✅
- Process PMC XMl into Paper objects ✅
- Dataset building functionality (paperSets) ✅
- Integration with pandas for easy use in data science applications ✅
- Semantic paper vectorization with ChromaDB ✅
- Natural language paper querying ✅
- Integration with pandas ✅
- paperSet visualization ✅


## Developer Usage

*License: MIT*

Feel free to fork and continue work on the ScrapeMed package, it is licensed under the MIT license to promote collaboration, extension, and inheritance. 

Make sure to create a conda environment and install the necessary requirements before developing this package. 

ie: `$ conda create --name myenv --file requirements.txt`

Add a `.env` file in your base scrapemed directory with PMC_EMAIL=youremail@example.com. This is necessary for several of the test scripts and may be useful for your development in general. 

You will need to install clang++ for chromadb and the Paper vectorization to work. You also need to make sure you have python 3.11 installed and active in your dev environment.

***Now an overview of the package structure:***

Under `notebooks` you can find some example work using the scrapemed modules, which may provide some insight into usage possibilities. 

Under `notebooks/data` you will find some example downloaded date (XML from Pubmed Central). It is recommended that any time you download data while working out of the notebooks, it should go here. Downloads will also go here by default when passing `download=True` to the scrapemed module functions which allow you to do so.

Under `scrapemed/tests` you will find several python scripts which can be run using pytest. If you also clone the `.github/workflows/test-scrapemed.yml`, these tests will be automatically run on any PR/ push to your github repo. Under `scrapemed/test/testdata` are some XML data crafted for the purpose of testing scrapemed. This data is necessary to run the testing scripts.

Each of the scrapemed python modules has a docstring at the top describing its general purpose and usage. All functions should also have descriptive docstrings and descriptions of input/output. Please contact me if any documentation is unclear. Full documentation is on its way.

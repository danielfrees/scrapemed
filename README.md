# scrapemed
## Open-Source Scraper for PubMed Central

![GitHub CI](https://github.com/mediboard/scrapemed/.github/workflows/test-scrapemed.yml/badge.svg)

Licensed under the MIT license.

<TODO: Create package art in Illustrator>

## Developer Usage

Feel free to fork and continue work on this python package, it is licensed under the MIT license to promote collaboration, extension, and inheritance of the scrapemed package.

Make sure to create a conda environment and install the necessary requirements before developing this package. 

ie: `$ conda create --name myenv --file requirements.txt`

***Now an overview of the package structure:***

Under `notebooks` you can find some example work using the scrapemed modules, which may provide some insight into usage possibilities. 

Under `notebooks/data` you will find some example downloaded date (XML from Pubmed Central). It is recommended that any time you download data while working out of the notebooks, it go here. Downloads will also go here by default when passing `download=True` to the scrapemed module functions which allow you to do so.

Under `scrapemed/data` you will find IMPORTANT data which affects module functionality. The `supported_tag_list.txt` contains all tags currently supported by the scrapemed module. The `supported_xml_html.csv` file contains all tag,attr,value combos currently supported by the scrapemed module, for tags which contain one or more attributes. The `supported_xml_html.json` file contains the same information in a json/dict format. The `tag_descriptions.csv` file contains descriptions of all supported tag types (TODO).

Under `scrapemed/tests` you will find several python scripts which can be run using pytest. If you also clone the `nlp/.github/workflows/test-scrapemed.yml`, these tests will be automatically run on any PR/ push to your github repo. Under `scrapemed/test/testdata` are some XML data crafted for the purpose of testing scrapemed. This data is necessary to run the testing scripts.

Each of the scrapemed python modules has a docstring at the top describing its general purpose and usage. All functions should also have descriptive docstrings and descriptions of input/output. Please contact me if any documentation is unclear.


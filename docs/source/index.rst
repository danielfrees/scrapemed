.. scrapemed documentation master file, created by
   sphinx-quickstart on Wed Sep 13 10:39:11 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to scrapemed's documentation!
=====================================

ScrapeMed is a powerful, easy to use, data scraping tool for PubMed Central (PMC) data.
Most users will only need to interact with ``Paper`` and ``paperSet`` objects to build
their PMC datasets, but a complete documentation of ScrapeMed's modules and functions can be found here.

Quick Start
===========

Quick start placeholder.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   modules

Developer Usage
===============

*License: MIT*

Feel free to fork and continue work on the ScrapeMed package, it is licensed under the MIT license to promote collaboration, extension, and inheritance.

Make sure to create a conda environment and install the necessary requirements before developing this package.

ie: ``$ conda create --name myenv --file requirements.txt``

Add a ``.env`` file in your base scrapemed directory with a variable defined as follows: ``PMC_EMAIL=youremail@example.com``.
This is necessary for several of the test scripts and may be useful for your development in general.

You will need to install clang++ for ``chromadb` and ``Paper`` vectorization to work. You also need to make sure you have ``python 3.10.2``
or later installed and active in your dev environment.

You'll also want to ``pip install pre-commit`` and ``pre-commit install`` so that
the ``.pre-commit-config.yaml`` file can do its magic in making sure your commits
follow PEP8 style guidelines (with line length increased to 88), and that your commits
do not break the testing framework with pytest.

**Now an overview of the package structure:**

Under ``examples`` you can find some example work using the scrapemed modules, which may provide some insight into usage possibilities.

Under ``examples/data`` you will find some example downloaded data (XML from Pubmed Central). It is recommended that any time you d
ownload data while working out of the notebooks, it should go here. Downloads will also go here by default when passing ``download=True``
to the scrapemed module functions which allow you to do so.

Under ``scrapemed/tests`` you will find several python scripts which can be run using pytest. If you also clone and update the
``.github/workflows/test-scrapemed.yml`` for your forked repo, these tests will be automatically run on ``git push``. Under ``scrapemed/test/testdata``
are some XML data crafted for the purpose of testing scrapemed. This data is necessary to run some of the testing scripts.

Each of the scrapemed python modules has a docstring at the top describing its general purpose and usage. All functions should also
have descriptive docstrings and descriptions of input/output. Please contact me if any documentation is unclear.


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


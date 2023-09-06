from setuptools import setup, find_packages
import os

_SCRAPEMED_REQS = [
    'biopython>=1.78',
    'graphviz>=0.20.1',
    'lxml>=4.9.2',
    'pandas>=1.5.2',
    'requests-html>=0.10.0',
    'sqlalchemy>=1.4.39',
    'beautifulsoup4>=4.11',
    'html5lib>=1.1',
    'jinja2',
    'python-dotenv',
    'chromadb',
    'langchain',
    'uuid',
    'matplotlib',
    'wordcloud',
    'charset-normalizer>=3.1.0'
]

_INSTALL_REQUIRES = _SCRAPEMED_REQS
_TEST_REQS = _SCRAPEMED_REQS

setup(
    name='scrapemed',
    version='1.0.4',
    description='ScrapeMed: Data Scraping for PubMed Central.',
    author='Daniel Frees',
    author_email='danielfrees@g.ucla.edu',
    url='https://github.com/mediboard/nlp/scrapemed',
    packages=[
        'scrapemed',
    ],
    package_dir={
        'scrapemed': 'scrapemed',
    },
    package_data={
        'scrapemed': [os.path.join('data', 'DTDs', '*')],
    },
    install_requires=_INSTALL_REQUIRES,
    tests_require=_TEST_REQS,
    test_suite="tests",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.11',
    ],
)
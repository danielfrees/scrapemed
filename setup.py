from setuptools import setup, find_packages
import os

def _read_reqs(relpath):
    fullpath = os.path.join(os.path.dirname(__file__), relpath)
    with open(fullpath) as f:
        return [s.strip() for s in f.readlines()
                if (s.strip() and not s.startswith("#"))]

_SCRAPEMED_REQS = _read_reqs("requirements.txt")
_DEPENDENCY_LINKS = [l for l in _SCRAPEMED_REQS if "://" in l]
_INSTALL_REQUIRES = [l for l in _SCRAPEMED_REQS if "://" not in l]
_TEST_REQS = _read_reqs("requirements.txt")

setup(
    name='scrapemed',
    version='1.0.0',
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
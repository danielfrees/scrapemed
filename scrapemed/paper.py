"""
The scrapemed "paper" module is intended as the primary point of contact for 
scrapemed end users.

Paper objects are defined here, as well end-user functionality for scraping data
from PubMed Central without stressing about the details.
"""

import pprint
from sqlalchemy import create_engine, ForeignKey, Column, String, Integer, CHAR, Boolean, DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
import scrapemed._parse as parse
import scrapemed.scrape as scrape
from scrapemed._parse import TextSection
from scrapemed.utils import basicBiMap
import lxml.etree as ET
import pandas as pd

#--------------------PAPER OBJECT SCHEMA-------------------------------------------
#Deriving from SQLalchemy base so this can be SQL Alchemy friendly when I scale to connection with the backend
Base = declarative_base()

class Paper(Base):
    __tablename__ = "Papers"

    def __init__(self, paper_dict:dict)->None:
        """
        Initialize a paper with a dictionary of paper information (ie. from parse.generate_paper_dict)
        """
        self.title = paper_dict['Title']
        self.authors = paper_dict['Authors']
        self.non_author_contributors = paper_dict['Non-Author Contributors']
        self.abstract = paper_dict['Abstract']
        self.body = paper_dict['Body']
        self.journal_id = paper_dict['Journal ID']
        self.journal_title = paper_dict['Journal Title']
        self.issn = paper_dict['ISSN']
        self.publisher_name = paper_dict['Publisher Name']
        self.publisher_location = paper_dict['Publisher Location']
        self.article_id = paper_dict['Article ID']
        self.article_types = paper_dict['Article Types']
        self.article_categories = paper_dict['Article Categories']
        self.published_date = paper_dict['Published Date']
        self.volume = paper_dict['Volume']
        self.issue = paper_dict['Issue']
        self.fpage = paper_dict['First Page']
        self.lpage = paper_dict['Last Page']
        self.permissions = paper_dict['Permissions']
        if self.permissions:
            self.copyright = self.permissions["Copyright Statement"] 
            self.license = self.permissions["License Type"]
        else:
            self.copyright = None
            self.license = None
        self.funding = paper_dict['Funding']
        self.footnote = paper_dict['Footnote']
        self.acknowledgements = paper_dict['Acknowledgements']
        self.notes = paper_dict['Notes']
        self.custom_meta = paper_dict['Custom Meta']
        self.ref_map = paper_dict['Ref Map']
        self._ref_map_with_tags = paper_dict['Ref Map With Tags']
        self.citations = paper_dict['Citations']
        self.tables = paper_dict['Tables']
        self.figures = paper_dict['Figures']

        self.data_dict = parse.define_data_dict()

    @classmethod 
    def from_pmc(cls, pmcid:int, email:str, download:bool=False, validate:bool=True, verbose:bool=False):
        """
        Generate a Paper from a pmcid. Specify your email for auth.
        """
        paper_dict = parse.paper_dict_from_pmc(pmcid=pmcid, email=email, download=download, validate=validate, verbose=verbose)
        return cls(paper_dict)

    @classmethod
    def from_xml(cls, root:ET.Element, verbose:bool=False):
        """
        Generate a Paper straight from PMC XML.
        """
        paper_dict = parse.generate_paper_dict(root)
        return cls(paper_dict)


        
    def __str__(self):
        s = ""
        #TODO: Add Important Metadata

        #Append all text from abstract PaperSections
        for sec in self.abstract:
            s += str(sec)
        #Append all text from body PaperSections
        for sec in self.body:
            s += str(sec)
        return s
    
    def __eq__(self, other):
        """
        For two Paper objects to be equal, they must share the same DOI and have the same date of last update.
        """
        return self.doi == other.doi and self.last_updated == other.last_updated

    def to_relational(self)->pd.Series:
        """
        Generates a pandas Series representation of the paper. Some data will be lost, 
        but most useful text data and metadata will be retained in the relational shape.
        """
        #TODO
        return None

    def vectorize(self, embedding_model, chunk_size:int):
        """
        Generates a lightweight vector database representation of the paper,
        stored in paper.embedded.
        """
        self.embedded = None

        return None
    
    def query(self, query:str, n_results:int)->str:
        """
        Query the paper with natural language questions. 
            Input:
            [query] - string question
            [n_results] - number of most semantically similar paper sections to retrieve
            Output:
            Paper chunks most semantically similar to the input quesiton.
        """
    
    #paper identifiers, DOI should be a completely unique string and is PK
    doi = Column("doi", String, primary_key=True)
    title = Column("title", String)
    pmcid = Column("pmcid", String)  #for articles in PMC
    authors = Column("authors", String)  #list of authors of paper, could potentially blow out into multiple columns later
    journal = Column("journal", String)

    #last updated date (retrieved from PMC to track paper updates)
    last_updated = Column("last_update", DateTime)

    #xml text for the abstract & body separately (each sub-sectioned into a list of strings)
    abstract = Column("abstract", String) 
    body = Column("body", String)

    #xml text for references
    references = Column("references", String)

#--------------------END PAPER OBJECT SCHEMA-------------------------------------------

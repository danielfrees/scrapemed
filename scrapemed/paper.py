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
from scrapemed._parse import TextSection
from scrapemed.utils import basicBiMap

#--------------------PAPER OBJECT SCHEMA-------------------------------------------
#Deriving from SQLalchemy base so this can be SQL Alchemy friendly when I scale to connection with the backend
Base = declarative_base()

class Paper(Base):
    __tablename__ = "Papers"

    def __init__(self, pmcid:int, email:str, download:bool=False, validate:bool=True, verbose:bool=False):
        paper_dict = parse.generate_paper_dict(pmcid=pmcid, email=email, download=download, validate=validate, verbose=verbose)
        
        #TODO: add more member assignments
        self.title = paper_dict['Title']
        self.authors = paper_dict['Authors']
        self.abstract = paper_dict['Abstract']
        self.body = paper_dict['Body']
        self.xref_map = paper_dict['XRef_Map']
        self.table_map = paper_dict['Table_Map']
        self.fig_map = paper_dict['Fig_Map']
        
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

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
        
        self.title = paper_dict['Title']
        self.authors = paper_dict['Authors']
        self.non_author_contributors = paper_dict['Non-author Contributors']
        self.abstract = paper_dict['Abstract']
        self.body = paper_dict['Body']
        self.ref_map = paper_dict['Ref Map']
        self.journal_id = paper_dict['Journal ID']
        self.journal_title = paper_dict['Journal Title']
        self.issn = paper_dict['ISSN']
        self.publisher_name = paper_dict['Publisher Name']
        self.publisher_location = paper_dict['Publisher Location']
        self.article_meta = paper_dict['Article Meta']
        self.article_id = paper_dict['Article ID']
        self.article_type = paper_dict['Article Type']
        self.article_categories = paper_dict['Article Categories']
        self.subject = paper_dict['Subject']
        self.institution = paper_dict['Institution']
        self.institution_id = paper_dict['Institution ID']
        self.published_date = paper_dict['Published Date']
        self.volume = paper_dict['Volume']
        self.issue = paper_dict['Issue']
        self.permissions = paper_dict['Permissions']
        self.copyright_statement = paper_dict['Copyright Statement']
        self.license = paper_dict['License']
        self.funding_group = paper_dict['Funding Group']
        self.award_group = paper_dict['Award Group']
        self.funding_source = paper_dict['Funding Source']
        self.footnote = paper_dict['Footnote']
        self.acknowledgements = paper_dict['Acknowledgements']
        self.notes = paper_dict['Notes']
        self.reference_list = paper_dict['Reference List']

        
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

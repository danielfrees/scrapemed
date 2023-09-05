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
import datetime

#--------------------PAPER OBJECT SCHEMA-------------------------------------------
#Deriving from SQLalchemy base so this can be SQL Alchemy friendly when I scale to connection with the backend
Base = declarative_base()

class Paper(Base):
    __tablename__ = "Papers"

    def __init__(self, paper_dict:dict)->None:
        """
        Initialize a paper with a dictionary of paper information (ie. from parse.generate_paper_dict)
        """
        if not paper_dict:
            self.has_data = False
            return None
        else: 
            self.has_data = True
        
        #capture current time as time of last update. Note that this date may not be synced with PMC paper updates if using
        #initialization via Paper.from_xml. Use Paper.from_pmc to update papers directly via PMC
        current_datetime = datetime.datetime.now()
        current_year = current_datetime.year
        current_month = current_datetime.month
        current_day = current_datetime.day
        self.last_updated = (current_month, current_day, current_year)

        #read in the Paper data from the parsed paper_dict
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
    def from_pmc(cls, pmcid:int, email:str, download:bool=False, validate:bool=True, verbose:bool=False, suppress_warnings:bool=False, suppress_errors:bool=False):
        """
        Generate a Paper from a pmcid. Specify your email for auth.
        
        [pmcid] - Unique PMCID for the article to parse.
        [email] - Provide your email address for authentication with PMC
        [download] - Whether or not to download the XML retreived from PMC
        [validate] - Whether or not to validate the XML from PMC against NLM articleset 2.0 DTD (HIGHLY RECOMMENDED)
        [verbose] - Whether or not to have verbose output for testing
        [suppress_warnings] - Whether to suppress warnings while parsing XML. 
            Note: Warnings are frequent, because of the variable nature of PMC XML data. 
            Recommended to suppress when parsing many XMLs at once.
        [suppress_errors] - Return None on failed XML parsing, instead of raising an error.
        """
        paper_dict = parse.paper_dict_from_pmc(pmcid=pmcid, email=email, download=download, validate=validate, verbose=verbose, suppress_warnings=suppress_warnings, suppress_errors=suppress_errors)
        return cls(paper_dict)

    @classmethod
    def from_xml(cls, root:ET.Element, verbose:bool=False, suppress_warnings:bool=False, suppress_errors:bool=False):
        """
        Generate a Paper straight from PMC XML.

        [root] - ET.Element of the root of the PMC XML
        [verbose] - Whether or not to have verbose output for testing
        [suppress_warnings] - Whether to suppress warnings while parsing XML. 
            Note: Warnings are frequent, because of the variable nature of PMC XML data. 
            Recommended to suppress when parsing many XMLs at once.
        [suppress_errors] - Return None on failed XML parsing, instead of raising an error.
        """
        paper_dict = parse.generate_paper_dict(root, verbose=verbose, suppress_warnings=suppress_warnings, suppress_errors=suppress_errors)
        return cls(paper_dict)
    
    def print_abstract(self)->str:
        """
        Prints and returns a string of the abstract.
        """
        s = self.abstract_as_str()
        print(s)
        return s
    
    def abstract_as_str(self)->str:
        s = ""
        if self.abstract:
            for sec in self.abstract:
                s += "\n"
                s += str(sec)
        return s
    
    def print_body(self)->str:
        """
        Prints and returns a string of the body.
        """
        s = self.body_as_str()
        print(s)
        return s
    
    def body_as_str(self)->str:
        """
        Returns a string of the body.
        """
        s = ""
        if self.body:
            for sec in self.body:
                s += "\n"
                s += str(sec)
        return s
    
    def __bool__(self):
        """
        The truth value of a Paper object depends on whether it parsed succesfully during initialization.
        """
        return self.has_data

    def __str__(self):
        s = ""
        s += f"\nPMCID: {self.article_id['pmc']}\n"
        s += f"Title: {self.title}\n"
        #Append all text from abstract PaperSections
        s+= f"\nAbstract:\n"
        if self.abstract:
            for sec in self.abstract:
                s += str(sec)
        #Append all text from body PaperSections
        s+= f"\nBody:\n"
        if self.body:
            for sec in self.body:
                s += str(sec)
        return s
    
    def __eq__(self, other):
        """
        For two Paper objects to be equal, they must share the same PMCID and have the same date of last update.

        Two Papers may be exactly equal but be downlaoded or parsed on different dates. These will not evaluate to equal. 
        Simply compare Paper1.article_id['pmc'] and Paper2.article_id['pmc'] if that is your desired behavior.

        Note also that articles which are not open access on PMC may not have a PMCID, and a unique comparison will need to be made for these
        to check equality. 
        """
        if not self:
            return False
        return self.article_id['pmc'] == other.article_id['pmc'] and self.last_updated == other.last_updated

    def to_relational(self)->pd.Series:
        """
        Generates a pandas Series representation of the paper. Some data will be lost, 
        but most useful text data and metadata will be retained in the relational shape.
        """

        data = {
            'Last_Updated': self.last_updated,
            'Title': self.title,
            'Authors': self._extract_names(self.authors) if isinstance(self.authors, pd.DataFrame) else None,
            'Non_Author_Contributors': self._extract_names(self.non_author_contributors) if isinstance(self.non_author_contributors, pd.DataFrame) else None,
            'Abstract': self.abstract_as_str(),
            'Body': self.body_as_str(),
            'Journal_ID': self.journal_id,
            'Journal_Title': self.journal_title,
            'ISSN': self.issn,
            'Publisher_Name': self.publisher_name,
            'Publisher_Location': self.publisher_location,
            'Article_ID': self.article_id,
            'Article_Types': self.article_types,
            'Article_Categories': self.article_categories,
            'Published_Date': self._serialize_dict(self.published_date) if isinstance(self.published_date, dict) else None,
            'Volume': self.volume,
            'Issue': self.issue,
            'First_Page': self.fpage,
            'Last_Page': self.lpage,
            'Copyright': self.copyright,
            'License': self.license,
            'Funding': self.funding,
            'Footnote': self.footnote,
            'Acknowledgements': self.acknowledgements,
            'Notes': self.notes,
            'Custom_Meta': self.custom_meta,
            'Ref_Map': self.ref_map,
            'Citations': [self._serialize_dict(c) for c in self.citations if isinstance(c, dict)],
            'Tables': [self._serialize_df(t) for t in self.tables if isinstance(t, (pd.io.formats.style.Styler, pd.DataFrame))],
            'Figures': self.figures
        }
        return pd.Series(data)
    
    #---------------Helper functions for to_relational---------------------
    def _extract_names(self, df):
        return df.apply(lambda row: f"{row['First_Name']} {row['Last_Name']}", axis=1).tolist()

    def _serialize_dict(self, data_dict):
        return "; ".join([f"{key}: {value}" for key, value in data_dict.items()])

    def _serialize_df(self, df):
        return df.to_html()
    #---------------End Helper functions for to_relational--------------------- 

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

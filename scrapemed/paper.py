"""
The scrapemed "paper" module is intended as the primary point of contact for 
scrapemed end users.

Paper objects are defined here, as well end-user functionality for scraping data
from PubMed Central without stressing about the details.
"""

import pprint
import scrapemed._parse as parse
import scrapemed.scrape as scrape
from scrapemed._parse import TextSection
from scrapemed.utils import basicBiMap
import lxml.etree as ET
import pandas as pd
import datetime
import chromadb
from langchain.text_splitter import CharacterTextSplitter
from typing import Union, List, Dict
from difflib import SequenceMatcher
import uuid
import re
import warnings
from urllib.error import HTTPError
import time

class emptyTextWarning(Warning):
    """
    Warned when trying to perform a text operation on a Paper which has no text.
    """
    pass

class pubmedHTTPError(Warning):
    """
    Warned when unable to retrieve a PMC XML repeatedly. Can occasionally happen on PMC due to traffic.
    """

#--------------------PAPER OBJECT SCHEMA-------------------------------------------
class Paper():
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
        self.pmcid = paper_dict['PMCID']
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

        self.vector_collection = None

        return None

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
        NUM_TRIES = 3
        paper_dict = None
        for i in range(NUM_TRIES):
            try:
                paper_dict = parse.paper_dict_from_pmc(pmcid=pmcid, email=email, download=download, validate=validate, verbose=verbose, suppress_warnings=suppress_warnings, suppress_errors=suppress_errors)
            except HTTPError:
                time.sleep(5)
        if not paper_dict:
            warnings.warn("Unable to retrieve PMCID {pmcid} from PMC. Try again later, may be due to HTTP traffic.", pubmedHTTPError)
            return False
        return cls(paper_dict)

    @classmethod
    def from_xml(cls, pmcid:int, root:ET.Element, verbose:bool=False, suppress_warnings:bool=False, suppress_errors:bool=False):
        """
        Generate a Paper straight from PMC XML.

        [pmcid] - PMCID for the XML. 
                This is not a mistake! 
                Super important to have a trustworthy PMCID. 
                Provide manually when uploading XML manually.
        [root] - ET.Element of the root of the PMC XML
        [verbose] - Whether or not to have verbose output for testing
        [suppress_warnings] - Whether to suppress warnings while parsing XML. 
            Note: Warnings are frequent, because of the variable nature of PMC XML data. 
            Recommended to suppress when parsing many XMLs at once.
        [suppress_errors] - Return None on failed XML parsing, instead of raising an error.
        """
        paper_dict = parse.generate_paper_dict(pmcid, root, verbose=verbose, suppress_warnings=suppress_warnings, suppress_errors=suppress_errors)
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
    
    def full_text(self, print_text:bool = False):
        """
        Return the full abstract and/or body text string of this Paper. Optionally print.
        """
        s = ""
        if self.abstract:
            s += "Abstract: \n"
            s += self.abstract_as_str()
        if self.body:
            s += "Body: \n"
            s += self.body_as_str()

        if print_text:
            print(s)
        return s

    def __str__(self):
        s = ""
        s += f"\nPMCID: {self.pmcid}\n"
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
        Simply compare Paper1.pmcid and Paper2.pmcid if that is your desired behavior.

        Note also that articles which are not open access on PMC may not have a PMCID, and a unique comparison will need to be made for these.
        However, most papers downloaded via ScrapeMed should have a PMCID.
        """
        if not self:
            return False
        return self.pmcid == other.pmcid and self.last_updated == other.last_updated

    def to_relational(self)->pd.Series:
        """
        Generates a pandas Series representation of the paper. Some data will be lost, 
        but most useful text data and metadata will be retained in the relational shape.
        """

        data = {
            'PMCID': self.pmcid,
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

    def vectorize(self, chunk_size:int = 100, chunk_overlap:int = 20, refresh:bool=False):
        """
        Generates an in-memory vector database representation of the paper,
        stored in paper.vector_collection. (Abstract and body only)

        Input:
        [chunk_size] - approximate chunk size to split paper into (len)
        [chunk_overlap] - approximate desired chunk overlap (len)
        [refresh] - Whether or not to clear and re-vectorize the paper (ie. with new settings)
        """
        if not refresh and self.vector_collection:
            print("Paper already vectorized! To re-vectorize with new settings, pass refresh=True.")
            return None
        
        print("Vectorizing Paper (This may take a little while)...")
        if len(self.full_text()) == 0:
            warnings.warn("Attempted to vectorize a Paper with no text. Aborting.", emptyTextWarning)
            return None
        
        #Set up an in-memory chromadb collection for this paper
        client = chromadb.Client()
        try:
            self.vector_collection = client.get_or_create_collection(f"Paper-PMCID-{self.pmcid}")
        except:
            self.vector_collection = client.get_or_create_collection(f"Paper-Random-UUID-{uuid.uuid4()}")

        #setup chunk model
        chunk_model = CharacterTextSplitter(
            separator="\\n\\n|\\n|\\.|\\s", 
            is_separator_regex=True, 
            chunk_size = chunk_size,
            chunk_overlap = chunk_overlap,
            length_function = len,
            keep_separator = True)
    
        #chunk the text, add metadata for the PMCID each chunk originates from, add unique chunk ids
        p_chunks = chunk_model.split_text(self.full_text())
        p_metadatas = [{"pmcid": self.pmcid}] * len(p_chunks)
        try:
            pmcid = self.pmcid
        except:
            pmcid = uuid.uuid4()
        p_ids = [self._generate_chunk_id(pmcid, i) for i in range(len(p_chunks))]

        #upload the chunked texts into the vector collection
        self.vector_collection.add(
            documents = p_chunks,
            metadatas = p_metadatas,
            ids = p_ids
        )

        print("Done Vectorizing Paper! Natural language query with Paper.query() now available.")
        return None
    
    #-----------------helper funcs for self.vectorize-----------------
    def _generate_chunk_id(self, pmcid:str, index:Union[int,str]):
        """
        Generate id for a PMC text chunk, using pmcid and index of the chunk.
        The chunk indices should be unique. Recommended to use indexes from the result
        of chunk model. 
        """
        return f"pmcid-{pmcid}-chunk-{str(index)}"

    def _get_chunk_index_from_chunk_id(self, chunk_id:str)->str:
        """
        Given a PMCID Chunk ID, in the format generated by _generate_pmcid_chunk_id,
        gather the index of the chunk.
        """
        pattern = re.compile(r"chunk-(\d+)")  # Compile the regex pattern
        match = pattern.search(chunk_id)
        index = None
        if match:
            index = match.group(1)
        return index    

    def _get_pmcid_from_chunk_id(self, chunk_id:str)->str:
        """
        Given a PMCID Chunk ID, in the format generated by _generate_pmcid_chunk_id,
        gather the PMCID of the chunk.
        """
        pattern = re.compile(r"pmcid-(\d+)")  # Compile the regex pattern
        match = pattern.search(chunk_id)
        pmcid = None
        if match:
            pmcid = match.group(1)
        return pmcid    
    #-----------------end helper funcs for self.vectorize-----------------

    def query(self, query:str, n_results:int =1, n_before:int = 2, n_after:int = 2)->Dict[str,str]:
        """
        Query the paper with natural language questions. 
            Input:
            [query] - string question
            [n_results] - number of most semantically similar paper sections to retrieve
            [n_before] - int, how many chunks before the match to include in combined output
            [n_after] - int, how many chunks after the match to include in combined output

            Output:
            Dict with key(s) = most semantically similar result chunk(s), and value(s) = Paper text(s) 
            around  the most semantically similar result chunk(s). Text length determined by 
            the chunk size used in self.vectorize() and n_before and n_after.
        """

        result = self.expanded_query(
            query=query,
            n_results = n_results,
            n_before = n_before, 
            n_after = n_after
            )
        
        return result
        
    #-----------------helper funcs for self.query----------------------
    def expanded_query(self, query:str, n_results:int=1, n_before:int = 2, n_after:int = 2)->Dict[str,str]:
        """
        Query function that matches natural language query with vectorized Paper.
        [query] - str, natural language query for paper
        [n_before] - int, how many chunks before the match to include in combined output
        [n_after] - int, how many chunks after the match to include in combined output
        """
        #if the paper has not already been vectorized, vectorize
        if not self.vector_collection:
            self.vectorize()
        #if vectorization fails, abort
        if not self.vector_collection:
            return None
        
        result = self.vector_collection.query(
            query_texts=[query],
            include=["documents"], 
            n_results=n_results)

        expanded_results = {}
        for id in result['ids'][0]:
            chunk_index = self._get_chunk_index_from_chunk_id(id)
            pmcid = self._get_pmcid_from_chunk_id(id)
            #get the texts before and after the result chunk
            expanded_ids = []
            for i in range(1, n_before+1):
                expanded_ids.append(self._generate_chunk_id(pmcid, int(chunk_index) - i))
            expanded_ids.append(id)
            for i in range(1, n_after+1):
                expanded_ids.append(self._generate_chunk_id(pmcid, int(chunk_index) + i))

            expanded_results[f"Match on {id}"] = self.vector_collection.get(
                    ids=expanded_ids,
                )['documents']

        cleaned_results = {}
        #append docs together two at a time, removing overlap
        for match, docs in expanded_results.items():
            combined_result = ""
            #combined docs together
            if len(docs) == 0:
                combined_result = None
            elif len(docs) == 1:
                combined_result = docs[0]
            else:
                #combine first two docs, removing overlap, to start the combined result
                substring_match = SequenceMatcher(None, docs[0], docs[1]).find_longest_match(0, len(docs[0]), 0, len(docs[1]))
                combined_docs = docs[0][:substring_match.a]+docs[1][substring_match.b:]
                combined_result += combined_docs
                #eat these first two docs
                if len(docs) >= 3:
                    docs = docs[2:]
                else:
                    docs = []
                #continue eating the rest one by one
                while len(docs) >= 1:
                    substring_match = SequenceMatcher(None, combined_result, docs[0]).find_longest_match(0, len(combined_result), 0, len(docs[0]))
                    combined_result = combined_result[:substring_match.a]+docs[0][substring_match.b:]
                    #eat the processed doc
                    if len(docs) >=2:
                        docs = docs[1:]
                    else:
                        docs = []
                    
                cleaned_results[match] = "..." + combined_result + "..."
        
        return cleaned_results
#--------------------END PAPER OBJECT SCHEMA-------------------------------------------

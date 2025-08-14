from helpers.llm import create_llm

from typing import Literal
from Bio import Entrez
import requests
from xml.etree import ElementTree as ET
from langchain_core.prompts import ChatPromptTemplate

class PubmedAPI():
  def __init__(self, email : str, debug : bool = False):
    self.email = email
    Entrez.email = email
    
    self.helper_agent = create_llm()
    self.debug = debug
    
  
  def search(self, user_query : str, number_to_retrieve : int, mode : Literal["abstract", "full"] = "abstract") -> list[dict[str, str]]:
    """searches PubMed and retrieves relevant text to answer user query"""
    
    #rephrased_user_query = self._rephrase_user_query(user_query)
    rephrased_user_query = user_query
    
    if mode == "abstract":
      pmids_and_text = self._fetch_abstracts(rephrased_user_query, number_to_retrieve)
      
    elif mode == "full":
      pmids_and_text = self._fetch_fulltext(rephrased_user_query, number_to_retrieve)
      
    else:
      raise ValueError(f'In search, mode with value {mode} is invalid, must be "abstract" or "full"')
    
    if not pmids_and_text:
      raise ValueError(f"In search, expected pmid_and_text to have value but it is None")
    
    system_prompt = """
      You are a professional decision maker given a set of pmids and texts. Please determine which pmids and their associated text are relevant to 
      the user query at hand.
      
      Your response must be **strictly JSON** following this schema:
        {{"pmids": ["PMID1", "PMID2", ...]}}
        
      Thank you and do your best!
      """

    human_prompt = "The user query is: {user_query}\n the pmids and text is {pmids_and_text}"
    
    prompt = ChatPromptTemplate.from_messages([
      ("system", system_prompt),
      ("human", human_prompt)
    ])
    
    llm_chain = prompt | self.helper_agent
    
    kept_pmids = llm_chain.invoke({"user_query": user_query, "pmids_and_text": pmids_and_text}).content
    if self.debug:
      print("=" * 30)
      print(f"In search, kept_pmids.content: {kept_pmids}")
      print("=" * 30)
    
    filtered_pmid_text_pairs = [pair for pair in pmids_and_text if pair["pmid"] in kept_pmids]
    return filtered_pmid_text_pairs
  
  
  def _fetch_abstracts(self, user_query : str, number_to_retrieve : int) -> list[dict[str, str]]:
    """fetches abstracts from pubmed using Entrez"""
    
    if (number_to_retrieve > 15):
      raise ValueError(f'number_to_retrieve with value {number_to_retrieve} is quite high, 15 is reasonable limit to maintain context.')
    
    pmids = self._fetch_pmids(user_query, number_to_retrieve)
    
    pmid_and_abstracts = []
    for pmid in pmids:
      abstract_handle = Entrez.efetch(db="pubmed", id=pmid, rettype="abstract", retmode="xml")
      xml_data = abstract_handle.read()
      root = ET.fromstring(xml_data)
      for abstract_part in root.findall(".//Abstract"):
        pmid_and_abstracts.append({"pmid": pmid, "abstract": self._get_element_text(abstract_part)})
    
    if self.debug:
      print("=" * 30)
      print(pmid_and_abstracts)
      print("=" * 30)
      
    return pmid_and_abstracts
  
  def _get_element_text(self, elem):
    """Recursively extract all text from an ElementTree element."""
    text_parts = []
    if elem.text:
        text_parts.append(elem.text)
    for child in elem:
        text_parts.append(self._get_element_text(child))
        if child.tail:
            text_parts.append(child.tail)
    return "".join(text_parts)
	
  def _fetch_fulltext(self, user_query : str, number_to_retrieve : int):
    """fetches available full-text articles from pmc using Entrez"""
    
    pass

  def _fetch_pmids(self, user_query : str, number_to_retrieve : int) -> list[str]:
    """fetches pmids from pubmed using Entrez"""
    
    handle = Entrez.esearch(db="pubmed", retmax=number_to_retrieve, term=user_query)
    record = Entrez.read(handle)
    if isinstance(record, dict):
      ids = record['IdList']
      if self.debug:
        print("=" * 30)
        print(user_query)
        print(record)
        print(f"in fetch_pmids, id_list {ids}")
        print("=" * 30)
        
      return ids
    
    raise TypeError(f"in fetch_pmids, expected a dict, got {type(record).__name__}")


  def _convert_pmid_pmcid(self, pmid : str) -> str:
    """converts a pmid to pmcid, allowing querying of pmc database"""
    
    url = f"https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?ids={pmid}&format=json"
    response = requests.get(url)
    data = response.json()
    pmcids = data["records"][0].get("pmcid")
    if pmcids:
      if self.debug:
        print("=" * 30)
        print(f"in _convert_pmid_pmcid, pmcids: {pmcids}")
        print("=" * 30)
      return pmcids
    raise ValueError(f"in _convert_pmid_pmcid, expected pmcids but got none")
	
  def _rephrase_user_query(self, user_query: str) -> str:
    """Usings helper_agent to rephrase a user query into a searchable keyword string"""
    
    system_prompt = """
    You are a helpful assistant that converts user queries into important keyword searches for PubMed entrez API. For example, 
    if a user query is "Can you give me a brief summary on latest brucella research" the keywords would be "brucella research latest"
    
    Your response must be a string
    Thanks and you will do great!
    """
    
    human_prompt = f"The user query to convert is: {user_query}"
    
    prompt = ChatPromptTemplate.from_messages([
      ("system", system_prompt),
      ("human", human_prompt)
    ])
    
    llm_chain = prompt | self.helper_agent
    rephrased_query = llm_chain.invoke({"user_query": user_query}).content
    if self.debug:
      print("=" * 30)
      print(f"in _rephrase_user_query, user query: {user_query} rephrased as: {rephrased_query}")
    if isinstance(rephrased_query, str):
      return rephrased_query
    else:
      raise TypeError(f"in _rephrase_user_query expected str, got {type(rephrased_query).__name__}")
 
 
 
def connect_pubmed(email : str, debug : bool) -> PubmedAPI:
  """Creates PubmedAPI object"""
  return PubmedAPI(email, debug)
from typing import Literal
from Bio import Entrez
import re
import requests
from xml.etree import ElementTree as ET

class PubmedAPI():
  def __init__(self, email : str, debug : bool = False):
    self.email = email
    Entrez.email = email
    self.debug = debug
    
  
  def search(self, user_query : str, number_to_retrieve : int, mode : Literal["abstract", "full"] = "abstract"):
    
    if mode == "abstract":
      self._fetch_abstracts(user_query, number_to_retrieve)
      
    elif mode == "full":
      self._fetch_fulltext(user_query, number_to_retrieve)
      
    else:
      raise ValueError(f'mode with value {mode} is invalid, must be "abstract" or "full"')
  
  
  def _fetch_abstracts(self, user_query : str, number_to_retrieve : int):
    """fetches abstracts from pubmed using Entrez"""
    
    if (number_to_retrieve > 15):
      raise ValueError(f'number_to_retrieve with value {number_to_retrieve} is quite high, 15 is reasonable limit to maintain context.')
  
	
  def _fetch_fulltext(self, user_query : str, number_to_retrieve : int):
    """fetches available full-text articles from pmc using Entrez"""
    
    pass

  def fetch_pmids(self, user_query : str, number_to_retrieve : int) -> list[str]:
    """fetches pmids from pubmed using Entrez"""
    
    handle = Entrez.esearch(db="pubmed", retmax=number_to_retrieve, term=user_query)
    record = handle.read()
    if isinstance(record, dict):
      if self.debug:
        ids = record['Idlist']
        print(f"in fetch_pmids, id_list {ids}\n")
        return ids
    raise TypeError(f"in fetch_pmids, expected a dict, got {type(record).__name__}")


  def _convert_pmid_pmcid(self, pmid : str) -> str:
    """converts a pmid to pmcid, allowing querying of pmc database"""
    
    url = f"https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?ids={pmid}&format=json"
    response = requests.get(url)
    data = response.json()
    if "records" in data and data["records"]:
      return data["records"][0].get("pmcid", None)
    return ""
	
def connect_pubmed() -> PubmedAPI:
  pass
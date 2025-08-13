from tool import Tool
from helpers.pubmed import connect_pubmed

class PubmedSearch(Tool):
  def __init__(self):
    super().__init__("pubmed_search")
    self.api_client = connect_pubmed()
    
  def execute(self, user_query: str):
    return self.api_client.search("pubmed_search")
from tools.tool import Tool
from helpers.pubmed import connect_pubmed

class PubmedSearch(Tool):
  def __init__(self, email: str, debug: bool = False):
    super().__init__("pubmed_search")
    self.api_client = connect_pubmed(email, debug)
    
  def execute(self, *args, **kwargs):
    user_query = kwargs.get("user_query") or args[0]
    number_to_retrieve = kwargs.get("number", 5)
    mode = kwargs.get("type", "abstract")
    return self.api_client.search(user_query, number_to_retrieve, mode)
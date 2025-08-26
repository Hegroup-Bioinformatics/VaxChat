from tools.tool import Tool
from drivers.neo4j_drive import connect_neo4j
from helpers.embed import EmbedAPI

class EmbedSearch(Tool):
  def __init__(self, debug: bool):
    super().__init__("embed_search")
    self.debug = debug
    self.neo4j_client = connect_neo4j()
    self.api_client = EmbedAPI(self.neo4j_client, self.debug)
  
  def execute(self, *args, **kwargs):
    user_query = kwargs.get("user_query") or args[0]
    k = kwargs.get("k", 1)
    return self.api_client.retrieve(user_query, k)
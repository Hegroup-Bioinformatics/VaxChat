from tool import Tool
from drivers.neo4j_drive import connect_neo4j
from helpers.cypher import CypherAPI

class CypherSearch(Tool):
  def __init__(self, debug : bool):
    super().__init__("cypher_search")
    self.neo4j_client = connect_neo4j()
    self.cypher_api = CypherAPI(self.neo4j_client, debug)
    
  def execute(self, *args, **kwargs):
    user_query = kwargs.get("user_query") or args[0]
    return self.cypher_api.retrieve(user_query)
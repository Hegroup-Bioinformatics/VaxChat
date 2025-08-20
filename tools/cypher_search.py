from tools.tool import Tool
from drivers.neo4j_drive import connect_neo4j
from helpers.cypher import CypherAPI

class CypherSearch(Tool):
  def __init__(self, debug : bool, vector_store_names: list[str], cypher_queries: list[str], cypher_query_names: list[str]):
    super().__init__("cypher_search")
    self.neo4j_client = connect_neo4j()
    self.cypher_api = CypherAPI(self.neo4j_client, debug, vector_store_names, cypher_queries, cypher_query_names)
    
  def execute(self, *args, **kwargs):
    user_query = kwargs.get("user_query") or args[0]
    return self.cypher_api.retrieve(user_query)
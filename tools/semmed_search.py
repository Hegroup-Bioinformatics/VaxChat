from tools.tool import Tool
from drivers.neo4j_drive import connect_neo4j
from helpers.llm import create_llm
from helpers.semmed import SemmedAPI

class SemmedSearch(Tool):
  def __init__(self, debug: bool, dotenv_path: str = "../semmed_neo4j.env"):
    super().__init__("semmed_search")
    self.driver = connect_neo4j(dotenv_path)
    self.helper = create_llm()
    self.semmed_api = SemmedAPI(self.driver, self.helper, debug)
  
  def execute(self, *args, **kwargs):
    user_query = kwargs.get("user_query") or args[0]
    k = kwargs.get("k", 10)
    return self.semmed_api.retrieve(user_query, k)
	
    
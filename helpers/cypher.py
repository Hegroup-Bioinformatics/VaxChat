from helpers.llm import create_llm
from helpers.ner import create_ner

from neo4j import Driver, Query
import neo4j


class CypherAPI():
  def __init__(self, neo4j_driver: Driver, debug: bool):
    self.neo4j_driver = neo4j_driver
    self.helper_agent = create_llm()
    self.debug = debug
    self.ner_model = create_ner()
    
  def retrieve(self, user_query : str) -> str:
    """takes user query, normalizes it, converts into cypher, returns the retrieved data from neo4j"""
    
    raise NotImplementedError
    
  def _normalize_query(self, user_query : str, entities : list[str]) -> str:
    """takes user query with highlighted entities and normalizes it to VaxKG name conventions"""
    raise NotImplementedError
    
  def _run_cypher(self, query: Query) -> list[dict]:
    """runs cypher query and returns data"""
    try:
      with self.neo4j_driver.session(default_access_mode=neo4j.READ_ACCESS) as session:
        retrieved_data = session.run(query)
        results = retrieved_data.data()
        if results is None:
          raise ValueError("in _run_cypher, expected results but got None")
        else:
          return results
    except Exception as e:
      raise Exception(f"in _run_cypher, got exception {e}")
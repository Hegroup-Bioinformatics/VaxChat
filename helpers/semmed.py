from langchain_core.prompts import ChatPromptTemplate
import neo4j

class SemmedAPI():
  def __init__(self, neo4j_driver, helper, debug: bool):
    self.neo4j_driver = neo4j_driver
    self.helper = helper
    self.debug = debug
    
  def retrieve(self, user_query: str, k: int):
    """Converts user query into cypher and retrieves k triples"""
    system_prompt = """
    You are a professional cypher expert, converting user queries into cypher. You will be provided
    a user query, please convert it into a cypher query. Your limit should be k which will also 
    be provided.
    
    The database that you work with is SemMedDB. Below are the node types and the relationships.
    
    Assertion: [triple, predication_id, indicator_type]
    Entity: [cui, name, semtype]
    Predicate [name]
    
    The relationship structure is:
    
    Assertion -[:CONTAINS_SUBJECT]-> Entity
    Assertion -[:CONTAINS_OBJECT]-> Entity
    Assertion -[:CONTAINS_PREDICATE]-> Predicate
    
    Always return the triples
    
    Examples:
    MATCH (p:Entity)<-[:CONTAINS_OBJECT|CONTAINS_SUBJECT]-(a:Assertion)
    WHERE toLower(p.name) CONTAINS "brucella"
    RETURN a.triple
    LIMIT 10
    
    Your response must be **strictly string** containing only the cyper query:
    """
    
    human_prompt = f"The user query is: {user_query} and the k is: {k}"
    
    prompt = ChatPromptTemplate([
      ("system", system_prompt),
      ("human", human_prompt)
    ])
    
    llm_chain = prompt | self.helper
    final_response = llm_chain.invoke({"user_query": user_query, "k": k}).content
    if self.debug:
      print(final_response)
    
    with self.neo4j_driver.session(default_access_mode=neo4j.READ_ACCESS) as session:
      retrieved_data = session.run(final_response)
      results = retrieved_data.data()
      if self.debug:
        print(results)
        
      if results is None:
        raise ValueError("in SemMedAPI, expected results but got None")
      else:
        return results

    
  
  
  
  
  
  
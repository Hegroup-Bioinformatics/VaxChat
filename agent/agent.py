from helpers.llm import create_llm
from tools.tool import Tool
from tools.cypher_search import CypherSearch
#from tools.embed
from tools.pubmed_search import PubmedSearch
from drivers.neo4j_drive import connect_neo4j


from langchain_core.prompts import ChatPromptTemplate
from typing import Optional, Any, Literal
from pydantic import BaseModel

class State:
  def __init__(self):
    self.past_messages = []
    self.performance_history = []

class Decision(BaseModel):
  tool_to_use : str
  tool_parameters : dict[str, str]

class Agent:
  def __init__(self,
               email: str, 
               name: str = "Agent", 
               llm_model: str = "AzureOpenAI", 
               tool_names: list[str] = ["cypher_search", "embed_search", "pubmed_search"],
               vector_stores: list[str] = ["host", "pathogen", "vaccine"],
               debug: bool = False): 
    self.name = name
    self.email = email
    self.llm_model = create_llm(llm_model)
    self.tool_names = tool_names
    self.neo4j_driver = connect_neo4j()
    self.state = ""
    self.debug = debug
    self.tools: dict[str, Tool] = {}
    
    for tool in tool_names:
      if tool == "cypher_search":
        self.tools["cypher_search"] = CypherSearch(self.debug, vector_stores, ["MATCH (n: HostName) return n.NAME", "MATCH (n: PathogenName) return n.NAME", "MATCH (n: VaccineName) return n.NAME"], [])
      if tool == "embed_search":
        pass
      if tool == "pubmed_search":
        self.tools["pubmed_search"] = PubmedSearch(self.email, self.debug)
  
  """
  def run(self, prompt, query):
    decision = self.decide(prompt)
    if decision:
      return self.tools[decision].execute(prompt)
  """
  def decide(self, user_query : str): 
    system_prompt = """
      You are a professional decision maker that chooses the best tool for user queries in the biological domain. 
      You will be provided a user query and optionally the agent state. Each tool has parameters, only fill them if the tool
      requires them.

      Available tools:

      - pubmed_search (parameters: 
          type: "full" or "abstract" (default: "abstract"), 
          number: integer (default: 5, use 10 if summary requested),
          query: rephrase the user query for use with pubmed article keyword search api. For example, 
            if a user query is "Can you give me a brief summary on latest brucella research" the keywords would be "brucella research latest"
        ): retrieves PubMed papers for the query.

      Below are tools based on VaxKG, a knowledge graph composed of many nodes like host, pathogen, vaccine. The graph is also embedded 
      with structural ontology related to the biology domain.

      - embedded_search(parameters: there are no tool parameters for this tool): embeds the user query and finds adjacent subgraph in the embedding space.

      - cypher_search (parameters: there are no tool parameters for this tool): a specialized agent converts the user query into Cypher and retrieves data from the graph.

      Your response must be **strictly JSON** following this schema:

      {{
        "tool_to_use": "<exact tool name>",
        "tool_parameters": {{
            "param1": "value1",
            "param2": "value2"
        }}
      }}
      Thank you and do your best!
    """
        
    human_prompt = "The user query is: {user_query}"
    if self.state:
      human_prompt += f" and the agent state is: {self.state}"
    
    prompt = ChatPromptTemplate.from_messages([
      ("system", system_prompt),
      ("human", human_prompt)
    ])
    
    llm_chain = prompt | self.llm_model
    
    decision = llm_chain.invoke({"user_query": user_query})
    return decision.content

  def final_answer(self, user_query: str, retrieved_content: Any, tool_used: Literal["pubmed_search", "embedded_search", "cypher_search"]) -> str:
    system_prompt = """
    You are a professional expert in the biology field. You are given a user query and retrieved information. Using this retrieved information, please 
    answer the question to the best of your ability. 
    Your response must be a string.
    
    Thank you and do your best!"""
    
    human_prompt = "The user query is {user_query}"
    
    if tool_used == "pubmed_search":
      human_prompt += " and the resulting data from pubmed is {retrieved_content}"
    
    prompt = ChatPromptTemplate([
      ("system", system_prompt),
      ("human", human_prompt)
    ])
    
    llm_chain = prompt | self.llm_model
    final_response = llm_chain.invoke({"user_query": user_query, "retrieved_content": retrieved_content}).content
    
    if not isinstance(final_response, str):
        final_response = str(final_response)
    return final_response
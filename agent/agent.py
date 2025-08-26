from helpers.llm import create_llm
from tools.tool import Tool
from tools.cypher_search import CypherSearch
from tools.embed_search import EmbedSearch
from tools.pubmed_search import PubmedSearch
from tools.semmed_search import SemmedSearch
from drivers.neo4j_drive import connect_neo4j


from langchain_core.prompts import ChatPromptTemplate
from typing import Optional, Any, Literal
from pydantic import BaseModel
import json

class Message:
  def __init__(self, user_query: str, tool_used: str, generated_answer: str):
    self.query = user_query
    self.tool = tool_used
    self.answer = generated_answer

class State:
  def __init__(self):
    self.past_messages: str = ""
    self.performance_history = []

class Decision(BaseModel):
  tool: str
  tool_parameters: dict[str, Any]
  

class Agent:
  def __init__(self,
               email: str, 
               name: str = "Agent", 
               helper_model: str = "AzureOpenAI-35-turbo", 
               llm_model: str = "AzureOpenAI-4o-mini",
               tool_names: list[str] = ["cypher_search", "embed_search", "pubmed_search", "semmed_search"],
               vector_stores: list[str] = ["host", "pathogen", "vaccine"],
               debug: bool = False): 
    self.name = name
    self.email = email
    self.helper_model = create_llm(helper_model)
    self.answer_model = create_llm(llm_model)
    self.tool_names = tool_names
    self.neo4j_driver = connect_neo4j()
    self.state = State()
    self.debug = debug
    self.tools: dict[str, Tool] = {}
    
    for tool in tool_names:
      if tool == "cypher_search":
        self.tools["cypher_search"] = CypherSearch(self.debug, vector_stores, ["MATCH (n: HostName) return n.NAME", "MATCH (n: PathogenName) return n.NAME", "MATCH (n: VaccineName) return n.NAME"], [])
      elif tool == "embed_search":
        self.tools["embed_search"] = EmbedSearch(self.debug)
      elif tool == "pubmed_search":
        self.tools["pubmed_search"] = PubmedSearch(self.email, self.debug)
      elif tool == "semmed_search":
        self.tools["semmed_search"] = SemmedSearch(self.debug)
      else:
        raise ValueError
  
  """
  def run(self, prompt, query):
    decision = self.decide(prompt)
    if decision:
      return self.tools[decision].execute(prompt)
  """
  def answer(self, user_query: str) -> str:
    state_update_str = f"User query: {user_query}\n"
    
    decision = self._decide(user_query)
    tool = decision.tool
    if tool == "cypher_search":
      retrieved = self.tools["cypher_search"].execute(user_query=user_query)
    elif tool == "embedded_search":
      retrieved = self.tools["embed_search"].execute(user_query=user_query, k=decision.tool_parameters["k"])
    elif tool == "pubmed_search":
      retrieved = self.tools["pubmed_search"].execute(user_query=decision.tool_parameters["query"], number_to_retrieve=decision.tool_parameters["number"], type=decision.tool_parameters["type"])
    elif tool == "semmed_search":
      retrieved = self.tools["semmed_search"].execute(user_query=user_query, k=decision.tool_parameters["k"])
    elif tool == "conversation":
      final_answer = decision.tool_parameters["message"]
      state_update_str += f"Answer: {final_answer}\n"
      self.state.past_messages += state_update_str
      return final_answer
    else: 
      raise ValueError
    
    final_answer = self._final_answer(user_query, retrieved, tool)
    
    state_update_str += f"Answer: {final_answer}\n"
    self.state.past_messages += state_update_str
    
    return final_answer

  def _decide(self, user_query: str) -> Decision: 
    system_prompt = """
      You are a professional decision maker that chooses the best tool for user queries in the biological domain. 
      You will be provided a user query and optionally the agent state. Each tool has parameters, only fill them if the tool
      requires them.

      Available tools:

      - pubmed_search (parameters: 
          type: "full" or "abstract" (default: "abstract"), 
          number: integer (default: 5, use 10 if summary requested),
          query: rephrase the user query for use with pubmed article keyword search api. For example, 
            if a user query is "Can you give me a brief summary on latest brucella research" the keywords would be "brucella latest" Pick keywords carefully you only can pick 3 keywords.
        ): retrieves PubMed papers for the query.
        
      - semmed_search (parameters: k: the number of triples to retrieve, default is 10)

      Below are tools based on VaxKG, a knowledge graph composed of many nodes like host, pathogen, vaccine. The graph is also embedded 
      with structural ontology related to the biology domain.

      - embedded_search (parameters: k: the number of nodes to retrieve (use 3 as a baseline)): embeds the user query and finds adjacent subgraph in the embedding space.

      - cypher_search (parameters: there are no tool parameters for this tool): a specialized agent converts the user query into Cypher and retrieves data from the graph.
      
      If no tool fits the tool's purpose, ie its a greeting message, your response should be: 
      - conversation (parameters: message)

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
    if self.state.past_messages:
      human_prompt += f" and the agent state is:\n{self.state.past_messages}"
    
    prompt = ChatPromptTemplate.from_messages([
      ("system", system_prompt),
      ("human", human_prompt)
    ])
    
    llm_chain = prompt | self.helper_model
    
    decision = llm_chain.invoke({"user_query": user_query})
    if self.debug:
      print(decision)
      
    if isinstance(decision.content, str):
      tool_json = json.loads(decision.content)
    else: 
      raise ValueError
    return Decision(tool=tool_json["tool_to_use"], tool_parameters=tool_json["tool_parameters"])

  def _final_answer(self, user_query: str, retrieved_content: Any, tool_used: str) -> str:
    system_prompt = """
    You are a professional expert in the biology field. You are given a user query and retrieved information. Using this retrieved information, please 
    answer the question to the best of your ability. 
    Your response must be a string. You should keep answer in a chat length unless otherwise instructed.
    
    Thank you and do your best!"""
    
    human_prompt = "The user query is {user_query}"
    
    if tool_used == "pubmed_search":
      human_prompt += " and the resulting data from pubmed is {retrieved_content}"
    elif tool_used == "cypher_search":
      human_prompt += " and the resulting data from vaccine knowledge graph is {retrieved_content}"
    elif tool_used == "embedded_search":
      human_prompt += " and the resulting data from embedded search on vaccine knowledge graph is {retrieved_content}"
      
    
    prompt = ChatPromptTemplate([
      ("system", system_prompt),
      ("human", human_prompt)
    ])
    str_retrieve_content = str(retrieved_content)
    llm_chain = prompt | self.answer_model
    final_response = llm_chain.invoke({"user_query": user_query, "retrieved_content": str_retrieve_content}).content
    if self.debug:
      print(final_response)
      
    if not isinstance(final_response, str):
        final_response = str(final_response)
    return final_response
  
  def self_evaluate(self, user_query: str, retrieved_data: str):
    """Evaluates and decides whether additional information is needed or the retrieval is good"""
    
    system_prompt = """You are an evaluator of a retriever system, you will determine whether or not the information is relevant to the questions.
      correct - will give this information an agent that answers the query using this information.
      more_info will do re-retrieval but on a different resource.
      incorrect - will completely scrap this information and cause re-retrieval
    Your output should strictly be a string, with correct, more_info, and incorrect as options."""
    
    human_prompt = f"The user query is: {user_query} and retrieved data is: {retrieved_data}"
    
    prompt = ChatPromptTemplate([
      ("system", system_prompt),
      ("human", human_prompt)
    ])
    
    llm_chain = prompt | self.answer_model
    final_response = llm_chain.invoke({"user_query": user_query, "retrieved_data": retrieved_data}).content
    if self.debug:
      print(final_response)
      
    if final_response == "correct":
      pass
    elif final_response == "more_info":
      pass
    elif final_response == "incorrect":
      pass
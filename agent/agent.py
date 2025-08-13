from helpers.llm import create_llm



from langchain_core.prompts import ChatPromptTemplate
from typing import Optional
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
               name: str = "Agent", 
               llm_model: str = "AzureOpenAI", 
               tools: list[str] = ["cypher_search", "embed_search", "pubmed_search"]): 
    self.name = name
    self.llm_model = create_llm(llm_model)
    self.tools = tools
    self.state = ""
  
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
          query: rephrase the user query for use with pubmed article search api
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
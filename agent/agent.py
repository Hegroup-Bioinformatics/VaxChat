
from langchain_core.prompts import ChatPromptTemplate

class State:
  def __init__(self):
    self.past_messages = []
    self.performance_history = []



class Agent:
  def __init__(self, name, llm_model, tools, prompt, memory): 
    self.name = name
    self.llm_model = llm_model
    self.tools = tools
    self.prompt = prompt
    self.memory = memory
  
  def run(self, prompt, query):
    decision = self.decide(prompt)
    if decision:
      return self.tools[decision].execute(prompt)
  
  def decide(self, user_query, state): 
    prompt = ChatPromptTemplate.from_messages([
			"system", """
   		You are a skilled decision maker that decides the tool to be used for user queries. You will be provided a user query and you
     	must decide which of the following tools to use.
    		
      -pubmed_search: a tool that will use pubmed api to answer the user query with a retrieved pubmed paper.
      
      VaxKG is a knowledge graph containing information on the following entities:
				vaccines, pathogens, hosts, references, 
      
      -embedded_search"""
		])
  
  
from neo4j import GraphDatabase, Driver
from dotenv import load_dotenv
import os

def connect_neo4j(dotenv_name: str = "../neo4j.env") -> Driver:
  """Connects to Neo4j instance, requires login credentials in neo4j.env"""
  
  load_dotenv(dotenv_name)
  uri = os.getenv("NEO4J_URI")
  user = os.getenv("NEO4J_USER")
  password = os.getenv("NEO4J_PASSWORD")
  if not uri or not user or not password:
    raise ValueError("in connect_neo4j, expected login credentials but got None")
  driver = GraphDatabase.driver(uri, auth=(user, password))
  return driver
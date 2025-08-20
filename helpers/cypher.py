from helpers.llm import create_llm
from helpers.ner import create_ner
from embed_create.vector_store import VectorStore

from spacy.tokens import Doc
from neo4j import Driver, Query
import neo4j
from langchain_core.prompts import ChatPromptTemplate
import json


class CypherAPI():
  def __init__(self, 
               neo4j_driver: Driver, 
               debug: bool, vector_store_names: list[str], 
               cypher_queries: list[str], 
               cypher_name_properties: list[str]):
    self.neo4j_driver = neo4j_driver
    self.helper_agent = create_llm()
    self.debug: bool = debug
    self.ner_model = create_ner()
    self.vector_store: dict[str, VectorStore] = {}
    
    self._create_vectorstores(vector_store_names, cypher_queries, cypher_name_properties)
    
  def retrieve(self, user_query : str):
    """takes user query, normalizes it, converts into cypher, returns the retrieved data from neo4j"""
    
    normalized_query = self._normalize_query(user_query)
    cypher_query = self._convert_to_cypher(normalized_query)
    neo4j_data = self._run_cypher(cypher_query)
    if self.debug:
      print(neo4j_data)
    
    return neo4j_data
    
  def _normalize_query(self, user_query : str) -> str:
    """takes user query with highlighted entities and normalizes it to VaxKG name conventions"""
    
    doc = self._run_ner(user_query)
    
    #for each text, entity pair in doc.ents, we map the text into text indexed with entity, using a arbitrary distance.
    if self.debug:
      print("doc")
      print(doc)
    #replace each text with new text
    normalized_query = ""
    for token in doc:
      if token.ent_iob_ != "O":
        #map and convert
        index = token.ent_type_.lower()
        if self.debug: 
          print(index)
        standardized_token = self.vector_store[index].query(token.text, 1)
        if self.debug:
          print(standardized_token)
        normalized_query += " " + standardized_token[0][0]
      else:
        normalized_query += " " + token.text
        
    if self.debug:
      print(normalized_query)
    return normalized_query.strip()
  
  
  def _run_ner(self, user_query) -> Doc:
    """runs the user query from NER model and provides doc with doc.ents annotations"""
    
    doc = self.ner_model(user_query)
    if self.debug:
      for ent in doc:
        print(ent.text, ent.ent_type_, ent.ent_iob_)
    return doc
    
  def _run_cypher(self, query: str) -> list[dict]:
    """runs cypher query and returns data"""
    try:
      with self.neo4j_driver.session(default_access_mode=neo4j.READ_ACCESS) as session:
        q = Query(query) # type: ignore
        retrieved_data = session.run(q)
        results = retrieved_data.data()
        if results is None:
          raise ValueError("in _run_cypher, expected results but got None")
        else:
          return results
    except Exception as e:
      raise Exception(f"in _run_cypher, got exception {e}")
    
    
  def _create_vectorstores(self, names: list[str], cypher_queries: list[str], cypher_name_properties: list[str] = []):
    """Finds all the names of the speciifc vectorstore and creates VectorStore instances"""

    if cypher_name_properties == []:
      cypher_name_properties = ["n.NAME"] * len(cypher_queries)
    elif len(cypher_name_properties) == 1:
      cypher_name_properties = cypher_name_properties * len(cypher_queries)
      
    if (len(names) != len(cypher_queries)):
      raise ValueError("in _create_vectorstores, expected lists names and cypher_queries to be same length")

    for cypher_query, name, query_name in zip(cypher_queries,names, cypher_name_properties):
      self.vector_store[name] = VectorStore(name)
      if self.vector_store[name].load():
        continue
      else:
        results = self._run_cypher(cypher_query)
        entities = [entity[query_name] for entity in results]
        self.vector_store[name].create_index(entities)
        self.vector_store[name].save()
        
  def _convert_to_cypher(self, normalized_query: str) -> str:
    """Takes in a normalized_query and returns a converted cypher query"""
    
    system_prompt = """
    You are a professional cypher expert, converting user queries into cypher. You will be provided a user query, please convert it into a cypher query that can best answer the user's question.
    You can be assured the entity names are standardized to the terms used in the database.
    
    Include nodes, relationships, and relevant properties in the queries.
    Use a default limit of 5 for specific queries, and a limit of 15 for abstract queries (e.g., "What is a description of Hepatitis C") only if the user does not specify a limit.
    Filter out empty or null values using IS NOT NULL, <> "", and <> "N/A".
    Keep in mind that all properties and node names, including numbers (e.g., HOST_ID), are treated as strings.
    Create robust and flexible queries when matching strings by using CONTAINS to ensure a match is found.
    Trim values to ensure better matching.
    Your response should only include the Cypher query itself.
    
    Node Types and their related Properties:
    {{
      HostName: [NAME, HOST_ID, HOST_SCIENTIFIC_NAME, HOST_TAXONOMY_ID],
      PathogenName: [NAME, PATHOGEN_ID, TAXON_ID, DISEASE_NAME, HOST_RANGE, ORGANISM_TYPE, PREPARATION_VO_ID, VACCINE_VO_ID, PROTEIN_VO_ID, PATHOGENESIS, PROTECTIVE_IMMUNITY, GRAM],
      VaccineName: [NAME, VACCINE_ID, IS_COMBINATION_VACCINE, DESCRIPTION, ADJUVANT, STORAGE, VIRULENCE, PREPARATION, BRAND_NAME, FULL_TEXT, ANTIGEN, CURATION_FLAG, VECTOR, PROPER_NAME, 
      MANUFACTURER, CONTRAINDICATION, STATUS, LOCATION_LICENSED, ROUTE, VO_ID, USAGE_AGE, MODEL_HOST, PRESERVATIVE, ALLERGEN, PREPARATION_VO_ID, HOST_SPECIES2, CVX_CODE, CVX_DESC]
    }}
    
    Relationships:
      (vn:VaccineName)-[:TARGETS_PATHOGEN]->(pn:PathogenName)
      (vn:VaccineName)-[:TARGETS_HOST]->(hn:HostName)
      
    Example Queries:
    User Query: 
      "Find vaccines targeting pathogens that cause disease in humans." 
    Cypher Query:
      MATCH (v:VaccineName)-[:TARGETS_PATHOGEN]->(p:PathogenName)
      MATCH (h:HostName {{NAME: "Human"}})
      WHERE p.DISEASE_NAME IS NOT NULL AND trim(p.DISEASE_NAME) <> ""
      RETURN v.NAME AS Vaccine, p.NAME AS Pathogen, p.DISEASE_NAME AS DISEASE
      LIMIT 5

    User Query: 
    "What vaccines were made by Pfizer Inc.?" 
    Cypher Query:
      MATCH (v:VaccineName)
      WHERE toLower(v.MANUFACTURER) CONTAINS toLower("Pfizer")
      RETURN v.NAME
      LIMIT 5

    User Query: 
      "What are the most common routes for Brucella vaccines?" 
    Cypher Query:
      MATCH (v:VaccineName)-[:TARGETS_PATHOGEN]->(p:PathogenName)
      WHERE toLower(p.NAME) CONTAINS toLower("Brucella")
      AND v.ROUTE IS NOT NULL
      AND toLower(trim(v.ROUTE)) <> "na"
      AND trim(v.ROUTE) <> ""
      RETURN v.ROUTE AS Route, COUNT(v.ROUTE) AS RouteCount
      ORDER BY RouteCount DESC
      LIMIT 5

    User Query: 
      "What are Influenza vaccines?" 
    Cypher Query:
      MATCH (v:VaccineName)-[:TARGETS_PATHOGEN]->(p:PathogenName)
      WHERE toLower(p.NAME) CONTAINS toLower("Influenza")
      AND v.DESCRIPTION IS NOT NULL
      AND toLower(v.DESCRIPTION) <> "na"
      AND v.DESCRIPTION <> ""
      RETURN v.DESCRIPTION AS VaccineDescription
      LIMIT 15

    User Query: 
      "Can you give me a list of 10 vaccine manufacturers by number of vaccines?" 
    Cypher Query:
      MATCH (v:VaccineName)
      WHERE v.MANUFACTURER IS NOT NULL AND v.MANUFACTURER <> ""
      WITH v.MANUFACTURER AS Manufacturer, COUNT(v) AS VaccineCount
      RETURN Manufacturer, VaccineCount
      ORDER BY VaccineCount DESC
      LIMIT 10
  
    Your response must be **strictly JSON** following this schema:
    
    {{"cypher": "cypher_query"}}
    Thank you and do your best!
    """
    
    human_prompt = "The user query is: {user_query}"
    
    prompt = ChatPromptTemplate([
      ("system", system_prompt),
      ("human", human_prompt)
    ])
    
    llm_chain = prompt | self.helper_agent
    final_response = llm_chain.invoke({"user_query": normalized_query}).content
    cypher_query = None
    try:
      json_response = json.loads(final_response) # type: ignore
      try: 
        cypher_query = json_response.get("cypher")
      except:
        print("in _convert_to_cypher() failed retrieving cypher parameter")
    except:
      print("in _convert_to_cypher() failed making json from chat response")
    
    if self.debug:
      print(cypher_query)
    if not isinstance(cypher_query, str):
      cypher_query = str(cypher_query)
    return cypher_query
    
from embed_create.vector_store import VectorStore

from neo4j import Driver
import neo4j

class EmbedAPI():
  def __init__(self, 
               neo4j_client: Driver,
               debug: bool):
    self.neo4j_driver = neo4j_client
    self.debug: bool = debug
    self.vector_store: VectorStore = VectorStore("graph_embed")
    
  def retrieve(self, user_query: str, k: int):
    """takes user query, embeds it, and then searches the vector database retrieve k top results"""
    
    if not self.vector_store.load():
      self._create_vectorstore()
    
    result = self.vector_store.query(user_query, k)
    result_str = "".join(result_node_str for result_node_str, _ in result)
    return result_str
    
  def _create_vectorstore(self):
    """retrieves all nodes and embeds them into a vectorstore"""
    
    nodes_text = self._fetch_nodes()
    self.vector_store.create_index(nodes_text)
    self.vector_store.save()
    
  def _fetch_nodes(self):
    with self.neo4j_driver.session() as session:
      result = session.run("MATCH (n) RETURN labels(n) as labels, properties(n) as props")
      nodes = []
      for node_expanded in result:
        if self.debug:
          print("in _fetch_nodes joining node")
        labels = ":".join(node_expanded["labels"])
        props = " ".join([f"{k}:{v}" for k,v in node_expanded["props"].items()])
        nodes.append(f"{labels} {props}")
      if self.debug:
        print(nodes)
      return nodes
import faiss
import numpy as np
import pickle
from sentence_transformers import SentenceTransformer
from typing import Optional, Tuple
from pathlib import Path

class VectorStore:
  def __init__(self, name: str, model_name: str = "all-MiniLM-L6-v2") -> None:
    self.name: str = name
    self.model: SentenceTransformer = SentenceTransformer(model_name)
    self.index: Optional[faiss.Index] = None
    self.entities: list[str] = []
    self.folder_path = Path("../embed_create/data")
    self.folder_path.mkdir(parents=True, exist_ok=True)
    
  def create_index(self, entities : list[str]) -> None:
    """Create FAISS index from a list of entities as strings"""
    
    self.entities = entities
    embeddings = self.model.encode(entities, normalize_embeddings=True)
    embeddings = np.array(embeddings, dtype="float32")
    dim = embeddings.shape[1]
    self.index = faiss.IndexFlatIP(dim)
    self.index.add(embeddings) # type: ignore
  
  def save(self, index_path: str = "", entities_path: str = "") -> None:
    """Save FAISS index and entities"""
  
    if not index_path:
      index_path = str(self.folder_path / f"{self.name}.index")
    if not entities_path:
      entities_path = str(self.folder_path / f"{self.name}.pkl")
    with open(entities_path, "wb") as file:
      pickle.dump(self.entities, file)
    faiss.write_index(self.index, index_path)
      
  def load(self, index_path: str = "", entities_path: str = "") -> bool:
    """Load FAISS index and entites"""
    
    if not index_path:
      index_path =  str(self.folder_path / f"{self.name}.index")
    if not entities_path:
      entities_path = str(self.folder_path / f"{self.name}.pkl")
    
    try:
      with open(entities_path, "rb") as file:
        self.entities = pickle.load(file)
        self.index = faiss.read_index(index_path)
        return True
    except:
      return False
  
  def query(self, query: str, top_k: int) -> list[Tuple[str, float]]:
    """Search the vectorstore and return k nearest neighbors"""
    
    if self.index is None:
      raise ValueError("Index is None, was it loaded or created?")
    if self.entities is None:
      raise ValueError("Entities is None, was it loaded or created?")
    query_vec = self.model.encode([query], normalize_embeddings=True).astype("float32")
    D, I = self.index.search(query_vec, top_k) #type: ignore
    return [(self.entities[idx], score) for idx, score in zip(I[0], D[0])]
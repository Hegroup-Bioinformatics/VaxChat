import spacy
from spacy.language import Language


def create_ner() -> Language:
  """creates a ner model for entity normalization"""
  
  #absolute path change later
  nlp = spacy.load(r"C:\Local Desktop\NER Model\ner_model")
  return nlp
  
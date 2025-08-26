from dotenv import load_dotenv
import os

def connect_langchain(dotenv_name: str = "../langchain.env"):
  load_dotenv(dotenv_name)
  os.environ["LANGCHAIN+TRACING_V2"] = os.getenv("LANGCHAIN_TRACING")
  os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
  os.environ["LANGCHAIN+ENDPOINT"] = os.getenv("LANGCHAIN_ENDPOINT")
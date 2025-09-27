from typing import Optional
from pydantic import SecretStr
from langchain_openai import AzureChatOpenAI
from dotenv import load_dotenv
from langchain_core.language_models.chat_models import BaseChatModel
import os

def create_llm(
			model: str = "AzureOpenAI-4o-mini",
			temperature: float = 0.3,
) -> BaseChatModel: 
  """LLM constructor that loads credentials from llm.env, AzureOpenAI with gpt35-turbo is default"""
  
  load_dotenv("../llm.env")
  valid_models = ["AzureOpenAI-4o-mini"]
  if model == "AzureOpenAI-4o-mini":
    return AzureChatOpenAI(
			api_key = SecretStr(os.getenv("OPEN_AI_KEY") or ""),
			api_version = "2024-10-21",
			openai_organization = os.getenv("OPEN_AI_ORG"), # type: ignore
			azure_deployment="gpt-4o-mini",
			azure_endpoint = os.getenv("AZURE_ENDPOINT"),
			temperature=temperature
		)
  else:
    raise ValueError(f"Invalid model parameter: {model}, only implemented models are {valid_models}")
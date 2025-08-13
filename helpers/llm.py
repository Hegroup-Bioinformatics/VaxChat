from typing import Optional
from pydantic import SecretStr
from langchain_openai import AzureChatOpenAI
from dotenv import load_dotenv
from langchain_core.language_models.chat_models import BaseChatModel
import os

def create_llm(
			model: str = "AzureOpenAI",
			temperature: float = 0.7,
) -> BaseChatModel: 
  load_dotenv("../llm.env")
  valid_models = ["AzureOpenAI"]
  if model == "AzureOpenAI":
    return AzureChatOpenAI(
				api_key = SecretStr(os.getenv("OPEN_AI_KEY") or ""),
				api_version = "2024-06-01",
				organization = os.getenv("OPEN_AI_ORG"),
				azure_deployment="gpt-35-turbo",
				azure_endpoint = os.getenv("AZURE_ENDPOINT"),
				temperature=temperature
		)
  else:
    raise ValueError(f"Invalid model parameter: {model}, only implemented models are {valid_models}")
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import sys
sys.path.append("../")

from agent.agent import Agent

load_dotenv("langchain.env")
os.environ["LANGCHAIN_TRACING_V2"] = os.getenv("LANGCHAIN_TRACING", "")
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY", "")
os.environ["LANGCHAIN_ENDPOINT"] = os.getenv("LANGCHAIN_ENDPOINT", "")

load_dotenv("email.env")
email = os.getenv("EMAIL", "")

local_agent = Agent(email, debug=True)

app = Flask(__name__)
CORS(app)

@app.route("/api/chat", methods=["POST"])
def generateAnswer():
  data = request.get_json()
  if not data or 'input' not in data:
    return jsonify({"error": "Invalid input"}, 400)
  
  user_query = data['input']
  answer = local_agent.answer(user_query)
  return jsonify({"response": answer, "cypher": "null", "data": "null"})

if __name__ == "__main__":
  app.run(debug=True)
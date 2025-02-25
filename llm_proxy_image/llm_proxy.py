from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import time
import redis
import os

class Prompt(BaseModel):
    prompt: str

app = FastAPI()

# Redis setup for rate limiting
redis_host = os.getenv("REDIS_HOST", "localhost")
redis_client = redis.Redis(host=redis_host, port=6379, db=0)

# API Keys & Endpoints
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_URL = "https://api.openai.com/v1/chat/completions"

LOCAL_MODEL_URL = os.getenv(
    "LOCAL_MODEL_URL", "http://llm_model:5000/generate")

# Rate Limit settings
RATE_LIMIT_KEY = "last_openai_call"
RATE_LIMIT_SECONDS = 60  # One minute


def is_openai_allowed():
    """Check if the OpenAI API is allowed (once per minute)."""
    last_call = redis_client.get(RATE_LIMIT_KEY)
    if last_call:
        elapsed = time.time() - float(last_call)
        return elapsed >= RATE_LIMIT_SECONDS

    return True


def call_openai(prompt):
    """Calls OpenAI API's GPT-4o-mini API."""
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": "gpt-4o-mini",
               "messages": [{"role": "user", "content": prompt}]}

    response = requests.post(OPENAI_URL, headers=headers, json=payload)
    if response.status_code == 200:
        redis_client.set(RATE_LIMIT_KEY, time.time()) # Store last call timestamp
        return response.json()["choices"][0]["message"]["content"]

    raise HTTPException(status_code=response.status_code, detail=response.text)

def call_local_model(prompt):
    """Calls the local LLM running in another Docker container."""
    response = requests.post(LOCAL_MODEL_URL, json={"prompt": prompt})
    if response.status_code == 200:
        return response.json()["response"]

    raise HTTPException(status_code=response.status_code, detail="Local model error")

@app.post("/chat")
def chat(prompt: Prompt):
    """Routes requests to either OpenAI or the local model based on rate limits."""
    if is_openai_allowed():
        return {"response": call_openai(prompt.prompt)}

    return {"response": call_local_model(prompt.prompt)}
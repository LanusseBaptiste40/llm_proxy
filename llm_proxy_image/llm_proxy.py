from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import json
import time
import redis
import os
import sys

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
    print("Checking OpenAI rate limit", file=sys.stderr)
    last_call = redis_client.get(RATE_LIMIT_KEY)
    if last_call:
        elapsed = time.time() - float(last_call)
        print("Elapsed time since last call:", elapsed, file=sys.stderr)
        return elapsed >= RATE_LIMIT_SECONDS

    print("OpenAI is allowed", file=sys.stderr)
    return True


def call_openai(prompt):
    """Calls OpenAI API's GPT-4o-mini API."""
    print("Calling OpenAI with prompt:", prompt, file=sys.stderr)
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": "gpt-4o-mini",
               "messages": [{"role": "user", "content": prompt}]}

    response = requests.post(OPENAI_URL, headers=headers, json=payload)
    if response.status_code == 200:
        print("OpenAI Response:", response.json(), file=sys.stderr)
        redis_client.set(RATE_LIMIT_KEY, time.time()) # Store last call timestamp
        return response.json()["choices"][0]["message"]["content"]

    print("OpenAI Error:", response.text, file=sys.stderr)
    raise HTTPException(status_code=response.status_code, detail=response.text)

def call_local_model(prompt):
    """Calls the local LLM running in another Docker container."""
    print("Calling Local Model with prompt:", prompt, file=sys.stderr)
    payload = {"model": "llama3", "prompt": prompt}

    try:
        response = requests.post(LOCAL_MODEL_URL, json=payload, stream=True)

        if response.status_code == 200:
            full_response = ""

            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line)
                        if "response" in data:
                            full_response += data["response"]
                    except json.JSONDecodeError:
                        print("JSON Decode Error on line:", line, file=sys.stderr)

            print("Local Model Response:", full_response, file=sys.stderr)
            return full_response

        print("Local Model Error:", response.text, file=sys.stderr)
        raise HTTPException(status_code=response.status_code, detail="Local model error")
    except Exception as e:
        print("Local Model Exception:", str(e), file=sys.stderr)
        raise HTTPException(status_code=500, detail="Local model exception")

@app.post("/chat")
def chat(prompt: Prompt):
    """Routes requests to either OpenAI or the local model based on rate limits."""
    if is_openai_allowed():
        return {"response": call_openai(prompt.prompt)}

    return {"response": call_local_model(prompt.prompt)}
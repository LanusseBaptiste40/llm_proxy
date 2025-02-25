from fastapi import FastAPI
from pydantic import BaseModel
import random

class Prompt(BaseModel):
    prompt: str

app = FastAPI()

responses = [
    "This is a local AI response.",
    "Local model thinks...",
    "Response from local LLM."
]

@app.post("/generate")
def generate(prompt: Prompt):
    return {"response": random.choice(responses)}
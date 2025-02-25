# Project Name

## Description
This project is designed to launch a simple LLM Proxy, that will take an input, once per minute will send the prompt to OPENAI, the rest of the time it will run it against a local LLM.

## Features
- LLM Proxy with rate limiting
- Access to OpenAI
- Local LLM running in a docker image

## Prerequisites
- Docker
- Docker Compose
- An OpenAI Api Key accessible through the `OPENAI_API_KEY` environment variable

## Installation
1. Clone the repository:
  ```sh
  git clone https://github.com/LanusseBaptiste40/llm_proxy.git
  ```
2. Navigate to the project directory:
  ```sh
  cd llm_proxy
  ```

## Usage
1. Start the application:
  ```sh
  docker compose up --build
  ```
2. Send the following curl request to make a call:
  ```sh
  curl --request POST \
    --url http://localhost:8000/chat \
    --header 'Content-Type: application/json' \
    --data '{
    "prompt": "Hello, AI!"
  }'
  ```
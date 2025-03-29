# Project Name

## Description

This project is designed to launch a simple LLM Proxy, that will take an input,
once per minute will send the prompt to OPENAI,
the rest of the time it will run it against a local LLM.

## Features

- LLM Proxy with rate limiting
- Access to OpenAI
- Local LLM running in a docker image using Ollama or Vllm
- LiteLLM as a Proxy

## Prerequisites

- Docker (If you are on Linux, make sure to run docker engine and not docker-desktop,
  since the ollama image does not seem to bind to gpus from docker desktop on Linux)
- Docker Compose
- An OpenAI Api Key accessible through the `OPENAI_API_KEY` environment variable
- (optional) a Huggingface token accessible through the `HUGGINGFACE_TOKEN`
  environment variable if you wish to run the VLLM image.

## Installation

1. Clone the repository:

```sh
git clone https://github.com/LanusseBaptiste40/llm_proxy.git
```

2. Navigate to the project directory:

```sh
cd llm_proxy
```

3. Follow the instructions from [Ollama Docker Image](https://hub.docker.com/r/ollama/ollama)
   to setup the usage of your graphics card.

## Usage

1. Start the application:

```sh
docker compose -f docker-compose.yml -f docker-compose-ollama.yml up --build # To run with the local proxy and the ollama image
docker compose -f docker-compose.yml -f docker-compose-vllm.yml up # To run with the vllm image
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


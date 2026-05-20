import os
import time
import asyncio
from enum import Enum

import boto3
import anthropic
from botocore.exceptions import ClientError
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

from concurrent.futures import ThreadPoolExecutor

load_dotenv(override=True)

app = FastAPI(title="Model Comparison API")

# Create clients ONCE
bedrock_client = boto3.client("bedrock-runtime", region_name=os.getenv("REGION_NAME"))
anthropic_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

AWS_MODEL = os.getenv("AWS_MODEL_ID")
CLAUDE_MODEL = os.getenv("ANTHROPIC_MODEL_ID")

class Provider(str, Enum):
    aws = "aws"
    anthropic = "anthropic"

class QueryRequest(BaseModel):
    prompt: str

def call_aws(prompt: str) -> dict:
    start = time.time()
    response = bedrock_client.converse(
        modelId=AWS_MODEL,
        messages=[
            {
                "role": "user",
                "content": [{"text": prompt}],
            }
        ],
        inferenceConfig={"maxTokens": 512, "temperature": 0.5, "topP": 0.9},
    )
    return {
        "text": response["output"]["message"]["content"][0]["text"],
        "latency_ms": round((time.time() - start) * 1000),
        "model": AWS_MODEL,
    }

def call_anthropic(prompt: str) -> dict:
    start = time.time()
    response = anthropic_client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=512,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )
    return {
        "text": response.content[0].text,
        "latency_ms": round((time.time() - start) * 1000),
        "model": CLAUDE_MODEL,
    }

@app.post("/query/compare")
def query_compare(req: QueryRequest):
    with ThreadPoolExecutor(max_workers=2) as executor:
        aws_response = executor.submit(call_aws, req.prompt)
        anthropic_response = executor.submit(call_anthropic, req.prompt)
        return {
            "aws": aws_response.result(),
            "anthropic": anthropic_response.result(),
        }


@app.post("/query/{provider}")
def get_response(provider: Provider, req: QueryRequest):
    try:
        if provider == Provider.aws:
            return call_aws(req.prompt)
        if provider == Provider.anthropic:
            return call_anthropic(req.prompt)
    except ClientError as e:
        raise HTTPException(status_code=502, detail=f"Upstream provider error: {e}")
    except anthropic.APIError as e:
        raise HTTPException(status_code=502, detail=f"Anthropic API error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {e}")
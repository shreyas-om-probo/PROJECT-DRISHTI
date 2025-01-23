from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
import regex as re
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
import llm_overview
import llm_combined
import json

load_dotenv()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods
    allow_headers=["*"],  # Allows all headers
)

encoder = None
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")

class TextInput(BaseModel):
    text: str


import json

import re
import json
import logging
from fastapi import HTTPException

# Set up logger (assuming logger is configured elsewhere)
logger = logging.getLogger(__name__)

def extract_json_for_against(response):
    try:
        try:
            # Remove markdown code blocks if present
            cleaned_text = re.sub(r'```json\s*|\s*```', '', response.strip())
            # Remove any extra whitespace
            cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
            logger.debug(f"Cleaned text: {cleaned_text[:200]}...")

            # Parse the cleaned text as JSON
            json_data = json.loads(cleaned_text)
            # If it's a dictionary, wrap it in a list
            if isinstance(json_data, dict):
                json_data = [json_data]
            elif isinstance(json_data, list):
                pass
            else:
                raise json.JSONDecodeError("Invalid JSON structure", cleaned_text, 0)



            # Extract the 'For' and 'Against' points
            for_against_data = []

            for item in json_data:
                if "For" in item and "Against" in item:
                    for_against_data.append(item)
                else:
                    logger.warning(f"Item missing 'For' or 'Against' points: {item}")
            
            if not for_against_data:

                raise ValueError("No valid For/Against data found in response")

            return for_against_data

        except json.JSONDecodeError:

            # Second try: Find all JSON-like structures manually
            json_pattern = r'\{(?:[^{}]*|\{(?:[^{}]*|\{[^{}]*\})*\})*\}'
            json_candidates = re.findall(json_pattern, response, re.DOTALL)

            if not json_candidates:
                logger.error("No JSON-like structures found in response")
                raise ValueError("No valid JSON found in response")

            valid_for_against = []
            for candidate in json_candidates:
                try:
                    item = json.loads(candidate)
                    if isinstance(item, dict) and "For" in item and "Against" in item:
                        valid_for_against.append(item)
                except json.JSONDecodeError:
                    continue

            if not valid_for_against:
                raise ValueError("No valid For/Against JSON objects found in response")

            return valid_for_against

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to extract valid For/Against data from response: {str(e)}"
        )

@app.post("/insights")
def event_generate_v1(user_prompt: TextInput):
    print(f'------------------------------------------Call made at {datetime.now()}------------------------------------------')
    print(user_prompt.text)

    overview = llm_overview.call_llm(user_prompt, sot=[], recency="year")
    combined = llm_combined.call_llm(user_prompt, sot=[], recency="year")
    print(combined)
    combined = extract_json_for_against(combined)
    return {"overview":overview,"arguments":(combined)}

@app.get("/")
def read_root():
    return {"message": "Hello World"}

if __name__=='__main__':
    import uvicorn
    uvicorn.run(app)
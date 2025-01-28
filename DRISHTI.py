from fastapi import FastAPI, Form, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import requests
from CREATE_QUERY import create_query
from pydantic import BaseModel
from twitter_query_search import fetch_tweets
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
from contextlib import asynccontextmanager
from datetime import datetime
import regex as re
import os
from dotenv import load_dotenv
import llm_overview
import llm_combined
from logger_config import setup_logger
from WEB_SEARCH import get_news
import httpx
import traceback
from typing import Dict, Any
load_dotenv()

class CustomHTTPException(HTTPException):
    def __init__(self, status_code: int, detail: str, internal_error: str = None):
        super().__init__(status_code=status_code, detail=detail)
        self.internal_error = internal_error
        logger.error(f"HTTP Exception raised - Status: {status_code}, Detail: {detail}, Internal Error: {internal_error}")

# Enhanced logging setup
logger = setup_logger(
    logger_name='contract_processor',
    log_file='contract_processing.log',
    log_format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
)

# Application startup logging
logger.info("="*50)
logger.info("Starting FastAPI application")
logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
logger.info(f"Current timestamp: {datetime.now().isoformat()}")
logger.info("="*50)

app = FastAPI()

# Middleware logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = datetime.now()
    request_id = os.urandom(6).hex()
    logger.info(f"Request started - ID: {request_id} - Method: {request.method} - URL: {request.url}")
    
    try:
        response = await call_next(request)
        process_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"Request completed - ID: {request_id} - Status: {response.status_code} - Duration: {process_time:.3f}s")
        return response
    except Exception as e:
        logger.error(f"Request failed - ID: {request_id} - Error: {str(e)}\n{traceback.format_exc()}")
        raise

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")

PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
if not PERPLEXITY_API_KEY:
    logger.warning("PERPLEXITY_API_KEY not found in environment variables")

class TextInput(BaseModel):
    text: str

def extract_json_for_against(response: str) -> list:
    logger.debug(f"Attempting to extract JSON from response of length: {len(response)}")
    try:
        cleaned_text = re.sub(r'```json\s*|\s*```', '', response.strip())
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
        logger.debug(f"Cleaned text sample: {cleaned_text[:200]}...")
        
        json_data = json.loads(cleaned_text)
        logger.debug(f"Successfully parsed JSON. Type: {type(json_data)}")

        if isinstance(json_data, dict):
            json_data = [json_data]
            logger.debug("Converted single dict to list")
        
        for_against_data = [item for item in json_data if "For" in item and "Against" in item]
        logger.debug(f"Found {len(for_against_data)} items with For/Against structure")
        
        if not for_against_data:
            error_msg = "No valid For/Against data found in response"
            logger.error(error_msg)
            raise CustomHTTPException(
                status_code=400,
                detail=error_msg,
                internal_error=f"Original response: {response[:200]}..."
            )
        
        return for_against_data
    
    except json.JSONDecodeError as e:
        error_msg = f"JSON parsing error at position {e.pos}: {e.msg}"
        logger.error(f"{error_msg}\nInput text: {e.doc[:200]}...")
        raise CustomHTTPException(
            status_code=400,
            detail=error_msg,
            internal_error=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error in extract_json_for_against: {str(e)}\n{traceback.format_exc()}")
        raise CustomHTTPException(
            status_code=500,
            detail="Internal server error while processing JSON data",
            internal_error=str(e)
        )

@app.post("/insights")
async def event_generate_v1(user_prompt: TextInput) -> Dict[str, Any]:
    request_id = os.urandom(6).hex()
    logger.info(f"Request ID {request_id} - Processing insights request for prompt: {user_prompt.text[:100]}...")
    
    try:
        logger.debug(f"Request ID {request_id} - Calling LLM overview")
        overview = llm_overview.call_llm(user_prompt, sot=[], recency="year")
        
        logger.debug(f"Request ID {request_id} - Calling LLM combined")
        combined = llm_combined.call_llm(user_prompt, sot=[], recency="year")
        
        logger.debug(f"Request ID {request_id} - Extracting For/Against data")
        arguments = extract_json_for_against(combined[0])
        
        response = {
            "overview": overview[0],
            "arguments": arguments,
            "overview_references": overview[1],
            "arguments_references": combined[1]
        }
        
        logger.info(f"Request ID {request_id} - Successfully processed insights request")
        return response

    except Exception as e:
        error_msg = f"Failed to process insights request: {str(e)}"
        logger.error(f"Request ID {request_id} - {error_msg}\n{traceback.format_exc()}")
        raise CustomHTTPException(
            status_code=500,
            detail=error_msg,
            internal_error=traceback.format_exc()
        )

@app.post("/search-tweets")
async def search_tweets(request: TextInput):
    request_id = os.urandom(6).hex()
    logger.info(f"Request ID {request_id} - Processing tweet search: {request.text[:100]}...")
    
    try:
        tweets = await fetch_tweets(request.text)
        logger.info(f"Request ID {request_id} - Successfully fetched {len(tweets)} tweets")
        return {"text": request.text, "tweets": tweets}
    
    except Exception as e:
        error_msg = f"Failed to fetch tweets: {str(e)}"
        logger.error(f"Request ID {request_id} - {error_msg}\n{traceback.format_exc()}")
        raise CustomHTTPException(
            status_code=500,
            detail=error_msg,
            internal_error=traceback.format_exc()
        )

@app.post("/get-insights")
async def post_index(payload: TextInput):
    request_id = os.urandom(6).hex()
    logger.info(f"Request ID {request_id} - Processing combined insights request: {payload.text[:100]}...")
    
    async with httpx.AsyncClient() as client:
        try:
            logger.debug(f"Request ID {request_id} - Fetching tweets")
            tweets_response = await client.post(
                "http://10.23.97.242:8506/search-tweets",
                json={"text": payload.text},
                timeout=30.0
            )
            tweets_response.raise_for_status()
            tweets_result = tweets_response.json()

            logger.debug(f"Request ID {request_id} - Fetching insights")
            analyze_response = await client.post(
                "http://10.23.97.242:8506/insights",
                json={"text": payload.text},
                timeout=30.0
            )
            analyze_response.raise_for_status()
            analyze_result = analyze_response.json()

            logger.debug(f"Request ID {request_id} - Fetching news")
            news_response = await client.post(
                "http://10.23.97.242:8506/search-news",
                json={"text": payload.text},
                timeout=30.0
            )
            news_response.raise_for_status()
            news_result = news_response.json()

            response = {
                "insights": analyze_result,
                "tweets": tweets_result,
                "news": news_result
            }
            
            logger.info(f"Request ID {request_id} - Successfully processed combined insights request")
            return response

        except httpx.TimeoutException as e:
            error_msg = "Request timed out while fetching data"
            logger.error(f"Request ID {request_id} - {error_msg}: {str(e)}")
            raise CustomHTTPException(
                status_code=504,
                detail=error_msg,
                internal_error=str(e)
            )
        except httpx.HTTPStatusError as e:
            error_msg = f"External service returned error status: {e.response.status_code}"
            logger.error(f"Request ID {request_id} - {error_msg}: {str(e)}")
            raise CustomHTTPException(
                status_code=502,
                detail=error_msg,
                internal_error=f"Response: {e.response.text}"
            )
        except Exception as e:
            error_msg = "Unexpected error processing insights request"
            logger.error(f"Request ID {request_id} - {error_msg}: {str(e)}\n{traceback.format_exc()}")
            raise CustomHTTPException(
                status_code=500,
                detail=error_msg,
                internal_error=traceback.format_exc()
            )

@app.post("/search-news")
def search_news(request: TextInput):
    request_id = os.urandom(6).hex()
    logger.info(f"Request ID {request_id} - Processing news search: {request.text[:100]}...")
    
    try:
        news = get_news(request.text)
        logger.info(f"Request ID {request_id} - Successfully fetched news results")
        return news
    
    except Exception as e:
        error_msg = "Failed to fetch news"
        logger.error(f"Request ID {request_id} - {error_msg}: {str(e)}\n{traceback.format_exc()}")
        raise CustomHTTPException(
            status_code=500,
            detail=error_msg,
            internal_error=traceback.format_exc()
        )

@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    request_id = os.urandom(6).hex()
    logger.info(f"Request ID {request_id} - Rendering frontend index page")
    return templates.TemplateResponse("frontend.html", {"request": request})

@app.post("/", response_class=HTMLResponse)
async def post_index(request: Request, text: str = Form(...)):
    request_id = os.urandom(6).hex()
    logger.info(f"Request ID {request_id} - Processing frontend form submission: {text[:100]}...")
    
    try:
        async with httpx.AsyncClient() as client:
            logger.debug(f"Request ID {request_id} - Fetching tweets")
            tweets_response = await client.post(
                "http://10.23.97.242:8506/search-tweets",
                json={"text": create_query(text)},
                timeout=30.0
            )
            tweets_response.raise_for_status()
            tweets_result = tweets_response.json()

            logger.debug(f"Request ID {request_id} - Fetching insights")
            analyze_response = await client.post(
                "http://10.23.97.242:8506/insights",
                json={"text": text},
                timeout=30.0
            )
            analyze_response.raise_for_status()
            analyze_result = analyze_response.json()

            logger.debug(f"Request ID {request_id} - Fetching news")
            news_response = await client.post(
                "http://10.23.97.242:8506/search-news",
                json={"text": text},
                timeout=30.0
            )
            news_response.raise_for_status()
            news_result = news_response.json()

        logger.info(f"Request ID {request_id} - Successfully processed frontend request")
        return templates.TemplateResponse(
            "frontend.html",
            {
                "request": request,
                "text": text,
                "tweets": tweets_result,
                "analysis": analyze_result,
                "news": news_result,
            },
        )

    except httpx.TimeoutException as e:
        error_msg = "Request timed out while fetching data"
        logger.error(f"Request ID {request_id} - {error_msg}: {str(e)}")
        raise CustomHTTPException(
            status_code=504,
            detail=error_msg,
            internal_error=str(e)
        )
    except httpx.HTTPStatusError as e:
        error_msg = f"External service returned error status: {e.response.status_code}"
        logger.error(f"Request ID {request_id} - {error_msg}: {str(e)}")
        raise CustomHTTPException(
            status_code=502,
            detail=error_msg,
            internal_error=f"Response: {e.response.text}"
        )
    except Exception as e:
        error_msg = "Unexpected error processing frontend request"
        logger.error(f"Request ID {request_id} - {error_msg}: {str(e)}\n{traceback.format_exc()}")
        raise CustomHTTPException(
            status_code=500,
            detail=error_msg,
            internal_error=traceback.format_exc()
        )

if __name__ == '__main__':
    logger.info("="*50)
    logger.info("Starting FastAPI server")
    logger.info(f"Server URL: http://10.23.97.242:8506")
    logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    logger.info("="*50)
    uvicorn.run(app)
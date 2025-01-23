from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from twitter_query_search import fetch_tweets
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Define the input schema for the request
class QueryRequest(BaseModel):
    query: str

# Create FastAPI app
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)


@app.post("/search-tweets")
async def search_tweets(request: QueryRequest):
    try:
        query = request.query
        q = {"query" : query}   
        tweets = await fetch_tweets(q['query'])  # Call the function from your module
        return {"query": query, "tweets": tweets}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

# Start the application on localhost:8002
if __name__=='__main__':
    import uvicorn
    uvicorn.run(app,host="127.0.0.1",port=8002)

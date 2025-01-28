from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from WEB_SEARCH import get_news
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


@app.post("/search-news")
def search_tweets(request: QueryRequest):
    query = request.query
    news = get_news(query)
    return(news)

# Start the application on localhost:8002
if __name__=='__main__':
    import uvicorn
    uvicorn.run(app,host="127.0.0.1",port=8004)

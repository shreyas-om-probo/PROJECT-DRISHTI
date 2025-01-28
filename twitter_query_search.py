import asyncio
import os
import json
from typing import List, Tuple
from dotenv import load_dotenv
from twikit import Client
from datetime import datetime
import regex as re

load_dotenv()
USERNAME = "Prabhav199653"
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
COOKIES_FILE = 'cookies.json'

async def login_or_load_cookies(client: Client):
    """Logs in or loads cookies, with a fallback to recreate cookies if loading fails."""
    try:
        if os.path.exists(COOKIES_FILE):
            try:
                client.load_cookies(COOKIES_FILE)
                print("Loaded cookies successfully.")
                return
            except Exception as e:
                print(f"Error loading cookies: {e}")
                os.remove(COOKIES_FILE)  # Remove invalid cookies file
        
        # Perform login and save new cookies
        print("Logging in...")
        await client.login(
            auth_info_1=USERNAME,
            auth_info_2=EMAIL,
            password=PASSWORD
        )
        client.save_cookies(COOKIES_FILE)
        print("Login successful and new cookies saved.")
    
    except Exception as e:
        print(f"Login failed: {e}")
        raise

def extract_tweet_link(tweet):
    lines = re.split(r'[ \n]+', tweet.strip())
    if lines and lines[-1].startswith('https://t.co/'):
        link = lines.pop()
        text_without_link = ' '.join(lines).strip()
        return text_without_link, link
    return tweet, None

async def fetch_tweets(query: str) -> List[Tuple[str, str, str, str, int]]:
    """Fetches tweets for a given query."""
    client = Client('en-US')
    await login_or_load_cookies(client)

    print(f"Searching for tweets containing: {query}")
    tweets = await client.search_tweet(query=query, product='Top')

    tweets_data = [
        {
            'ID': str(tweet.id), 
            'TEXT': extract_tweet_link(tweet.text)[0], 
            'DATA': str(tweet.created_at), 
            'USER_ID': str(tweet.user), 
            'VIEW_COUNT': tweet.view_count,
            'LIKE_COUNT': tweet.favorite_count, 
            'LINK': extract_tweet_link(tweet.text)[1]
        }
        for tweet in tweets
    ]

    tweets_data.sort(key=lambda x: datetime.strptime(x['DATA'], "%a %b %d %H:%M:%S %z %Y"), reverse=True)

    return tweets_data

# Example usage
if __name__ == "__main__":
    query = "Python programming"
    
    async def main():
        tweets = await fetch_tweets(query)
        print(f"Fetched {len(tweets)} tweets.")
        print(json.dumps(tweets, indent=2, ensure_ascii=False))

    asyncio.run(main())
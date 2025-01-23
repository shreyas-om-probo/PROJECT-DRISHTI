from dotenv import load_dotenv
import os
import json
import requests
import regex as re
from pydantic import BaseModel
load_dotenv()

PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
url = "https://api.perplexity.ai/chat/completions"

class TextInput(BaseModel):
    text: str

def return_json(response):
    if response.status_code == 200:
        try:
            data_dict = json.loads(response.text)
            return(data_dict) 
        except json.JSONDecodeError as e:
            return(f"Error decoding JSON: {e}")
    else:
        return(f"Request failed with status code: {response.status_code}")

def create_message_prompt(user_prompt):
    messages = [
        {
            "role": "system",
            "content": (
                "You are an expert analyst tasked with providing detailed, concise, and structured insights about events. "
                "Your response must be in HTML format and address the following clearly and succinctly:"
                "   - A brief history of the event (including context and background)."
                "   - What the event is specifically about."
                "   - The key acting parties involved in the event."
                "   - Why the event is significant or relevant."
                "Ensure your response is strictly limited to the requested details and avoid including any references or additional commentary. "
                "Keep the response crisp, focused, and within 5 lines of content."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Provide a detailed, HTML-formatted response for the following event: {user_prompt.text}."
                "It should be in a pargraph format and not in points format."
                "Ensure the history, details, and significance are addressed within 50-100 words and in a short crisp manner."
                "Keep the views statstically backed supporting the probability of events."
            ),
        },
    ]
    return messages

def call_llm(event_details,sot,recency):
    print(event_details)
    payload = {
        "model": "llama-3.1-sonar-small-128k-online",
        "messages": create_message_prompt(event_details),
        "temperature": 0,
        "search_domain_filter": sot,
        "search_recency_filter" :recency
    }


    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.request("POST", url, json=payload, headers=headers)
    response = return_json(response)
    print(response)
    return response['choices'][0]['message']['content']

if __name__=='__main__':
    print(call_llm(event_details="Germany Parliamentary Election Winner.",sot=["www.fancode.com"],recency="hour"))  

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

# def create_message_prompt(user_prompt):
#     messages = [
#         {
#             "role": "system",
#             "content": (
#                 "You are an expert analyst providing precise and well-structured insights on events. "
#                 "Your response must include a brief historical background, the key details of the event, the major participants involved, and its significance, all written in a single concise paragraph. "
#                 "Keep the response between 50-100 words, ensuring factual accuracy and historical/statistical backing. "
#                 "The text should be objective, to the point, and strictly plain text with no headings, formatting, or additional commentary."
#             ),
#         },
#         {
#             "role": "user",
#             "content": (
#                 f"Provide an overview of the following event: {user_prompt.text}. "
#                 "Ensure historical context, details, and significance are addressed concisely in a single paragraph. "
#                 "Verify correctness before responding, ensuring statistical and historical accuracy."
#             ),
#         },
#     ]
#     return messages

def create_message_prompt(user_prompt):
    messages = [
        {
            "role": "system",
            "content": (
                "You are an expert analyst providing **concise, well-structured, and factual overviews** of upcoming events. "
                "Your response must be a **single, cohesive paragraph** (50-100 words) that seamlessly integrates:\n"
                "- **Key details of the upcoming event** (what, when, where, and who is involved).\n"
                "- **Relevant historical insights** that provide context or precedent for the event.\n\n"
                
                "**Guidelines:**\n"
                "- The response must be **objective, accurate, and fact-based**.\n"
                "- Maintain a **smooth, natural flow**—do **not** separate the event details and history into distinct parts.\n"
                "- Keep the format **strictly plain text**—no headings, bullet points, or extra commentary.\n"
                "- Verify **historical/statistical accuracy** before responding.\n\n"
            ),
        },
        {
            "role": "user",
            "content": (
                f"Provide a single cohesive paragraph summarizing the following upcoming event: {user_prompt.text}. "
                "Ensure the response integrates both key event details and historical context in 50 words, maintaining factual accuracy."
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

    return [response['choices'][0]['message']['content'],response['citations']]

if __name__ == '__main__':
    event_details = TextInput(text="Germany Parliamentary Election Winner.")
    sot = ["www.fancode.com"]
    recency = "hour"
    result = call_llm(event_details, sot, recency)
    print(result)
    print(json.dumps(result, indent=4))


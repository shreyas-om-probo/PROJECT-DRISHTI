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
            return data_dict
        except json.JSONDecodeError as e:
            return {"error": f"Error decoding JSON: {e}"}
    else:
        return {"error": f"Request failed with status code: {response.status_code}"}
    
def read_example_file(input="example.txt"):
    with open(input, 'r') as file:
        text = file.read()
    return text

def create_message_prompt(user_prompt):
    messages = [
        {
            "role": "system",
            "content": (
                "You are an artificial intelligence assistant tasked with evaluating an event from two opposing perspectives: "
                "1) providing points in favor of the event, and 2) providing points against the event. "
                "Your goal is to provide **highly polarizing views** with a focus on the conditions or factors that could either enable the event to succeed or cause it to fail entirely. "
                "The output should be valid JSON with the following fields:"
                "- **For**: A JSON object containing a list of points that strongly support the event, under a key named 'points'."
                                "The response must focus exclusively on providing **3 concrete, evidence-backed points** that strongly support the event or highlight conditions or actions that could make it successful."
                "- **Against**: A JSON object containing a list of points that strongly oppose the event, under a key named 'points'."
                                "The response must focus exclusively on providing **3 concrete, evidence-backed points** that highlight risks, obstacles, or factors that could lead to the event's failure."
                "The points should strictly be HTML formatted strings."
                f"Example of the proper format:{read_example_file()}"
                "Ensure the output is following the above given guidelines."
                "Ensure the tone is engaging and emphasizes extremes in support or opposition, highlighting practical outcomes."
                "Do not add any other explanations or context outside the JSON object."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Evaluate the following event from both perspectives: {user_prompt.text}."
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
        "Authorization": "Bearer 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",
        "Content-Type": "application/json"
    }
    
    response = requests.request("POST", url, json=payload, headers=headers)
    response = return_json(response)
    print(response)

    return response['choices'][0]['message']['content']


if __name__ == '__main__':
    event_details = TextInput(text="Germany Parliamentary Election Winner.")
    sot = ["www.fancode.com"]
    recency = "hour"
    result = call_llm(event_details, sot, recency)
    print(result)
    print(json.dumps(result, indent=4))

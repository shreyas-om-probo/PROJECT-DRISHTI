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

# def create_message_prompt(user_prompt):
#     messages = [
#         {
#             "role": "system",
#             "content": (
#                 "You are an artificial intelligence assistant tasked with evaluating an event from two opposing perspectives: "
#                 "1) providing points in favor of the event, and 2) providing points against the event. "
#                 "Your goal is to provide **highly polarizing views** with a focus on the conditions or factors that could either enable the event to happen or cause it to fail (not happen). "
#                 "The output should be valid JSON with the following fields:"


#                 "- **For**: A JSON object containing a list of points that strongly support the event happening, under a key named 'points'."
#                                 "The response must focus exclusively on providing **concrete, evidence-backed points** that strongly support the event's happening or highlight conditions or actions that could make it happen."
#                 "- **Against**: A JSON object containing a list of points that strongly oppose the event, under a key named 'points'."
#                                 "The response must focus exclusively on providing **concrete, evidence-backed points** that highlight risks, obstacles, or factors that could lead to the event not happening."


#                 "The response format should be like:"
#                 "'''json{\n"
#                 '  "For": {\n'
#                 '    "points": [\n'
#                 '      "Strong Supporting in HTML format.",\n'
#                 '      "Strong Supporting in HTML format.",\n'
#                 '      "Strong Supporting in HTML format.",\n'
#                 '    ]\n'
#                 '  },\n'
#                 '  "Against": {\n'
#                 '    "points": [\n'
#                 '      "Strong Opposing in HTML format.",\n'
#                 '      "Strong Opposing in HTML format.",\n'
#                 '      "Strong Opposing in HTML format.",\n'
#                 '    ]\n'
#                 '  }\n'
#                 "}'''\n\n"


#                 f"Example of the proper format:{read_example_file()}"
#                 "Ensure the output is following the above given guidelines."
#                 "Ensure the tone is engaging and emphasizes extremes in support or opposition, highlighting practical outcomes."
#                 "Do not add any other explanations or context outside the JSON object."
#             ),
#         },
#         {
#             "role": "user",
#             "content": (
#                 f"Evaluate the following event from both perspectives: {user_prompt.text}."
#             ),
#         },
#     ]
#     return messages

# def create_message_prompt(user_prompt):
#     messages = [
#         {
#             "role": "system",
#             "content": (
#                 "You are an AI assistant specializing in **highly polarizing analysis** of events. "
#                 "Your task is to evaluate the likelihood of an event happening from two extreme perspectives: \n"
#                 "1) **FOR** (Why the event is highly likely to happen) \n"
#                 "2) **AGAINST** (Why the event is highly unlikely to happen) \n\n"
                
#                 "**Requirements:**\n"
#                 "- Provide **strong, concrete, and justified arguments** in both perspectives.\n"
#                 "- Focus on **factual, logical, and strategic** reasons rather than personal opinions.\n"
#                 "- Use **historical precedents, financial considerations, legal frameworks, and technological feasibility** to justify each point.\n"
#                 "- Do **not** hedge between positions. Each perspective should be **extreme and well-argued**.\n\n"
                
#                 "The response format should be like:"
#                 "'''json{\n"
#                 '  "For": {\n'
#                 '    "points": [\n'
#                 '      "Strong Supporting in HTML format.",\n'
#                 '      "Strong Supporting in HTML format.",\n'
#                 '      "Strong Supporting in HTML format.",\n'
#                 '    ]\n'
#                 '  },\n'
#                 '  "Against": {\n'
#                 '    "points": [\n'
#                 '      "Strong Opposing in HTML format.",\n'
#                 '      "Strong Opposing in HTML format.",\n'
#                 '      "Strong Opposing in HTML format.",\n'
#                 '    ]\n'
#                 '  }\n'
#                 "}'''\n\n"
                
#                 "**Guidelines for Points:**\n"
#                 "- Each argument should be **specific, realistic, and backed by evidence** (financial, legal, strategic, or technological factors).\n"
#                 "- Avoid weak, vague, or overly general statements. Every point should be **impactful** and **persuasive**. if any point is not upto the mark then avoid listing it.\n"
#                 "- Do **not** provide additional commentary outside the JSON format.\n\n"

#                 f"Example response:\n{read_example_file()}"
#             ),
#         },
#         {
#             "role": "user",
#             "content": (
#                 f"Evaluate the following event from both perspectives: {user_prompt.text}."
#             ),
#         },
#     ]
#     return messages

def create_message_prompt(user_prompt):
    messages = [
        {
            "role": "system",
            "content": (
                "You are an AI assistant specializing in **highly polarizing analysis** of events. "
                "Your task is to evaluate the likelihood of an event happening from two extreme perspectives:\n"
                "1) **FOR** (Why the event is highly likely to happen)\n"
                "2) **AGAINST** (Why the event is highly unlikely to happen)\n\n"

                "**Requirements:**\n"
                "- Each argument must be **highly compelling, factually supported, and unique**.\n"
                "- **Quality over quantity**: If strong, distinct arguments are not available, **do not force weak or repetitive points**.\n"
                "- Focus on **strategic, financial, legal, historical, and technological** factors.\n"
                "- Avoid **hedging, weak phrasing, or redundant arguments**—each perspective should be **strong and extreme**.\n\n"
                
                "The response format should be like:"
                "'''json{\n"
                '  "For": {\n'
                '    "points": [\n'
                '      "Strong Supporting in HTML format.",\n'
                '      "Strong Supporting in HTML format.",\n'
                '      "Strong Supporting in HTML format.",\n'
                '    ]\n'
                '  },\n'
                '  "Against": {\n'
                '    "points": [\n'
                '      "Strong Opposing in HTML format.",\n'
                '      "Strong Opposing in HTML format.",\n'
                '      "Strong Opposing in HTML format.",\n'
                '    ]\n'
                '  }\n'
                "}'''\n\n"

                "**Guidelines for Each Argument:**\n"
                "- Must be **specific, impactful, and backed by strong evidence** (financial, legal, historical, strategic, or technological precedents).\n"
                "- Avoid **vague or weak arguments**—only list points that have **real, actionable evidence**.\n"
                "- Each point should be **no more than 10 words**.\n"
                "- **No additional commentary**—only the JSON response is allowed.\n\n"

                "**Example response:**\n"
                f"{read_example_file()}"
            ),
        },
        {
            "role": "user",
            "content": (
                f"Evaluate the following event from both perspectives: {user_prompt.text}."
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

    return [response['choices'][0]['message']['content'],response['citations']]

if __name__ == '__main__':
    event_details = TextInput(text="Germany Parliamentary Election Winner.")
    sot = ["www.fancode.com"]
    recency = "hour"
    result = call_llm(event_details, sot, recency)
    print(result)
    print(json.dumps(result, indent=4))

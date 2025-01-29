import requests
from datetime import datetime
from dateutil.relativedelta import relativedelta
import json
import requests
from CREATE_SEARCH_QUERY import create_query
from dotenv import load_dotenv
import os
load_dotenv()

API_KEY = os.getenv("API_KEY")
CX = os.getenv("CX")

def google_custom_search(api_key, cx, query, num_results=10):
    """
    Perform a Google Custom Search API request.

    Parameters:
        api_key (str): API key for Google Custom Search API.
        cx (str): Custom search engine ID.
        query (str): The search query string.
        date_restrict (str): Restrict results to specific dates (e.g., "2024-11-27").
        num_results (int): Number of results to retrieve. Default is 10.

    Returns:
        dict: Parsed JSON response from the API.
    """
    two_months_prior = datetime.now() - relativedelta(months=2)
    two_months_prior = two_months_prior.strftime('%Y-%m-%d')
    query = create_query(query)

    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": api_key,
        "cx": cx,
        "q": query,
        "hq": "news",
        "dateRestrict": 'm2',
        "num": num_results,
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()

def extract_needed_results(search_results):
    all_results = search_results["items"]
    refined_outputs = []
    for i in all_results:
        result = {}
        result['link'] = i['link']
        result['source'] = i["displayLink"]
        result['title'] = i['title']
        try:
            result['text'] = i['pagemap']['metatags'][0]['og:description']
            result['thumbnail'] = i['pagemap']['metatags'][0]['og:image']
        except:
            result['text'] = i['snippet']
            result['thumbnail'] = "NULL"
        result['date'] = i['snippet'].split("...")[0]
        refined_outputs.append(result)
    return refined_outputs

def get_news(QUERY):
    try:
        results = google_custom_search(API_KEY, CX, QUERY)
        print(results)
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
    
    results = google_custom_search(API_KEY, CX, QUERY)

    with open(QUERY+'.json', 'w') as json_file:
        json.dump(results, json_file, indent=4)

    return(extract_needed_results(results))

# Example usage:
if __name__ == "__main__":
    QUERY = 'Who will win most GRAMMY, Beyonce or Taylor?'

    try:
        results = google_custom_search(API_KEY, CX, QUERY)
        print(results)
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
    
    results = google_custom_search(API_KEY, CX, QUERY)

    with open(QUERY+'.json', 'w') as json_file:
        json.dump(results, json_file, indent=4)

    print(extract_needed_results(results))
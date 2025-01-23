import spacy
import re
from datetime import datetime
from dateutil.relativedelta import relativedelta

# Load the spaCy language model
nlp = spacy.load("en_core_web_lg")

import spacy

# Load the spaCy language model
nlp = spacy.load("en_core_web_lg")

def identify_keywords(sentence):
    """
    Identifies the most important keywords in a sentence, excluding datetime-related words.
    Verbs are lemmatized to their root form.
    """
    # List of datetime-related keywords to ignore
    datetime_keywords = {"before", "after", "on", "since", "until", "within", "months", "week", "time", "date", "year", "today", "tomorrow", "yesterday", "december", "january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november"}
    
    doc = nlp(sentence)
    keywords = [
        token.lemma_ if token.pos_ == "VERB" else token.text
        for token in doc
        if token.pos_ in {"VERB", "PROPN", "NOUN"} and token.text.lower() not in datetime_keywords
    ]
    
    try:
        keywords.remove('end')  # Avoids removing 'end' if not present
    except ValueError:
        pass

    return keywords



def create_query(sentence):
#{"query" : "('Beyoncé' AND 'Taylor Swift' AND 'GRAMMY') since:2024-12-12"}
    keywords = identify_keywords(sentence)
    if len(keywords)>=2:
        query = f"('{keywords[0]}' "
        for keyword in keywords[1:]:
            query = query + f"AND '{keyword}' "
        query = query +")"
    elif len(keywords)!=0:
        query = f"('{keywords[0]}')"
    else:
        query = " "
        
    two_months_prior = datetime.now() - relativedelta(months=2)
    query += f" since:{two_months_prior.strftime('%Y-%m-%d')}"
    
    return query
if __name__ == "__main__":
    sentence = "virat retiring before 2026?"
    # sentence = "Will Beyonce win more grammies than taylor swift?"
    print("Keywords:", identify_keywords(sentence))
    print("query",create_query(sentence))

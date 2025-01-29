import nltk
import ssl
import re
from datetime import datetime
from dateutil.relativedelta import relativedelta
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk import pos_tag

# SSL Context Fix
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

# Download required NLTK data files with error handling
def download_nltk_resources():
    resources = ['punkt', 'wordnet', 'stopwords', 'averaged_perceptron_tagger', 'averaged_perceptron_tagger_eng']
    for resource in resources:
        try:
            nltk.download(resource)
            print(f"Successfully downloaded {resource}")
        except Exception as e:
            print(f"Error downloading {resource}: {e}")

# Call the download function
download_nltk_resources()

# List of datetime-related keywords to ignore
datetime_keywords = {"before", "after", "on", "since", "until", "within", "months", "week", "time", "date", "year", "today", "tomorrow", "yesterday", "december", "january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november"}

# Initialize the lemmatizer
lemmatizer = WordNetLemmatizer()

def identify_keywords(sentence):
    """
    Identifies the most important keywords in a sentence, excluding datetime-related words.
    Verbs are lemmatized to their root form.
    """
    # Tokenize the sentence
    tokens = word_tokenize(sentence)
    
    # POS tagging
    pos_tags = pos_tag(tokens)
    
    keywords = []
    for word, pos in pos_tags:
        # Filter out stopwords and datetime-related words
        if word.lower() not in stopwords.words("english") and word.lower() not in datetime_keywords:
            # Lemmatize verbs, keep nouns and proper nouns as they are
            if pos.startswith('V'):
                keywords.append(lemmatizer.lemmatize(word, pos='v'))
            elif pos.startswith('N') or pos.startswith('PROPN'):
                keywords.append(word)
    
    # Remove 'end' if it's present (to avoid unnecessary keywords)
    try:
        keywords.remove('end')
    except ValueError:
        pass

    return keywords

def create_query(sentence):
    """
    Creates a query using the identified keywords, and appends a date filter to the query.
    The query will only include results from the last 2 months.
    """
    keywords = identify_keywords(sentence)
    
    if len(keywords) >= 2:
        query = f"'{keywords[0]}' "
        for keyword in keywords[1:]:
            query = query + f"AND '{keyword}' "
    elif len(keywords) != 0:
        query = f"'{keywords[0]}'"
    else:
        query = " "
    
    return query +"inurl:news"

if __name__ == "__main__":
    sentence = "Who will win most GRAMMY, Beyonce or Taylor?"
    print("Keywords:", identify_keywords(sentence))
    print("Query:", create_query(sentence))
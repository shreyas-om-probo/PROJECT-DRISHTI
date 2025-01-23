from flask import Flask, request, render_template, jsonify
import requests
from CREATE_QUERY import create_query
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        text = request.form.get('text')

        # Fetch tweets
        tweets_response = requests.post('http://127.0.0.1:8002/search-tweets', json={"query": create_query(text)})
        tweets_result = tweets_response.json()

        # Analyze text
        analyze_response = requests.post('http://127.0.0.1:8003/insights', json={"text": text})
        analyze_result = analyze_response.json()

        return render_template('mono.html', text=text, tweets=tweets_result, analysis=analyze_result)

    return render_template('mono.html')

if __name__ == '__main__':
    app.run(debug=True)
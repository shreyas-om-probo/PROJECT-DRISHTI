from flask import Flask, request, render_template_string, jsonify
import requests

app = Flask(__name__)

# HTML templates as strings
INDEX_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Text Analysis</title>
</head>
<body>
    <h1>Enter Text for Analysis</h1>
    <form method="POST">
        <textarea name="text" rows="4" cols="50"></textarea><br>
        <button type="submit">Submit</button>
    </form>
</body>
</html>
"""

RESULTS_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Analysis Results</title>
</head>
<body>
    <h1>Results for: {{ text }}</h1>

    <h2>Tweets:</h2>
    <pre>{{ tweets | tojson(indent=4) }}</pre>

    <h2>Analysis:</h2>
    <pre>{{ analysis | tojson(indent=4) }}</pre>

    <a href="/">Go Back</a>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        text = request.form.get('text')

        # Fetch tweets
        tweets_response = requests.post('http://127.0.0.1:8002/search-tweets', json={"query": "('Beyoncé' AND 'Taylor Swift' AND 'GRAMMY') since:2024-12-12"})
        tweets_result = tweets_response.json()

        # Analyze text
        analyze_response = requests.post('http://127.0.0.1:8003/insights', json={"text": text})
        analyze_result = analyze_response.json()

        return render_template_string(RESULTS_HTML, text=text, tweets=tweets_result, analysis=analyze_result)

    return render_template_string(INDEX_HTML)

if __name__ == '__main__':
    app.run(debug=True)

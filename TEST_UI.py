from flask import Flask, render_template, jsonify, request
import requests

app = Flask(__name__)

@app.route('/get-tweet', methods=['GET'])
def tweets():
    data = {"query" : "('Beyoncé' AND 'Taylor Swift' AND 'GRAMMY') since:2024-12-12"}
    response = requests.post('http://127.0.0.1:8002/search-tweets', json=data)
    return jsonify(response.json())

@app.route('/analyze', methods=['GET'])
def analyze():
    data = {"text" : "Who will win most GRAMMY, Beyonce or Taylor?"}
    response = requests.post('http://127.0.0.1:8003/insights', json=data)
    return jsonify(response.json())

if __name__ == '__main__':
    app.run(debug=True, port=5000)
from flask import Flask, request, jsonify, render_template
import openai
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Initialize OpenAI and Weather.com API keys
openai.api_key = os.getenv('OPENAI_API_KEY')
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')

# Placeholder for city management
cities = {}
current_city = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message')
    # TODO: Implement ChatGPT interaction and weather API calls
    return jsonify({'response': 'Chat and weather functionality will be implemented here'})

if __name__ == '__main__':
    app.run(debug=True)

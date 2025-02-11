from flask import Flask, request, jsonify, render_template
import openai
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Initialize API keys
openai.api_key = os.getenv('OPENAI_API_KEY')
ACCUWEATHER_API_KEY = os.getenv('ACCUWEATHER_API_KEY')

# AccuWeather API endpoints
ACCUWEATHER_BASE_URL = 'http://dataservice.accuweather.com'

# City management
cities = {}
current_city = None

# ChatGPT model
CHATGPT_MODEL = 'gpt-4o-mini'


def get_location_key(city_name):
    url = f'{ACCUWEATHER_BASE_URL}/locations/v1/cities/search'
    params = {
        'apikey': ACCUWEATHER_API_KEY,
        'q': city_name,
        'language': 'en-us'
    }
    response = requests.get(url, params=params)
    if response.status_code == 200 and response.json():
        return response.json()[0]['Key']
    return None


def get_current_weather(location_key):
    url = f'{ACCUWEATHER_BASE_URL}/currentconditions/v1/{location_key}'
    params = {
        'apikey': ACCUWEATHER_API_KEY,
        'details': 'true',
        'language': 'en-us'
    }
    response = requests.get(url, params=params)
    if response.status_code == 200 and response.json():
        return response.json()[0]
    return None


def process_chatgpt_query(user_input, weather_data):
    prompt = f'''Given the following weather data:
{weather_data}

Answer the user's question: {user_input}'''

    response = openai.ChatCompletion.create(
        model=CHATGPT_MODEL,
        messages=[
            {'role': 'system', 'content': 'You are a helpful weather assistant.'},
            {'role': 'user', 'content': prompt}
        ],
        temperature=0.7
    )
    return response.choices[0].message.content


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/cities', methods=['GET'])
def get_cities():
    return jsonify({
        'cities': list(cities.keys()),
        'current_city': current_city
    })


@app.route('/cities', methods=['POST'])
def add_city():
    city_name = request.json.get('city_name')
    if not city_name:
        return jsonify({'error': 'City name is required'}), 400

    location_key = get_location_key(city_name)
    if not location_key:
        return jsonify({'error': 'Could not find city'}), 404

    cities[city_name] = location_key
    return jsonify({'message': f'Added {city_name}'}), 201


@app.route('/cities/<city_name>', methods=['DELETE'])
def remove_city(city_name):
    if city_name not in cities:
        return jsonify({'error': 'City not found'}), 404

    del cities[city_name]
    if current_city == city_name:
        global current_city
        current_city = None
    return jsonify({'message': f'Removed {city_name}'})


@app.route('/cities/current', methods=['POST'])
def set_current_city():
    city_name = request.json.get('city_name')
    if city_name not in cities:
        return jsonify({'error': 'City not found'}), 404

    global current_city
    current_city = city_name
    return jsonify({'message': f'Set current city to {city_name}'})


@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message')
    
    if not current_city:
        return jsonify({'response': 'Please set a city first'})

    location_key = get_location_key(current_city)
    if not location_key:
        return jsonify({'response': 'Could not find weather data for this city'})

    weather_data = get_current_weather(location_key)
    if not weather_data:
        return jsonify({'response': 'Could not fetch weather data'})

    response = process_chatgpt_query(user_input, weather_data)
    return jsonify({'response': response})


if __name__ == '__main__':
    app.run(debug=True)

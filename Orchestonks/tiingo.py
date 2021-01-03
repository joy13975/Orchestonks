import requests
import json

with open('config/tiingo.json', 'r') as f:
    tiingo_config = json.load(f)
token = tiingo_config['api_token']
headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Token {token}'
}
requestResponse = requests.get(
    f'https://api.tiingo.com/api/test/',
    headers=headers)
print(requestResponse.json())

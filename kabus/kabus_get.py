import json
import requests
import yaml
from pprint import pprint

# ---

def get_token():
    with open('auth.yaml', 'r') as yml:
        auth = yaml.safe_load(yml)

    url = 'http://localhost:18080/kabusapi/token'
    headers = {'content-type': 'application/json'}
    payload = json.dumps(
        {'APIPassword': auth['PASS'],}
        ).encode('utf8')

    response = requests.post(url, data=payload, headers=headers)

    return json.loads(response.text)['Token']

# ---

token = get_token()
print(token)

url = 'http://localhost:18080/kabusapi/board/9433@1'
headers = {'Content-Type': 'application/json', 'X-API-KEY': token,}
response = requests.get(url, headers=headers)

pprint(json.loads(response.text))

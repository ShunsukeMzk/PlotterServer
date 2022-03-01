import json
import requests
import yaml

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
    print(response.text)
    return json.loads(response.text)['Token']

# ---

token = get_token()

url = 'http://localhost:18080/kabusapi/unregister/all'
headers = {'Content-Type': 'application/json', 'X-API-KEY': token,}
response = requests.put(url, headers=headers)

print(json.loads(response.text))

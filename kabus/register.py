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

EXCHANGES = {
    1: '東証',
    3: '名証',
    5: '福証',
    6: '札証',
}

payload = json.dumps({
    'Symbols': [
        {'Symbol': 9983 ,'Exchange': 1},  # ファーストリテイリング
        # ... 50件まで登録可
    ],}).encode('utf8')

url = 'http://localhost:18080/kabusapi/register'
headers = {'Content-Type': 'application/json', 'X-API-KEY': token,}
response = requests.put(url, payload, headers=headers)

regist_list = json.loads(response.text)

print('配信登録銘柄')
for regist in regist_list['RegistList']:
    print("{} {}".format(
        regist['Symbol'],
        EXCHANGES[regist['Exchange']]))

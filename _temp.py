
import requests

response = requests.get("http://192.168.1.17:5000/kabusapi/ranking?type=2")
print(response.text)

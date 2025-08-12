import requests

url = "http://127.0.0.1:8000/jsonrpc/"
payload = {
    "jsonrpc": "2.0",
    "method": "ping",
    "id": 1
}
r = requests.post(url, json=payload)
print(r.text)

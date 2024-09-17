import requests

proxies = {
    'http': 'http://127.0.0.1:9000',
    'https': 'http://127.0.0.1:9000',
}
response = requests.get('http://google.com', proxies=proxies)
print(response)
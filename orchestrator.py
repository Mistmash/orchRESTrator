import requests

URL = 'https://3eb8d0f8-8826-41eb-a609-9e1ab92a0384.mock.pstmn.io/'
statusURL = URL + 'status'
startURL = URL + 'start'
stopURL = URL + 'stop'

print(statusURL)
print(startURL)
print(stopURL)

response = requests.get(statusURL)
print(response)

response = requests.post(startURL)
print(response)

response = requests.post(stopURL)
print(response)

print("Windows Git")
import requests
import json

# Login to get token
response = requests.post('http://127.0.0.1:8767/api/v1/auth/login', json={
    'ai_id': 21,
    'ai_name': 'TwoWayCommAI',
    'ai_nickname': 'TwoWay'
})
token = response.json()['token']

# Test GET brain state
response = requests.get('http://127.0.0.1:8767/api/v1/brain/state',
    headers={'Authorization': f'Bearer {token}'}
)
print('GET brain state status:', response.status_code)
print('GET brain state response:', response.json())

# Test PUT brain state
response = requests.put('http://127.0.0.1:8767/api/v1/brain/state',
    headers={'Authorization': f'Bearer {token}'},
    json={'task': 'Test task', 'last_thought': 'Test thought'})
print('PUT brain state status:', response.status_code)
print('PUT brain state response:', response.json())

import json
from http import client

def get_user(request):
	conn = client.HTTPConnection('users:8000')
	conn.request('GET', '/get_user/', request.body, request.headers)
	response = conn.getresponse()
	if response.status != 200:
		return None
	return json.loads(response.read().decode())

def get_user_with_token(auth_token, csrf_token):
	conn = client.HTTPConnection('users:8000')
	conn.request('GET', '/get_user/', None, {
		'Authorization': 'Bearer ' + auth_token,
		'X-CSRFToken': csrf_token
	})
	response = conn.getresponse()
	if response.status != 200:
		return None
	return json.loads(response.read().decode())

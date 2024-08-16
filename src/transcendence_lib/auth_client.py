from django.utils.deprecation import MiddlewareMixin
from django.utils.functional import SimpleLazyObject

from .models import User
from django.conf import settings

import json
from os import environ
from http import client

def api_call(self, method, url, body=None, headers={}):
		conn = client.HTTPConnection(self._url)
		try:
			conn.request(method, url, body, headers)
			response = conn.getresponse()
			return response.status, json.loads(response.read().decode())
		finally:
			conn.close()

class AuthenticationClient:
	def __init__(self) -> None:
		self._auth_url = environ.get('auth_url')
	
	def _to_user_model(self, status, data):
		if status != 200 and status != 201:
			return None
		return User(
			id=data['id'], 
			username=data['username'], 
			password=data['password'], 
			is_42=data['is_42'])

	def authenticate(self, request, **credentials):
		# Your custom authentication logic goes here
		# Example: authenticate against an external service
		data = json.dumps(credentials)
		return self._to_user_model(api_call('GET', '/authenticate/', data, request.headers))

	def get_user(self, user_id):
		data = json.dumps({
			'id': user_id
		})
		return self._to_user_model(api_call('GET', '/get_user/', data, {}))
	
	def create_user(self, request, **credentials):
		return self._to_user_model(api_call('POST', '/create_user/', json.dumps(credentials), {}))

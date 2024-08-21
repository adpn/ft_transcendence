# from .models import User
from django.db import models
from django.contrib.auth import base_user

import json
from os import environ
from http import client

AUTH_URL = environ.get('AUTH_URL')

class User(base_user.AbstractBaseUser):
    username42 = models.CharField(default=None, null=True)
    username = models.CharField(max_length=25, unique=True)

    # USERNAME_FIELD = 'id'
    # REQUIRED_FIELDS = ['username']
    # class Meta:
    #     constraints = [
    #         models.UniqueConstraint(
    #             fields=['username', 'is_42'],
    #             name='unique_username_with_is_42'
    #         )
    #     ]
    # profile_picture = models.FileField(upload_to=None, height_field=512, width_field=512, max_length=512)

def _to_user_model(status, data):
		if status != 200 and status != 201:
			return None
		return User(
			id=data['id'], 
			username=data['username'], 
			password=data['password'], 
			username42=data['username42'])

def api_call(method, url, body=None, headers={}):
		conn = client.HTTPConnection(AUTH_URL)
		try:
			conn.request(method, url, body, headers)
			response = conn.getresponse()
			return response.status, json.loads(response.read().decode())
		finally:
			conn.close()
	
def create_user(request):
	return _to_user_model(*api_call('POST', '/create_user/', request, request.headers))

def is_authenticated(request):
	user = _to_user_model(api_call('GET', '/is_authenticated/', request, request.headers))
	if not user:
		return False
	return True

class AuthenticationClient:
	def __init__(self) -> None:
		self._auth_url = environ.get('AUTH_URL')
	
	def _to_user_model(self, status, data):
		if status != 200 and status != 201:
			return None
		return User(
			id=data['id'], 
			username=data['username'], 
			password=data['password'], 
			username42=data['username42'])

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

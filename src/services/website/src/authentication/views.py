from django.shortcuts import render
from django.contrib.auth import login, logout, models
from django.http import JsonResponse, HttpResponse
from django.db.utils import IntegrityError
from django.db import models

import json
from uuid import uuid4
from http import client
import os

class ProtectedService(object):
	def __call__(self, request):
		return JsonResponse({'message': 'Hello!'}, status=200)

# wrapper that checks for othentication.
class NeedsAuthentication(object):
	def __init__(self, service_client) -> None:
		self._service_client = service_client
	
	def __call__(self, request):
		if request.user.is_authenticated:
			return self._service_client(request)
		return JsonResponse({}, status=401)

#relays request to a backend service.
class ServiceClient(object):
	def __init__(self, server_address) -> None:
		self._connection = client.HTTPConnection(server_address)
	
	def forward(self, path=None):
		def execute(request):
			conn = self._connection
			conn.request(
				request.method, 
				path if path else request.get_full_path(), 
				request.body, 
				request.headers)
			response = conn.getresponse()
			resp = HttpResponse(
				content=response.read(), 
				status=response.status, 
				content_type=response.getheader('Content-Type'))
			#copy headers
			for header, value in response.getheaders():
				resp[header] = value
			return resp
		return execute

	def __call__(self, request):
		#todo: send session ?
		conn = self._connection
		conn.request(
			request.method, 
			request.get_full_path(), 
			request.body, 
			request.headers)
		response = conn.getresponse()
		resp = HttpResponse(
			content=response.read(), 
			status=response.status, 
			content_type=response.getheader('Content-Type'))
		#copy headers
		for header, value in response.getheaders():
			resp[header] = value
		return resp

def login_view(user_management):
	def execute(request):
		if request.user.is_authenticated:
			return JsonResponse({'status': 1, 'message': 'already logged in'}, status=200)
		# additional authentication from backend
		# response = user_management.forward('/authenticate/')(request)
		# if response.status_code != 200:
		# 	return JsonResponse({'status': 0, 'message': 'login failed'}, status=401)
		try:
			data = json.loads(request.body)
		except json.decoder.JSONDecodeError:
			return HttpResponse(status=400)
		username = data["username"]
		password = data["password"]
		user = models.User.objects.filter(username=username).first()
		if user is not None and user.check_password(password):
			login(request, user)
			#todo: need a login response json -> should contain images
			return JsonResponse({'status': 1, 'message': 'successfully logged-in'}, status=200)
		return JsonResponse({'status': 1, 'message': 'login failed'}, status=401)
	return execute

def logout_view(request):
	logout(request)
	return JsonResponse({'status' : 1}, status=200)

def signup_view(user_management):
	def execute(request):
		# also create user in user-management.
		# response = user_management.forward('/signup/')(request)
		# if response.status_code != 200:
		# 	return JsonResponse({'status': 0, 'message' : 'username already taken'}, status=400)
		try:
			data = json.loads(request.body)
		except json.decoder.JSONDecodeError:
			return HttpResponse(status=400)
		try:
			user = models.User.objects.create_user(data["username"], password=data["password"])
		except IntegrityError:
			return JsonResponse({'status': 0, 'message' : 'username already taken'}, status=400)
		#todo: check if the fields are present
		#todo: perform hashing and salting before storing the password.
		#user.password = data["password"]
		user.is_active = True
		user.save()
		return JsonResponse({'status': 1, 'message' : 'successfully signed up'}, status=201)
	return execute

def auth42_view(request):
	code = request.get_full_path()[19:]
	client_id = os.environ.get('CLIENT_ID')
	client_secret = os.environ.get('CLIENT_SECRET')
	redirect_uri = os.environ.get("REDIRECT_URI")

	auth_url = "api.intra.42.fr"
	endpoint = "/oauth/token"

	fields = {
		'grant_type': 'authorization_code',
		'client_id': client_id,
		'client_secret': client_secret,
		'code': code,
		'redirect_uri': redirect_uri
	}

	# Generate a boundary string
	boundary = uuid4().hex

	# Create multipart/form-data body
	body = ''
	for key, value in fields.items():
		body += f'--{boundary}\r\n'
		body += f'Content-Disposition: form-data; name="{key}"\r\n\r\n'
		body += f'{value}\r\n'
	body += f'--{boundary}--\r\n'

	# Convert the body to bytes
	body = body.encode('utf-8')

	headers = {
		'Content-Type': f'multipart/form-data; boundary={boundary}',
		'Content-Length': str(len(body))
	}

	# Create a connection and send the POST request
	connection = client.HTTPSConnection(auth_url)
	connection.request("POST", endpoint, body, headers)

	# Get the response
	response = connection.getresponse()
	data = response.read().decode()

	# Close the connection
	connection.close()

	# Parse the response and return the JSON response
	# if response.status == 200:
	return JsonResponse(json.loads(data))
	# else:
	# 	return JsonResponse({'error': 'Failed to authenticate'}, status=response.status)

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout, get_user_model
from django.http import JsonResponse, HttpResponse
from django.db.utils import IntegrityError, DataError
# from django.db import models

import json
from uuid import uuid4
from http import client
import os
import random
import string
from common import auth_client

User = get_user_model()

class ProtectedService(object):
	def __call__(self, request):
		return JsonResponse({'message': 'Hello!'}, status=200)

def login_view(user_management):
	def execute(request):
		if request.method == 'GET' and request.user.is_authenticated:
			return JsonResponse({'status': 1, 'message': 'logged-in', 'user': {'username': 'bert', 'profile_picture': 'https://cdn.intra.42.fr/users/7877e411d4514ebf416307e7b17ae1a1/bvercaem.jpg'}}, status=200)
		elif request.method == 'GET':
			return JsonResponse({'status': 0, 'message': 'User not connected'}, status=200)

		if request.user.is_authenticated:
			return JsonResponse({'status': 2, 'message': 'already logged in'}, status=200)
		# additional authentication from backend
		# response = user_management.forward('/authenticate/')(request)
		# if response.status_code != 200:
		# 	return JsonResponse({'status': 0, 'message': 'login failed'}, status=401)
		try:
			data = json.loads(request.body)
		except json.decoder.JSONDecodeError:
			return JsonResponse({'status': 0, 'message': 'Couldn\'t read input'}, status=500)
		username = data["username"]
		password = data["password"]
		user = User.objects.filter(username=username).first()
		if user is not None and user.username42 is not None:
			return JsonResponse({'status': 0, 'message': 'You should login through 42auth'}, status=401)
		if user is not None and user.check_password(password):
			login(request, user)
			#todo: need a login response json -> should contain images
			return JsonResponse({'status': 1, 'message': 'successfully logged-in', 'user': {'username': 'bert', 'profile_picture': 'https://cdn.intra.42.fr/users/7877e411d4514ebf416307e7b17ae1a1/bvercaem.jpg' }}, status=200)
		return JsonResponse({'status': 0, 'message': 'Login failed'}, status=401)
	return execute

def logout_view(request):
	if not request.user.is_authenticated:
		return JsonResponse({'status': 0, 'message': 'not logged in'}, status=401)
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
			return JsonResponse({'status': 0, 'message': 'Couldn\'t read input'}, status=500)
		if (data["password"] != data["confirm_password"]):
			return JsonResponse({'status': 0, 'message' : 'Passwords do not match'}, status=400)
		try:
			user = User.objects.create_user(data["username"], password=data["password"])
		except IntegrityError:
			return JsonResponse({'status': 0, 'message': "Username already taken"}, status=400)
		except DataError:
			return JsonResponse({'status': 0, 'message': "Username too long"}, status=400)
		except Exception:
			return JsonResponse({'status': 0, 'message': 'An unexpected error occurred'}, status=500)
		#todo: check if the fields are present
		#todo: perform hashing and salting before storing the password.
		#user.password = data["password"]
		user.is_active = True
		user.save()
		login(request, user)

		# send a post request to user-management to create a user
		# response = user_management.post("/create-user/", data={"id": user.id}, content_type="application/json")
		# if response.status_code != 201:
		# 	return JsonResponse({'status': 0, 'message' : 'USER MANAGEMENT TEST'}, status=400)
	
		return JsonResponse({'status': 1, 'message' : 'successfully signed up',  'user': {'username': 'bert', 'profile_picture': 'https://cdn.intra.42.fr/users/7877e411d4514ebf416307e7b17ae1a1/bvercaem.jpg' }}, status=201)
	return execute

def authenticate_42API(request):
	path = request.get_full_path()
	if "error" in path:
		return None, 'Failed to authenticate'
	
	code = path[19:]
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

	boundary = uuid4().hex
	body = ''
	for key, value in fields.items():
		body += f'--{boundary}\r\n'
		body += f'Content-Disposition: form-data; name="{key}"\r\n\r\n'
		body += f'{value}\r\n'
	body += f'--{boundary}--\r\n'

	body = body.encode('utf-8')

	headers = {
		'Content-Type': f'multipart/form-data; boundary={boundary}',
		'Content-Length': str(len(body))
	}

	connection = client.HTTPSConnection(auth_url)
	connection.request("POST", endpoint, body, headers)

	response = connection.getresponse()
	data = response.read().decode()
	connection.close()

	if response.status != 200:
		return None, 'Failed to authenticate'
	return json.loads(data), None

def generate_username():
	words = ["alpha", "bravo", "charlie", "delta", "echo", "foxtrot", "golf"]
	username = random.choice(words) + "".join(random.choices(string.digits, k=4))
	return username

def auth42_view(request):
	if request.user.is_authenticated:
		return redirect('/')
	
	auth_response, error_message = authenticate_42API(request)
	
	if error_message:
		messages.error(request, error_message)
		return redirect('/')
	
	headers = {
		"Authorization": "Bearer " + auth_response["access_token"]
	}

	api_url = "api.intra.42.fr"
	endpoint = "/v2/me"

	connection = client.HTTPSConnection(api_url)
	connection.request("GET", endpoint, "", headers)
	api_response = connection.getresponse()
	data = api_response.read().decode()
	connection.close()

	if api_response.status != 200:
		messages.error(request, 'Failed to retrieve user data')
		return redirect('/')

	MeData = json.loads(data)
	user = User.objects.filter(username42=MeData["login"]).first()
	if user is None:
		# generate a username, that the user will change later
		username = generate_username()
		while User.objects.filter(username=username).exists():
			username = generate_username()
		user = User.objects.create_user(username=username, username42=MeData["login"])
		user.is_active = True
		user.save()
		# todo: create entry in user management db

	login(request, user)
	return redirect('/')


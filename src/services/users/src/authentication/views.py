from django.shortcuts import redirect
from common import jwt, service_client

# Create your views here.

from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout
from django.http import JsonResponse, HttpResponse
from django.db.utils import IntegrityError, DataError
# from django.db import models

import os
import json
from uuid import uuid4
from http import client
import random
import string
import time
from datetime import datetime, timedelta
from .models import UserToken

User = get_user_model()

SECRET = os.environ.get('JWT_SECRET_KEY').encode('utf-8')

def create_jwt(username):
	header = {
		"alg": "HS256",
		"typ": "JWT"
	}

	now = datetime.now()
	exp = now + timedelta(hours=2)

	payload = {
		"sub": uuid4().int,
		"name": username,
		"iat": int(now.timestamp()),
		"exp": int(exp.timestamp()),
		"iss": "ft_transcendence.com"
	}

	payload_json = json.dumps(payload, separators=(',', ':')).encode('utf-8')
	payload_b64 = jwt.base64url_encode(payload_json)
	header_json = json.dumps(header, separators=(',', ':')).encode('utf-8')
	header_b64 = jwt.base64url_encode(header_json)
	signature = jwt.hmac.new(SECRET, f"{header_b64}.{payload_b64}".encode('utf-8'), jwt.hashlib.sha256).digest()
	signature_b64 = jwt.base64url_encode(signature)

	return f"{header_b64}.{payload_b64}.{signature_b64}"

def get_jwt(request):
	auth = request.headers.get('Authorization')
	if not auth:
		return None
	if not 'Bearer ' in auth:
		return None
	values = auth.split(' ')
	if len(values) != 2:
		return None
	return values[1]

def validate_jwt(token):
	if not token:
		raise ValueError("No token")
	payload = jwt.verify_jwt(token, SECRET)
	# todo: check for expiration date.
	exp = payload.get("exp")
	if exp is None:
		raise ValueError("Token has no expiration time")
	# Compare with the current time
	current_time = int(time.time())
	if current_time > exp:
		raise ValueError("Token has expired")

def check_jwt(request) -> User:
	# check if we have the token in the database -> means that user has not logged out
	token = get_jwt(request)
	user_token = UserToken.objects.filter(token=token).first()
	if not user_token:
		return None
	# check if the token is still valid.
	try:
		validate_jwt(token)
		return user_token.user
	except ValueError:
		# remove the token from the database as it is invalid
		user_token.delete()
		return None

def custom_login(request, username, password):
	user = User.objects.filter(username=username).first()
	if user is None:
		return JsonResponse({
			'status': 0, 
			'message': 
			'User does not exist'}, status=401)
	if user.username42 is not None:
		return JsonResponse({'status': 0, 'message': 'You should login through 42auth'}, status=401)
	if user.check_password(password):
		login(request, user)
		return profile_mini(request)
	return JsonResponse({
		'status': 0, 
		'message': 'Login failed'}, status=401)

def login_view(request) -> JsonResponse:
	if request.user.is_authenticated:
		return JsonResponse({'status': 2, 'message': 'already logged in'}, status=200)
	try:
		data = json.loads(request.body)
	except json.decoder.JSONDecodeError:
		return JsonResponse({'status': 0, 'message': 'Couldn\'t read input'}, status=500)
	username = data["username"]
	password = data["password"]
	# todo: need to implement this...
	return custom_login(request, username, password)

def logout_view(request) -> JsonResponse:
	if not request.user.is_authenticated:
		return JsonResponse({'status': 0, 'message': 'not logged in'}, status=401)
	# delete token from database.
	user_token = UserToken.objects.filter(user=request.user).first()
	print("TOKEN DELETE", user_token.token, flush=True)
	user_token.delete()
	logout(request)
	return JsonResponse({'status' : 1}, status=200)

def profile_mini(request) -> JsonResponse:
	connection = client.HTTPConnection("users:8000")
	
	try:
		connection.request("GET", f"/get_picture/{request.user.id}/")
		response = connection.getresponse()
		
		# Debug: print the status and response data
		print("Response status:", response.status)
		raw_data = response.read().decode()
		print("Raw response data:", raw_data)
		
		if response.status != 200:
			return JsonResponse({'status': 0, 'message': 'Failed to retrieve profile picture'}, status=response.status)
		
		if not raw_data:
			return JsonResponse({'status': 0, 'message': 'Empty response from users service'}, status=500)
		
		profile_picture = json.loads(raw_data).get('profile_picture')
		
		if not profile_picture:
			return JsonResponse({'status': 0, 'message': 'Profile picture not found'}, status=404)
		
	except json.JSONDecodeError:
		return JsonResponse({'status': 0, 'message': 'Invalid JSON response from users service'}, status=500)
	except Exception as e:
		return JsonResponse({'status': 0, 'message': f'An error occurred: {str(e)}'}, status=500)
	finally:
		connection.close()

	token = create_jwt(request.user.username)
	# save token in db.
	UserToken(user=request.user, token=token).save()

	return JsonResponse({
		'status': 1,
		'message': 'logged-in',
		'token': token,
		'user': {
			'username': request.user.username,
			'profile_picture': profile_picture
		}
	}, status=200)

def sign_up_view(request) -> JsonResponse:
	try:
		data: dict = json.loads(request.body)
	except json.decoder.JSONDecodeError:
		return JsonResponse({'status': 0, 'message': 'Couldn\'t read input'}, status=500)
	if (data["password"] != data["confirm_password"]):
		return JsonResponse({'status': 0, 'message' : 'Passwords do not match'}, status=400)

	#temporary, will go up to 8 or 10
	if (len(data["password"]) < 1):
		return JsonResponse({'status': 0, 'message' : 'Password too short'}, status=400)

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
	user.is_active = True
	user.save()

	# send create_user to user_data app
	connection = client.HTTPConnection("users:8000")
	connection.request("POST", "/create_user/", json.dumps({"user_id": user.id, "profile_picture": ""}), {'Content-Type': 'application/json'})
	response = connection.getresponse()
	connection.close()
	if response.status != 201:
		return JsonResponse({'status': 0, 'message': 'User creation failed'}, status=500)
	login(request, user)
	
	return profile_mini(request)

def is_authenticated_view(request) -> JsonResponse:
	# check if it has a valid token first
	user = check_jwt(request)
	if user:
		login(request, user)
		return profile_mini(request)
	if request.user.is_authenticated:
		return profile_mini(request)
	else :
		return JsonResponse({'status': 0, 'message': 'User not connected'}, status=200)

def authenticate_42API(request) -> tuple:
	path = request.get_full_path()
	if "error" in path:
		return None, 'Failed to authenticate'
	
	code = path[14:]
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

def generate_username() -> str:
	words = ["alpha", "bravo", "charlie", "delta", "echo", "foxtrot", "golf", "hotel", "lima"]
	username = random.choice(words) + "".join(random.choices(string.digits, k=4))
	return username

# games_client = service_client.ServiceClient('website:8000')

# def create_game(request):
# 	if request.user.is_authenticated:
# 		return games_client.forward('/games/create_game/')(request)
# 	return JsonResponse({}, status=401)

def check_token(request):
	# todo: if the user has logged-out this should 
	if check_jwt(request):
		return HttpResponse(status=200)
	return HttpResponse(status=401)

def get_user(request) -> JsonResponse:
	user = check_jwt(request)
	if user:
		return JsonResponse({
			'username': user.username,
			'user_id': user.id
		}, status=200)
	return JsonResponse({}, status=401)

def auth42_view(request):
	if request.user.is_authenticated:
		return redirect('/')
	
	auth_response, error_message = authenticate_42API(request)
	if error_message:
		messages.error(request, error_message)
		return redirect('/', permanent=True)
	
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
		return redirect('/', permanent=True)

	MeData = json.loads(data)
	user = User.objects.filter(username42=MeData["login"]).first()
	if user is None:
		# generate a username, that the user will change later
		username = generate_username()
		while User.objects.filter(username=username).exists():
			username = generate_username()
		new_user = User.objects.create_user(username=username, username42=MeData["login"])
		new_user.is_active = True
		new_user.save()

		profile_picture = MeData["image"]["link"]
		connection = client.HTTPConnection("users:8000")
		connection.request("POST", "/create_user/", json.dumps({"user_id": new_user.id, "profile_picture": profile_picture}))
		connection.close()
		login(request, new_user)
	else:
		login(request, user)
	return redirect('/', permanent=True)

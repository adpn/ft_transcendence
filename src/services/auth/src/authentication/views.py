from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from django.views import View
from django.db.utils import IntegrityError

from http import client
from urllib import request, parse

import os
import json

# Create your views here.
#todo: make a json required decorator.

def login_view(request):
	#todo: check if the fields are present
	try:
		data = json.loads(request.body)
	except json.decoder.JSONDecodeError:
		return HttpResponse(status=400)
	username = data["username"]
	password = data["password"]
	user = authenticate(request, username=username, password=password)
	if user is not None:
		login(request, user)
		#todo: need a login response json -> should contain images
		return JsonResponse({'status': 1}, status=200)
	else:
		return JsonResponse({}, status=401)

def logout_view(request):
	logout(request)
	return JsonResponse({'status' : 1}, status=200)

def signup_view(request):
	try:
		data = json.loads(request.body)
	except json.decoder.JSONDecodeError:
		return HttpResponse(status=400)
	try:
		user = User.objects.create_user(data["username"])
	except IntegrityError:
		return JsonResponse({'status': 0, 'message' : 'username already taken'}, status=400)
	#todo: check if the fields are present
	#todo: perform hashing and salting before storing the password.
	user.password = data["password"]
	return JsonResponse({'status': 1, 'message' : ''}, status=201)

# def auth42_view(request):
# 	code = request.get_full_path()[12:]
# 	client_id = os.environ.get('CLIENT_ID')
# 	client_secret = os.environ.get('CLIENT_SECRET')
# 	# auth_url = os.environ.get("AUTH_URL")

# 	# Add fields
# 	fields = {
# 		'grant_type': 'authorization_code',
# 		'client_id': client_id,
# 		'client_secret': client_secret,
# 		'code': code
# 	}

# 	# Convert multipart_data to string
# 	body = fields
# 	# Send the request
# 	connection = client.HTTPConnection("https://api.intra.42.fr/oauth/token")
# 	connection.request(
# 		"POST",
# 		"/oauth/token",
# 		body
# 	)

# 	# Get the response
# 	response = connection.getresponse()
# 	response_data = response.read()

# 	print(response_data.decode())
# 	connection.close()

# 	return JsonResponse({"auth42":response_data.decode()}, status=200)

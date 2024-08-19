from django.shortcuts import render

# Create your views here.

from django.contrib.auth import get_user_model, login, logout
from django.http import JsonResponse, HttpResponse
from django.db.utils import IntegrityError, DataError
# from django.db import models

import json
from uuid import uuid4
from http import client
import os

User = get_user_model()

def user_to_json(user):
	return {
		'id': user.pk,
		'username': user.username,
		'password': user.password,
		'username42': user.username42
	}

def get_user(request):
	try:
		data = json.loads(request.body)
	except json.decoder.JSONDecodeError:
		return JsonResponse({'status': 0, 'message': 'Couldn\'t read input'}, status=500)
	try:
		user_to_json(User.objects.get(id=data['id']).first())
	except User.DoesNotExist:
		return JsonResponse({'status': 0, 'message': 'User does not exist'}, status=404)

# def authenticate(request):
# 	try:
# 		data = json.loads(request.body)
# 	except json.decoder.JSONDecodeError:
# 		return JsonResponse({'status': 0, 'message': 'Couldn\'t read input'}, status=500)
# 	username = data["username"]
# 	password = data["password"]
# 	user = User.objects.filter(username=username).first()
# 	if user is not None and user.check_password(password):
# 		return user_to_json(user)
# 	return JsonResponse({'status': 0, 'message': 'Failed to authenticate'}, status=404)

def login_view(request):
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
	# user = User.objects.filter(username=username).first()
	# todo: need to implement this...
	user = User.objects.filter(username=username).first()
	if user is not None and user.username42 is not None:
		return JsonResponse({'status': 0, 'message': 'You should login through 42auth'}, status=401)
	if user is not None and user.check_password(password):
		login(request, user)
		#todo: need a login response json -> should contain images
		return JsonResponse({'status': 1, 'message': 'successfully logged-in', 'user': {'username': 'bert', 'profile_picture': 'https://cdn.intra.42.fr/users/7877e411d4514ebf416307e7b17ae1a1/bvercaem.jpg' }}, status=200)
	return JsonResponse({'status': 0, 'message': 'Login failed'}, status=401)

def logout_view(request):
	if not request.user.is_authenticated:
		return JsonResponse({'status': 0, 'message': 'not logged in'}, status=401)
	logout(request)
	return JsonResponse({'status' : 1}, status=200)

def create_user(request):
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
	# try:
	# 	user = User.objects.create_user(data["username"], password=data["password"])
	# 	request.user = user
	# except IntegrityError:
	# 	return JsonResponse({
	# 		'status': 0, 
	# 		'message' : 'Username already taken'}, 
	# 		status=400)
	# user.is_active = True
	# user.save()
	# # login(request, user)
	# return JsonResponse(
	# 	user_to_json(user), 
	# 	status=201)

def is_authenticated(request):
	if request.user.is_authenticated:
		return

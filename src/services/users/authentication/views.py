from django.shortcuts import render

# Create your views here.

from django.contrib.auth import login, logout, get_user_model
from django.http import JsonResponse, HttpResponse
from django.db.utils import IntegrityError
# from django.db import models

import json
from uuid import uuid4
from http import client
import os

User = get_user_model()

def user_to_json(user):
	return {
		'username': user.username,
		'password': user.password
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

def authenticate(request):
	try:
		data = json.loads(request.body)
	except json.decoder.JSONDecodeError:
		return JsonResponse({'status': 0, 'message': 'Couldn\'t read input'}, status=500)
	username = data["username"]
	password = data["password"]
	user = User.objects.filter(username=username).first()
	if user is not None and user.check_password(password):
		return user_to_json(user)
	return JsonResponse({'status': 0, 'message': 'Failed to authenticate'}, status=404)

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
		user = User.objects.create_user(data["username"], password=data["password"])
	except IntegrityError:
		return JsonResponse({
			'status': 0, 
			'message' : 'Username already taken'}, 
			status=400)
	user.is_active = True
	user.save()
	# login(request, user)
	return JsonResponse(
		user_to_json(user), 
		status=201)

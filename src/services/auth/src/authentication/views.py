from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from django.views import View
from django.db.utils import IntegrityError

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

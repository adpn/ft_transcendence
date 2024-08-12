from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from django.views import View
from django.db.utils import IntegrityError

import json

# Create your views here.
#todo: make a json required decorator.

def signup_view(request):
	try:
		data = json.loads(request.body)
	except json.decoder.JSONDecodeError:
		return HttpResponse(status=400)
	try:
		user = User.objects.create_user(data["username"], data["password"])
	except IntegrityError:
		return JsonResponse({'status': 0, 'message' : 'username already taken'}, status=400)
	#todo: check if the fields are present
	#todo: perform hashing and salting before storing the password.
	#user.password = data["password"]
	user.is_active = True
	user.save()
	return JsonResponse({'status': 1, 'message' : 'successfully signed up'}, status=201)

def authenticate_view(request):
	try:
		data = json.loads(request.body)
	except json.decoder.JSONDecodeError:
		return HttpResponse(status=400)
	username = data["username"]
	password = data["password"]
	user = User.objects.filter(username=username).first()
	if user is None:
		return HttpResponse(status=404)
	if not user.check_password(password):
		return HttpResponse(status=404)
		#todo: need a login response json -> should contain images
	return HttpResponse(status=200)

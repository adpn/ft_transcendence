from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.contrib.auth.models import User

import json
from .serializers import ItemSerializer
from .models import Item

# Create your views here.
def index(request):
	return render(request, 'index.html')

class ItemListView(View):

	def get(self, request):
		items = Item.objects.all()
		data = ItemSerializer.serialize_many(items)
		return JsonResponse(data, safe=False)

	def post(self, request):
		try:
			data = json.loads(request.body)
			item = Item.objects.create(name=data['name'], description=data['description'])
			return JsonResponse(ItemSerializer.serialize(item), status=201)
		except (KeyError, json.JSONDecodeError):
			return HttpResponse(status=400)

def login_view(request):
	#todo: check if the fields are present
	username = request.POST["username"]
	password = request.POST["password"]
	user = authenticate(request, username=username, password=password)
	if user is not None:
		login(request, user)
		#todo: need a login response json -> should contain images
		return JsonResponse({}, status=200)
	else:
		return JsonResponse({}, status=404)

def logout_view(request):
	logout(request)
	return JsonResponse({}, status=200)

def signup_view(request):
	user = User.objects.create_user()
	#todo: check if the fields are present
	user.username = request.POST["username"]
	#todo: perform hashing and salting before storing the password.
	user.password = request.POST["password"]
	user.save()
	#todo: check if username is already taken...
	return JsonResponse({}, status=200)

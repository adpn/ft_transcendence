from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views import View
from django.contrib.auth.models import User

import json
from .serializers import ItemSerializer
from .models import Item

from .clients import AuthenticationClient

auth_client = AuthenticationClient("authentication:8000")

# Create your views here.
def index(request):
	return render(request, 'index.html')

class ViewFactory(object):
	def __init__(self, view_class, **kwargs) -> None:
		self._view_class = view_class
		self._kwargs = kwargs

	def __call__(self, *args, **kwargs):
		view_instance = self._view_class(**self._kwargs)
		return view_instance(*args, **kwargs)

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

class SignUpView(View):
	def __init__(self, **kwargs) -> None:
		super().__init__(**kwargs)
		self._auth_client = kwargs['auth_client']
	
	def post(self, request):
		return self._auth_client.signup(request)

class LoginView(View):
	def __init__(self, **kwargs) -> None:
		super().__init__(**kwargs)
		self._auth_client = kwargs['auth_client']
	
	def post(self, request):
		return self._auth_client.login(request)

class LogoutView(View):
	def __init__(self, **kwargs) -> None:
		super().__init__(**kwargs)
		self._auth_client = kwargs['auth_client']
	
	def post(self, request):
		return self._auth_client.logout(request)

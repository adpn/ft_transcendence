from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views import View

import json

from http import client

from .serializers import ItemSerializer
from .models import Item

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
			# #copy headers
			# for header, value in response.getheaders():
			# 	resp[header] = value
			# return resp
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
		# #copy headers
		# for header, value in response.getheaders():
		# 	resp[header] = value
		return resp

from os import environ

AUTH_URL = environ.get('AUTH_URL')
server_url = environ.get('SESSION_SERVER')

def api_call(method, url, body=None, headers={}):
		conn = client.HTTPConnection(AUTH_URL)
		try:
			conn.request(method, url, body, headers)
			response = conn.getresponse()
			return response.status, json.loads(response.read().decode())
		finally:
			conn.close()

def _request(self, method, url, body=None, headers={}):
	conn = client.HTTPConnection(server_url)
	try:
		conn.request(method, url, body, headers)
		response = conn.getresponse()
		return response.status, response.read().decode()
	finally:
		conn.close()

def is_authenticated(request):
	#_request(request.method, '/auth/is_authenticated/', request.body, request.headers)
	status, data = api_call(request.method, '/is_authenticated/', request.body, request.headers)
	return JsonResponse(data, status=status)


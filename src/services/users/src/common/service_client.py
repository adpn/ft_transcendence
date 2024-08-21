from django.shortcuts import render
from django.http import HttpResponse
from django.views import View
from django.contrib.auth.models import User

from http import client

class ServiceClient(object):
	def __init__(self, server_address) -> None:
		self._server_address = server_address
		self._connection = client.HTTPConnection(server_address)
	
	def forward(self, path=None):
		connection = client.HTTPConnection(self._server_address)
		def execute(request):
			conn = connection
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
			return resp
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
import json
# import requests

from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse

# todo: make requests to backend client
class AuthenticationClient(object):
	def __init__(self, server_address) -> None:
		self._server_address = server_address

	def signup(self, request):
		# requests.post(self._server_address)
		pass
	
	def login(self, request):
		# requests.get()
		#todo: check if the fields are present
		data = json.loads(request.body)
		username = data["username"]
		password = data["password"]
		user = authenticate(request, username=username, password=password)
		if user is not None:
			login(request, user)
			#todo: need a login response json -> should contain images
			return JsonResponse({}, status=200)
		else:
			return JsonResponse({}, status=404)
	
	def logout(self, request):
		logout(request)
		return JsonResponse({}, status=200)

from django.http import JsonResponse, HttpResponse

from http import client

# wrapper that checks for othentication.
class NeedsAuthentication(object):
	def __init__(self, service_client) -> None:
		self._service_client = service_client
	
	def __call__(self, request):
		if request.user.is_authenticated:
			return self._service_client(request)
		return JsonResponse({}, status=401)

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
			#copy headers
			for header, value in response.getheaders():
				resp[header] = value
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
		#copy headers
		# for header, value in response.getheaders():
		# 	resp[header] = value
		
		return resp

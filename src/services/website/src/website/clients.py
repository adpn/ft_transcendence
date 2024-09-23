from http import client

from django.http import HttpResponse

class AuthenticationClient(object):
	def __init__(self, server_address) -> None:
		self._connection = client.HTTPConnection(server_address)
	
	def __call__(self, request):
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
		for header, value in response.getheaders():
			resp[header] = value
		return resp

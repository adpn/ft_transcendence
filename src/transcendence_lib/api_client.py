from json import loads
from http import client

class APIClient(object):
	def __init__(self, url) -> None:
		self._url = url

	def request(self, method, url, body=None, headers={}):
		conn = client.HTTPConnection(self._url)
		try:
			conn.request(method, url, body, headers)
			response = conn.getresponse()
			return response.status, loads(response.read().decode())
		finally:
			conn.close()

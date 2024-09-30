from django.contrib.sessions.backends.base import SessionBase, CreateError

from http import client
from os import environ
import json

class SessionStore(SessionBase):
	def __init__(self, session_key=None) -> None:
		super().__init__(session_key)
		self._server_url = environ.get('SESSION_SERVER')

	def _request(self, method, url, body=None, headers={}):
		conn = client.HTTPConnection(self._server_url)
		try:
			conn.request(method, url, body, headers)
			response = conn.getresponse()
			return response.status, response.read().decode()
		finally:
			conn.close()

	def load(self):
		if self._session_key:
			url = f"/session/{self._session_key}/"
			status, response_body = self._request("GET", url)
			if status == 200:
				session_data = json.loads(response_body).get('session_data', {})
				return session_data
		self.create()
		return {}

	def create(self):
		status, response_body = self._request("POST", '/session/')
		if status == 200:
			self._session_key = json.loads(response_body).get('session_id')
			self._session_cache = {}
		else:
			raise CreateError()

	def save(self, must_create=False):
		if must_create or self._session_key is None:
			self.create()
		data = json.dumps(self._session_cache)
		headers = {'Content-Type': 'application/json'}
		url = f"/session/{self._session_key}/"
		status, _ = self._request("PUT", url, body=data, headers=headers)
		if status != 200:
			raise CreateError()

	def delete(self, session_key=None):
		session_key = session_key or self._session_key
		if session_key:
			url = f"/session/{session_key}/"
			self._request("DELETE", url)

	def exists(self, session_key: str) -> bool:
		return True

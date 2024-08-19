from django.contrib.sessions.backends.base import SessionBase, CreateError
from os import environ
import uuid

SESSION_STORE = {}

def add(session_id):
	SESSION_STORE[session_id] = {}

def get(session_id):
	return SESSION_STORE.get(session_id, {})

def update(session_id, data):
	if session_id in SESSION_STORE:
		SESSION_STORE[session_id].update(data)
	else:
		add(session_id)
		SESSION_STORE[session_id].update(data)

def remove(session_id):
	if session_id in SESSION_STORE:
		del SESSION_STORE[session_id]

def has_session(session_id):
	return session_id in SESSION_STORE


class SessionStore(SessionBase):
	def __init__(self, session_key=None) -> None:
		super().__init__(session_key)
		if session_key:
			self._session_key = session_key

	def load(self):
		if self._session_key and has_session(self._session_key):
			self._session_cache = get(self._session_key)
		else:
			self.create()
			self._session_cache = {}
		return self._session_cache

	def create(self):
		session_id = str(uuid.uuid4())
		add(session_id)
		self._session_key = session_id
		self._session_cache = {}

	def save(self, must_create=False):
		if must_create or self._session_key is None:
			self.create()
		update(self._session_key, self._session_cache)

	def delete(self, session_key=None):
		session_key = session_key or self._session_key
		if session_key:
			remove(session_key)
			self._session_key = None

	def exists(self, session_key: str) -> bool:
		return has_session(session_key)
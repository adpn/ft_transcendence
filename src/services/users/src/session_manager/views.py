from django.http import JsonResponse
from django.views import View
import uuid
import json
from common import session_store

class SessionView(View):
	def post(self, request):
		# Create a new session
		session_id = str(uuid.uuid4())
		# SESSION_STORE[session_id] =
		session_store.add(session_id)
		return JsonResponse({'session_id': session_id})

	def get(self, request, session_id):
		# Retrieve session data
		session_data = session_store.get(session_id)
		if session_data is None:
			return JsonResponse({'error': 'Session not found'}, status=404)
		return JsonResponse({'session_data': session_data})

	def put(self, request, session_id):
		# Update session data
		if not session_store.has_session(session_id):
			return JsonResponse({'error': 'Session not found'}, status=404)
		session_store.update(session_id, json.loads(request.body))
		# SESSION_STORE[session_id] = json.loads(request.body)
		return JsonResponse({'status': 'success'})

	def delete(self, request, session_id):
		# Delete session data
		if session_store.has_session(session_id):
			# del SESSION_STORE[session_id]
			session_store.remove(session_store)
			return JsonResponse({'status': 'success'})
		return JsonResponse({'error': 'Session not found'}, status=404)

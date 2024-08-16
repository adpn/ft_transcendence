from django.shortcuts import render

# Create your views here.

from django.shortcuts import render

# Create your views here.

from django.http import JsonResponse
from django.views import View
from django.middleware.csrf import get_token
import uuid
import json

# In-memory store for simplicity, use a database like Redis or SQL in production
SESSION_STORE = {}

class SessionView(View):
    def post(self, request):
        # Create a new session
        session_id = str(uuid.uuid4())
        SESSION_STORE[session_id] = {}
        return JsonResponse({'session_id': session_id})

    def get(self, request, session_id):
        # Retrieve session data
        session_data = SESSION_STORE.get(session_id)
        if session_data is None:
            return JsonResponse({'error': 'Session not found'}, status=404)
        return JsonResponse({'session_data': session_data})

    def put(self, request, session_id):
        # Update session data
        if session_id not in SESSION_STORE:
            return JsonResponse({'error': 'Session not found'}, status=404)
        SESSION_STORE[session_id] = json.loads(request.body)
        return JsonResponse({'status': 'success'})

    def delete(self, request, session_id):
        # Delete session data
        if session_id in SESSION_STORE:
            del SESSION_STORE[session_id]
            return JsonResponse({'status': 'success'})
        return JsonResponse({'error': 'Session not found'}, status=404)

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from django.views import View
from django.db.utils import IntegrityError

import json

# Create your views here.
#todo: make a json required decorator.

def login_view(request):
	#todo: check if the fields are present
	try:
		data = json.loads(request.body)
	except json.decoder.JSONDecodeError:
		return HttpResponse(status=400)
	username = data["username"]
	password = data["password"]
	user = authenticate(request, username=username, password=password)
	user = User.objects.filter(username=username).first()
	if request.user.is_authenticated:
		return JsonResponse({'status': 1, 'message': 'already logged in'}, status=200)
	if user is not None:
		login(request, user)
		#todo: need a login response json -> should contain images
		return JsonResponse({'status': 1, 'message': 'successfully logged-in'}, status=200)
	else:
		return JsonResponse({'status': 0, 'message': 'login failed'}, status=401)

def logout_view(request):
	logout(request)
	return JsonResponse({'status' : 1}, status=200)

def signup_view(request):
	try:
		data = json.loads(request.body)
	except json.decoder.JSONDecodeError:
		return HttpResponse(status=400)
	try:
		user = User.objects.create_user(data["username"], data["password"])
	except IntegrityError:
		return JsonResponse({'status': 0, 'message' : 'username already taken'}, status=400)
	#todo: check if the fields are present
	#todo: perform hashing and salting before storing the password.
	#user.password = data["password"]
	user.is_active = True
	user.save()
	return JsonResponse({'status': 1, 'message' : 'successfully signed up'}, status=201)

def authenticate_view(request):
	try:
		data = json.loads(request.body)
	except json.decoder.JSONDecodeError:
		return HttpResponse(status=400)
	username = data["username"]
	password = data["password"]
	user = User.objects.filter(username=username).first()
	if user is None:
		return HttpResponse(status=404)
	if not user.check_password(password):
		return HttpResponse(status=404)
		#todo: need a login response json -> should contain images
	return HttpResponse(status=200)

def auth42_view(request):
	code = request.get_full_path()[12:]
	client_id = os.environ.get('CLIENT_ID')
	client_secret = os.environ.get('CLIENT_SECRET')
	redirect_uri = os.environ.get("REDIRECT_URI")

	auth_url = "api.intra.42.fr"
	endpoint = "/oauth/token"

	fields = {
		'grant_type': 'authorization_code',
		'client_id': client_id,
		'client_secret': client_secret,
		'code': code,
		'redirect_uri': redirect_uri
	}

	# Generate a boundary string
	boundary = uuid4().hex

	# Create multipart/form-data body
	body = ''
	for key, value in fields.items():
		body += f'--{boundary}\r\n'
		body += f'Content-Disposition: form-data; name="{key}"\r\n\r\n'
		body += f'{value}\r\n'
	body += f'--{boundary}--\r\n'

	# Convert the body to bytes
	body = body.encode('utf-8')

	headers = {
		'Content-Type': f'multipart/form-data; boundary={boundary}',
		'Content-Length': str(len(body))
	}

	# Create a connection and send the POST request
	connection = http.client.HTTPSConnection(auth_url)
	connection.request("POST", endpoint, body, headers)

	# Get the response
	response = connection.getresponse()
	data = response.read().decode()

	# Close the connection
	connection.close()

	# Parse the response and return the JSON response
	# if response.status == 200:
	return JsonResponse(json.loads(data))
	# else:
	# 	return JsonResponse({'error': 'Failed to authenticate'}, status=response.status)

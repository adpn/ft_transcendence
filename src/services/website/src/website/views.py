from django.shortcuts import render
from django.http import HttpRequest
import os

def index(request : HttpRequest):
	elements = {'ip_address': os.getenv("IP_ADDRESS")}
	if request.headers.get("status"):
		elements['status'] = request.headers.get("status")
		elements['message'] = request.headers.get("message")
	return render(request, 'index.html', elements)

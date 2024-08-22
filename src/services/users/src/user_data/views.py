from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from user_data.models import UserProfile
from django.http import HttpResponse, JsonResponse, FileResponse
import json
from django.core.files.base import ContentFile
from django.conf import settings
import os
from http import client

# Create user in the database user_data
@csrf_exempt
def create_user(request):
    body = json.loads(request.body)
    user_id = body['user_id']
    if len(body["profile_picture"]) > 0:
        image_url: str = body["profile_picture"]
        url_parsed: list = image_url.split("/")
        connection = client.HTTPSConnection(url_parsed[2])
        connection.request("GET", "/" + "/".join(url_parsed[3:]))
        response = connection.getresponse()
        image = ContentFile(response.read(), name=str(user_id) + ".jpg")
        connection.close()
        new_user = UserProfile(user_id=user_id, profile_picture=image)
    else:
        new_user = UserProfile(user_id=user_id)
    new_user.save() #using='user_data'
    return HttpResponse(status=201)

@csrf_exempt
def get_picture(request, user_id) -> JsonResponse:
    # .using("user_data")
    user = UserProfile.objects.get(user_id=user_id)
    profile_picture = user.profile_picture.url
    return JsonResponse({'profile_picture': profile_picture}, status=200)

def send_picture(request, filename: str):
    image_path = request.path
    full_image_path = os.path.join(settings.MEDIA_ROOT, image_path.lstrip('/'))
    if os.path.exists(full_image_path):
        return FileResponse(open(full_image_path, 'rb'), content_type='image/jpeg')
    else:
       return HttpResponse(status=404)

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from user_data.models import UserProfile
from django.http import HttpResponse, JsonResponse, FileResponse
import json
from django.core.files.base import ContentFile
from django.conf import settings
import os
from http import client
import sys

# Create user in the database user_data
@csrf_exempt
def create_user(request):
    body = json.loads(request.body)
    user_id = body['user_id']
    if len(body["profile_picture"]) > 0:
        print(body["profile_picture"], flush=True, file=sys.stderr)
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
def get_picture_url(request, user_id: int) -> JsonResponse:
    # .using("user_data")
    user = UserProfile.objects.get(user_id=user_id)
    profile_picture = user.profile_picture.url
    return JsonResponse({'profile_picture': profile_picture}, status=200)

def get_image(request, filename: str):
    image_path = request.path
    full_image_path = os.path.join(settings.MEDIA_ROOT, image_path.lstrip('/'))
    if os.path.exists(full_image_path):
        return FileResponse(open(full_image_path, 'rb'), content_type='image/jpeg')
    else:
       return HttpResponse(status=404)

def change_profile_picture(request) -> JsonResponse:
    if not request.user.is_authenticated:
        return JsonResponse({'status': 0, 'message': 'User not connected'}, status=401)
    if request.method != 'POST':
        return JsonResponse({'status': 0, 'message': 'Only POST method is allowed'}, status=405)
    image = request.FILES['profile_picture']
    user = UserProfile.objects.get(user_id=request.user.id)
    user.profile_picture.save(f"{user.user_id}.jpg", image)
    user.save()
    return JsonResponse({'status': 1, 'message': 'Profile picture updated', 'new_profile_picture_url': user.profile_picture.url}, status=200)

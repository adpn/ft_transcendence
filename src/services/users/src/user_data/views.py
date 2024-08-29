from django.views.decorators.csrf import csrf_exempt
from user_data.models import UserProfile, Game
from django.http import HttpResponse, JsonResponse, FileResponse, HttpRequest
import json
from django.core.files.base import ContentFile
from django.conf import settings
import os
from http import client
from django.contrib.auth import get_user_model

User = get_user_model()

# Create user in the database user_data
@csrf_exempt
def create_user(request : HttpRequest):
    body = json.loads(request.body)
    user_id = body['user_id']

    try:
        user = User.objects.get(id=user_id)  # Retrieve the User instance using the user_id
    except User.DoesNotExist:
        return HttpResponse(status=500)

    if len(body["profile_picture"]) > 0:
        image_url: str = body["profile_picture"]
        url_parsed: list = image_url.split("/")
        connection = client.HTTPSConnection(url_parsed[2])
        connection.request("GET", "/" + "/".join(url_parsed[3:]))
        response = connection.getresponse()
        if response.status != 200:
            connection.close()
            return HttpResponse(status=500)
        image = ContentFile(response.read(), name=str(user_id) + ".jpg")
        connection.close()
        new_user = UserProfile(user=user, profile_picture=image)
    else:
        new_user = UserProfile(user=user)
    new_user.save()
    return HttpResponse(status=201)

@csrf_exempt
def get_picture_url(request, user_id: int) -> JsonResponse:
    user = UserProfile.objects.get(user_id=user_id)
    if not user:
        return JsonResponse({'profile_picture': ""}, status=404)
    profile_picture = user.profile_picture.url
    return JsonResponse({'profile_picture': profile_picture}, status=200)

def get_image(request : HttpRequest, filename: str):
    if request.method != 'GET':
        return HttpResponse(status=405)
    image_path = request.path
    full_image_path = os.path.join(settings.MEDIA_ROOT, image_path.lstrip('/'))
    if os.path.exists(full_image_path):
        return FileResponse(open(full_image_path, 'rb'), content_type='image/jpeg')
    else:
       return HttpResponse(status=404)

def change_profile_picture(request : HttpRequest) -> JsonResponse:
    if request.method != 'POST':
        return JsonResponse({'status': 0, 'message': 'Only POST method is allowed'}, status=405)
    if not request.user.is_authenticated:
        return JsonResponse({'status': 0, 'message': 'User not connected'}, status=401)
    image = request.FILES['profile_picture']
    user = UserProfile.objects.get(user_id=request.user.id)
    user.profile_picture.save(f"{user.user_id}.jpg", image)
    user.save()
    return JsonResponse({'status': 1, 'message': 'Profile picture updated', 'new_profile_picture_url': user.profile_picture.url}, status=200)

@csrf_exempt
def game_stats_view(request, user_id):
    if request.method != 'GET':
        return JsonResponse({'status': 0, 'message': 'Only GET method is allowed'}, status=405)
    user_profile = UserProfile.objects.get(user__id=user_id)
    if not user_profile:
        return JsonResponse({'status': 0, 'message': 'User not found'}, status=404)
    games_won = Game.objects.filter(winner=user_profile)
    games_lost = Game.objects.filter(loser=user_profile)

    win_count = games_won.count()
    loss_count = games_lost.count()
    if win_count + loss_count == 0:
        return JsonResponse({'status': 1, 'total_games': 0}, status=200)

    games_data = []
    for game in games_won.union(games_lost):
        games_data.append({
            'is_winner': game.winner == user_profile,
            'opponent': game.loser.user.username if game.winner == user_profile else game.winner.user.username,
            'personal_score': game.winner_score if game.winner == user_profile else game.loser_score,
            'opponent_score': game.loser_score if game.winner == user_profile else game.winner_score,
            'game_date': game.game_date,
            'game_duration': game.game_duration,
        })

    response_data = {
        'status': 1,
        'total_games': win_count + loss_count,
        'total_wins': win_count,
        'win_percentage': round(win_count / (win_count + loss_count) * 100, 1),
        'games': games_data
    }

    return JsonResponse(response_data, status=200)

def personal_stats(request : HttpRequest):
    if request.method != 'GET':
        return JsonResponse({'status': 0, 'message': 'Only GET method is allowed'}, status=405)
    if not request.user.is_authenticated:
        return JsonResponse({'status': 0, 'message': 'User not connected'}, status=401)
    connection = client.HTTPConnection("users:8000")
    connection.request("GET", f"/game_stats/{request.user.id}/")
    response = connection.getresponse()
    data = json.loads(response.read().decode())
    connection.close()
    return JsonResponse(data, status=response.status)

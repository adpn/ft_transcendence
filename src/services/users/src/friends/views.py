from django.shortcuts import render
from django.http import JsonResponse, HttpRequest
from user_data.models import UserProfile
from .models import Relation

def get_friend_list(request : HttpRequest) -> JsonResponse:
    if request.method != 'GET':
        return JsonResponse({'status': 0, 'message': 'Method not allowed'}, status=405)
    if not request.user.is_authenticated:
        return JsonResponse({'status': 0, 'message': 'User not connected'}, status=401)
    user_profile = UserProfile.objects.get(user=request.user)
    friends = Relation.objects.filter(user=user_profile, status=True) | Relation.objects.filter(friend=user_profile, status=True)
    friend_list_data = []
    for item in friends:
        if item.user == user_profile:
            friend_list_data.append({'username': item.friend.user.username, 'profile_picture': item.friend.profile_picture.url})
        else:
            friend_list_data.append({'username': item.user.user.username, 'profile_picture': item.user.profile_picture.url})
    return JsonResponse({'status': 1, 'friends': friend_list_data}, status=200)

def get_friend_requests_list(request : HttpRequest) -> JsonResponse:
    if request.method != 'GET':
        return JsonResponse({'status': 0, 'message': 'Method not allowed'}, status=405)
    if not request.user.is_authenticated:
        return JsonResponse({'status': 0, 'message': 'User not connected'}, status=401)
    user_profile = UserProfile.objects.get(user=request.user)
    friends = Relation.objects.filter(friend=user_profile, status=False)
    friend_list_data = []
    for item in friends:
        friend_list_data.append({'username': item.user.user.username, 'profile_picture': item.user.profile_picture.url, 'id': item.id})
    return JsonResponse({'status': 1, 'friend_requests': friend_list_data}, status=200)

def accept_friend(request : HttpRequest, request_id : int) -> JsonResponse:
    if request.method != 'POST':
        return JsonResponse({'status': 0, 'message': 'Method not allowed'}, status=405)
    if not request.user.is_authenticated:
        return JsonResponse({'status': 0, 'message': 'User not connected'}, status=401)
    user_profile = UserProfile.objects.get(user=request.user)
    friend_request = Relation.objects.get(id=request_id)
    if friend_request.friend != user_profile:
        return JsonResponse({'status': 0, 'message': 'You are not the recipient of this request'}, status=403)
    friend_request.status = True
    friend_request.save()
    return JsonResponse({'status': 1, 'message': 'Friend request accepted'}, status=200)

def refuse_friend(request : HttpRequest, request_id : int) -> JsonResponse:
    if request.method != 'POST':
        return JsonResponse({'status': 0, 'message': 'Method not allowed'}, status=405)
    if not request.user.is_authenticated:
        return JsonResponse({'status': 0, 'message': 'User not connected'}, status=401)
    user_profile = UserProfile.objects.get(user=request.user)
    friend_request = Relation.objects.get(id=request_id)
    if friend_request.friend != user_profile:
        return JsonResponse({'status': 0, 'message': 'You are not the recipient of this request'}, status=403)
    friend_request.delete()
    return JsonResponse({'status': 1, 'message': 'Friend request refused'}, status=200)

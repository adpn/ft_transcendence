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
    if not friend_request:
        return JsonResponse({'status': 0, 'message': 'Friend request not found'}, status=404)
    if friend_request.friend != user_profile:
        return JsonResponse({'status': 0, 'message': 'You are not the recipient of this request'}, status=403)
    friend_request.status = True
    friend_request.save()
    return JsonResponse({'status': 1, 'message': 'Friend request accepted', 'friendship_id': friend_request.id}, status=200)

def decline_friend(request : HttpRequest, request_id : int) -> JsonResponse:
    if request.method != 'POST':
        return JsonResponse({'status': 0, 'message': 'Method not allowed'}, status=405)
    if not request.user.is_authenticated:
        return JsonResponse({'status': 0, 'message': 'User not connected'}, status=401)
    user_profile = UserProfile.objects.get(user=request.user)
    friend_request = Relation.objects.get(id=request_id)
    if not friend_request:
        return JsonResponse({'status': 0, 'message': 'Friend request not found'}, status=404)
    if friend_request.friend != user_profile:
        return JsonResponse({'status': 0, 'message': 'You are not the recipient of this request'}, status=403)
    user_id = friend_request.user.user.id
    friend_request.delete()
    return JsonResponse({'status': 1, 'message': 'Friend request declined', 'user_id': user_id}, status=200)

def cancel_friend_request(request: HttpRequest, request_id: int) -> JsonResponse:
    if request.method != 'POST':
        return JsonResponse({'status': 0, 'message': 'Method not allowed'}, status=405)
    if not request.user.is_authenticated:
        return JsonResponse({'status': 0, 'message': 'User not connected'}, status=401)
    user_profile = UserProfile.objects.get(user=request.user)
    friend_request = Relation.objects.get(id=request_id)
    if not friend_request:
        return JsonResponse({'status': 0, 'message': 'Friend request not found'}, status=404)
    if friend_request.user.user != request.user and friend_request.friend.user != request.user:
        return JsonResponse({'status': 0, 'message': 'You are not part of this friend request'}, status=403)
    if friend_request.status == True:
        return JsonResponse({'status': 0, 'message': 'This request has already been accepted'}, status=403)
    if friend_request.user != user_profile:
        return JsonResponse({'status': 0, 'message': 'You are not the sender of this request'}, status=403)
    user_id = friend_request.friend.user.id
    friend_request.delete()
    return JsonResponse({'status': 1, 'message': 'Friend request cancelled', 'user_id': user_id}, status=200)

def remove_friend(request: HttpRequest, request_id: int) -> JsonResponse:
    if request.method != 'POST':
        return JsonResponse({'status': 0, 'message': 'Method not allowed'}, status=405)
    if not request.user.is_authenticated:
        return JsonResponse({'status': 0, 'message': 'User not connected'}, status=401)
    friendship = Relation.objects.get(id=request_id)
    if not friendship:
        return JsonResponse({'status': 0, 'message': 'Friend not found'}, status=404)
    if friendship.user.user != request.user and friendship.friend.user != request.user:
        return JsonResponse({'status': 0, 'message': 'You are not part of this friendship'}, status=403)
    if friendship.status == False:
        return JsonResponse({'status': 0, 'message': 'This request not been accepted yet'}, status=403)
    user_id = friendship.friend.user.id if friendship.user.user == request.user else friendship.user.user.id
    friendship.delete()
    return JsonResponse({'status': 1, 'message': 'Friendship cancelled', 'user_id': user_id}, status=200)

def add_friend(request: HttpRequest, friend_id: int) -> JsonResponse:
    if request.method != 'POST':
        return JsonResponse({'status': 0, 'message': 'Method not allowed'}, status=405)
    if not request.user.is_authenticated:
        return JsonResponse({'status': 0, 'message': 'User not connected'}, status=401)
    user_profile = UserProfile.objects.get(user=request.user)
    friend_profile = UserProfile.objects.get(id=friend_id)
    if not friend_profile:
        return JsonResponse({'status': 0, 'message': 'User does not exist'}, status=404)
    if Relation.objects.filter(user=user_profile, friend=friend_profile).exists() or Relation.objects.filter(user=friend_profile, friend=user_profile).exists():
        return JsonResponse({'status': 0, 'message': 'Can\'t send a friend request to this user'}, status=403)
    new_relation = Relation(user=user_profile, friend=friend_profile)
    new_relation.save()
    return JsonResponse({'status': 1, 'message': 'Friend request sent', 'friendship_id': new_relation.id}, status=200)

from channels.middleware import BaseMiddleware
from django.db import close_old_connections

# from django.http import JsonResponse

# from http import client


# def get_user_from_token(token):
# 	try:
# 		# Decode the token and get the user ID
# 		payload = jwt.decode(token, "your_secret_key", algorithms=["HS256"])
# 		user_id = payload['user_id']
		
# 		# Retrieve the user from the database
# 		return User.objects.get(id=user_id)
# 	except Exception as e:
# 		return AnonymousUser()

class GameRoomAuthMiddleware(BaseMiddleware):
	"""
	Custom middleware that takes a JWT token from the query string and 
	authenticates the user.
	"""

	async def __call__(self, scope, receive, send):
		close_old_connections()

		# todo: perform a query to check if the room exists, if not reject 
		
		# Get the user from the token
		#scope['user'] = await get_user_from_token(token)
		
		# Call the next middleware or the consumer
		return await super().__call__(scope, receive, send)
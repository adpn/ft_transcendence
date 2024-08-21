from common import game

DEFAULT_BALL_SPEED = 20
MAX_BALL_SPEED = 40
BALL_ACCELERATION = 1.002
DEFAULT_RACKET_SPEED = 30
MAX_DIRY = 0.8
MAX_DEVIATION = 0.6

class PongLogic(game.GameLogic):
	def __init__(self):
		self.game_data = {
			"ball_posx": 500,
			"ball_posy": 500,
			"ball_size": 10,
			"racket_left_pos": 400,
			"racket_left_size": 200,
			"racket_right_pos": 400,
			"racket_right_size": 200,
			"score_left": 0,
			"score_right": 0
			}
		self.ball_dirx = 0.9
		self.ball_diry = 0.1
		self.ball_speed = DEFAULT_BALL_SPEED
		self.racket_speed = DEFAULT_RACKET_SPEED
		self.input = [[False, False], [False, False]]	# [player][direction] = pressed

	async def updateInput(self, dir, action, player):
		self.input[player][dir] = action

	async def gameTick(self):
		await self.update_rackets()
		await self.update_ball()
		return self.game_data	# try to do this in binary stuff instead of json ?

	async def update_rackets(self):
		if self.input[1][1]:
			self.game_data["racket_right_pos"] -= self.racket_speed
			if self.game_data["racket_right_pos"] < 0:
				self.game_data["racket_right_pos"] = 0
		if self.input[1][0]:
			self.game_data["racket_right_pos"] += self.racket_speed
			if self.game_data["racket_right_pos"] + self.game_data["racket_right_size"] > 1000:
				self.game_data["racket_right_pos"] = 1000 - self.game_data["racket_right_size"]
		if self.input[0][1]:
			self.game_data["racket_left_pos"] -= self.racket_speed
			if self.game_data["racket_left_pos"] < 0:
				self.game_data["racket_left_pos"] = 0
		if self.input[0][0]:
			self.game_data["racket_left_pos"] += self.racket_speed
			if self.game_data["racket_left_pos"] + self.game_data["racket_left_size"] > 1000:
				self.game_data["racket_left_pos"] = 1000 - self.game_data["racket_left_size"]

	async def update_ball(self):
		self.game_data["ball_posx"] += self.ball_dirx * self.ball_speed
		self.game_data["ball_posy"] += self.ball_diry * self.ball_speed
		await self.do_collision()
		if self.ball_speed < MAX_BALL_SPEED:
			self.ball_speed *= BALL_ACCELERATION
		await self.do_score()

	async def do_collision(self):
		if self.game_data["ball_posy"] - (self.game_data["ball_size"] / 2) <= 0:
			await self.bounce('u')
		elif self.game_data["ball_posy"] + (self.game_data["ball_size"] / 2) >= 1000:
			await self.bounce('d')
		elif ( self.game_data["ball_posx"] - (self.game_data["ball_size"] / 2) <= 15
			and self.game_data["racket_left_pos"] < self.game_data["ball_posy"] + (self.game_data["ball_size"] / 2)
			and self.game_data["racket_left_pos"] + self.game_data["racket_left_size"] > self.game_data["ball_posy"] - (self.game_data["ball_size"] / 2)):
			await self.bounce('l')
		elif ( self.game_data["ball_posx"] + (self.game_data["ball_size"] / 2) >= 985
			and self.game_data["racket_right_pos"] < self.game_data["ball_posy"] + (self.game_data["ball_size"] / 2)
			and self.game_data["racket_right_pos"] + self.game_data["racket_right_size"] > self.game_data["ball_posy"] - (self.game_data["ball_size"] / 2)):
			await self.bounce('r')

	async def bounce(self, side):
		if side == 'u':
			self.game_data["ball_posy"] = 0 + self.game_data["ball_size"] - self.game_data["ball_posy"]
			self.ball_diry *= -1
			return
		if side == 'd':
			self.game_data["ball_posy"] = 2000 - self.game_data["ball_size"] - self.game_data["ball_posy"]
			self.ball_diry *= -1
			return
		if side == 'l':
			limit = 15 + self.game_data["ball_size"] / 2
			racket_pos = self.game_data["racket_left_pos"]
			racket_half_size = self.game_data["racket_left_size"] / 2
		elif side == 'r':
			limit = 985 - self.game_data["ball_size"] / 2
			racket_pos = self.game_data["racket_right_pos"]
			racket_half_size = self.game_data["racket_right_size"] / 2
		remainingspeed = self.ball_speed - ((limit - self.game_data["ball_posx"] + self.ball_dirx * self.ball_speed) / self.ball_dirx)
		self.game_data["ball_posy"] -= self.ball_diry * remainingspeed
		relative_racket_hit = -((racket_pos + racket_half_size - self.game_data["ball_posy"]) / racket_half_size)
		self.ball_diry += relative_racket_hit * MAX_DEVIATION
		if (self.ball_diry > MAX_DIRY):
			self.ball_diry = MAX_DIRY
		elif (self.ball_diry < -MAX_DIRY):
			self.ball_diry = -MAX_DIRY
		self.ball_dirx = (1 - await get_abs(self.ball_diry)) * -(self.ball_dirx / await get_abs(self.ball_dirx)) # self.ball_dirx cannot be 0
		self.game_data["ball_posx"] = limit + self.ball_dirx * remainingspeed
		self.game_data["ball_posy"] += self.ball_diry * remainingspeed

	async def do_score(self):
		if self.game_data["ball_posx"] < 0:
			await self.goal('l')
		elif self.game_data["ball_posx"] > 1000:
			await self.goal('r')

# doesn't check endgame yet
	async def goal(self, side):
		if side == 'l':
			self.game_data["score_right"] += 1
			self.ball_dirx = -0.9
		elif side == 'r':
			self.game_data["score_left"] += 1
			self.ball_dirx = 0.9
		self.ball_diry = 0.1
		self.ball_speed = DEFAULT_BALL_SPEED
		self.game_data["ball_posx"] = 500
		self.game_data["ball_posy"] = 500
		self.game_data["racket_left_pos"] = 400
		self.game_data["racket_left_size"] = 200
		self.game_data["racket_right_pos"] = 400
		self.game_data["racket_right_size"] = 200


async def get_abs(value):
	if value < 0:
		return -value
	return value

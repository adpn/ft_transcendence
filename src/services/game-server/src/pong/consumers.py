from common import game
import time

DEF_BALL_SIZE = 10
DEF_BALL_SPEED = 20
MAX_BALL_SPEED = 50
BALL_ACCELERATION = 1.0012
DEF_RACKET_SIZE = 150
DEF_RACKET_POS = 500 - DEF_RACKET_SIZE / 2
DEF_RACKET_SPEED = 25
START_DEVIATION = 0.04
MAX_DIRY = 0.8
MAX_DEVIATION = 0.6
MAX_SCORE = 5

START_PAUSE = 60

BOUNCE_UP = 0
BOUNCE_DOWN = 1
BOUNCE_LEFT = 2
BOUNCE_RIGHT = 3

class PongLogic(game.GameLogic):
	def __init__(self):
		# client data
		self.ball_pos = [500, 500]		# x,y
		self.ball_size = DEF_BALL_SIZE
		self.racket_pos = [DEF_RACKET_POS, DEF_RACKET_POS]	# left,right
		self.racket_size = [DEF_RACKET_SIZE, DEF_RACKET_SIZE]	# left,right
		self.score = [0, 0]				# left,right
		# server data
		self.ball_dirx = 1 - START_DEVIATION
		self.ball_diry = START_DEVIATION
		self.ball_speed = DEF_BALL_SPEED
		self.racket_speed = DEF_RACKET_SPEED
		self.input = [[False, False], [False, False]]	# [player][direction]
		self.time = 0.0
		self.date = ""
		self.game_id = 0
		self.player0_id = 0
		self.player1_id = 0
		self.pause = START_PAUSE
		# event flags
		self.goalEvent = False
		self.playerWin = -1

	async def update(self, data, player):
		# give up
		# self.players[player]
		if data[0]:
			await self.game_end(1 - player)
			return
		# input
		self.input[player][data[1]] = data[2]

	async def gameTick(self):
		await self.update_rackets()
		if (self.pause):
			self.pause -= 1
		else:
			await self.update_ball()
		return {"type": "tick", "b": self.ball_pos, "r": self.racket_pos }

	async def startEvent(self):
		self.__init__()
		self.time = time.time()
		self.date = time.asctime(time.localtime(self.time)) # IT RETURNS UTC I DON'T KNOW WHY
		return { "type": "start", "ball_size": self.ball_size, "racket_size": self.racket_size, "score": self.score }

	async def sendEvent(self):
		if self.goalEvent:
			self.goalEvent = False
			yield { "type": "goal", "score": self.score }
		if self.playerWin != -1:
			yield { "type": "win", "player": self.playerWin, "loser": 1 - self.playerWin, "score": self.score }

	async def update_rackets(self):
		if self.input[1][1]:
			self.racket_pos[1] -= self.racket_speed
			if self.racket_pos[1] < 0:
				self.racket_pos[1] = 0
		if self.input[1][0]:
			self.racket_pos[1] += self.racket_speed
			if self.racket_pos[1] + self.racket_size[1] > 1000:
				self.racket_pos[1] = 1000 - self.racket_size[1]
		if self.input[0][1]:
			self.racket_pos[0] -= self.racket_speed
			if self.racket_pos[0] < 0:
				self.racket_pos[0] = 0
		if self.input[0][0]:
			self.racket_pos[0] += self.racket_speed
			if self.racket_pos[0] + self.racket_size[0] > 1000:
				self.racket_pos[0] = 1000 - self.racket_size[0]

	async def update_ball(self):
		self.ball_pos[0] += self.ball_dirx * self.ball_speed
		self.ball_pos[1] += self.ball_diry * self.ball_speed
		await self.do_collision()
		if self.ball_speed < MAX_BALL_SPEED:
			self.ball_speed *= BALL_ACCELERATION
		await self.do_score()

	async def do_collision(self):
		if self.ball_pos[1] - (self.ball_size / 2) <= 0:
			await self.bounce(BOUNCE_UP)
		elif self.ball_pos[1] + (self.ball_size / 2) >= 1000:
			await self.bounce(BOUNCE_DOWN)
		elif ( self.ball_pos[0] - (self.ball_size / 2) <= 15
			and self.racket_pos[0] < self.ball_pos[1] + (self.ball_size / 2)
			and self.racket_pos[0] + self.racket_size[0] > self.ball_pos[1] - (self.ball_size / 2)):
			await self.bounce(BOUNCE_LEFT)
		elif ( self.ball_pos[0] + (self.ball_size / 2) >= 985
			and self.racket_pos[1] < self.ball_pos[1] + (self.ball_size / 2)
			and self.racket_pos[1] + self.racket_size[1] > self.ball_pos[1] - (self.ball_size / 2)):
			await self.bounce(BOUNCE_RIGHT)

	async def bounce(self, side):
		if side == BOUNCE_UP:
			self.ball_pos[1] = 0 + self.ball_size - self.ball_pos[1]
			self.ball_diry *= -1
			return
		if side == BOUNCE_DOWN:
			self.ball_pos[1] = 2000 - self.ball_size - self.ball_pos[1]
			self.ball_diry *= -1
			return
		if side == BOUNCE_LEFT:
			limit = 15 + self.ball_size / 2
			racket_pos = self.racket_pos[0]
			racket_half_size = self.racket_size[0] / 2
		elif side == BOUNCE_RIGHT:
			limit = 985 - self.ball_size / 2
			racket_pos = self.racket_pos[1]
			racket_half_size = self.racket_size[1] / 2
		remainingspeed = self.ball_speed - ((limit - self.ball_pos[0] + self.ball_dirx * self.ball_speed) / self.ball_dirx)
		self.ball_pos[1] -= self.ball_diry * remainingspeed
		relative_racket_hit = -((racket_pos + racket_half_size - self.ball_pos[1]) / racket_half_size)
		self.ball_diry += relative_racket_hit * MAX_DEVIATION
		if (self.ball_diry > MAX_DIRY):
			self.ball_diry = MAX_DIRY
		elif (self.ball_diry < -MAX_DIRY):
			self.ball_diry = -MAX_DIRY
		self.ball_dirx = (1 - await get_abs(self.ball_diry)) * -(self.ball_dirx / await get_abs(self.ball_dirx)) # self.ball_dirx cannot be 0
		self.ball_pos[0] = limit + self.ball_dirx * remainingspeed
		self.ball_pos[1] += self.ball_diry * remainingspeed

	async def do_score(self):
		if self.ball_pos[0] < 0:
			await self.goal(1)
		elif self.ball_pos[0] > 1000:
			await self.goal(0)

	async def goal(self, player):
		self.goalEvent = True
		self.score[player] += 1
		if self.score[player] >= MAX_SCORE:
			await self.game_end(player)
			return
		self.pause = START_PAUSE
		if player == 0:
			self.ball_dirx = -(1 - START_DEVIATION)
		elif player == 1:
			self.ball_dirx = (1 - START_DEVIATION)
		self.ball_diry = START_DEVIATION
		self.ball_speed = DEF_BALL_SPEED
		self.ball_pos[0] = 500
		self.ball_pos[1] = 500
		self.racket_pos[0] = DEF_RACKET_POS
		self.racket_pos[1] = DEF_RACKET_POS

	async def game_end(self, player):
		self.time = time.time() - self.time
		self.playerWin = player
		# add entry to database


async def get_abs(value):
	if value < 0:
		return -value
	return value

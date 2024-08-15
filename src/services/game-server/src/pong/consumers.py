from common import game

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
		self.ball_dirx = 1.0
		self.ball_diry = 0.0
		self.ball_speed = 10
		self.maxdeviation = 0.5
		self.maxdiry = 0.9
		self.racket_speed = 10
		self.left_up = False
		self.left_down = False
		self.right_up = False
		self.right_down = False

	def update(self, data):
		self.left_up = data["left_up"]
		self.left_down = data["left_down"]
		self.right_up = data["right_up"]
		self.right_down = data["right_down"]
		self.gameTick()
		return self.game_data

	def gameTick(self):
		self.update_rackets()
		self.update_ball()

	def update_rackets(self):
		if self.right_up:
			self.game_data["racket_right_pos"] -= self.racket_speed
			if self.game_data["racket_right_pos"] < 0:
				self.game_data["racket_right_pos"] = 0
		if self.right_down:
			self.game_data["racket_right_pos"] += self.racket_speed
			if self.game_data["racket_right_pos"] + self.game_data["racket_right_size"] > 1000:
				self.game_data["racket_right_pos"] = 1000 - self.game_data["racket_right_size"]
		if self.left_up:
			self.game_data["racket_left_pos"] -= self.racket_speed
			if self.game_data["racket_left_pos"] < 0:
				self.game_data["racket_left_pos"] = 0
		if self.left_down:
			self.game_data["racket_left_pos"] += self.racket_speed
			if self.game_data["racket_left_pos"] + self.game_data["racket_left_size"] > 1000:
				self.game_data["racket_left_pos"] = 1000 - self.game_data["racket_left_size"]

	def update_ball(self):
		self.game_data["ball_posx"] += self.ball_dirx * self.ball_speed
		self.game_data["ball_posy"] += self.ball_diry * self.ball_speed
		self.do_collision()
		self.ball_speed *= 1.05
		self.do_score()

	def do_collision(self):
		if self.game_data["ball_posy"] - (self.game_data["ball_size"] / 2) <= 0:
			self.bounce('u')
		elif self.game_data["ball_posy"] + (self.game_data["ball_size"] / 2) >= 1000:
			self.bounce('d')
		elif ( self.game_data["ball_posx"] - (self.game_data["ball_size"] / 2) <= 15
			and self.game_data["racket_left_pos"] < self.game_data["ball_posy"] + (self.game_data["ball_size"] / 2)
			and self.game_data["racket_left_pos"] + self.game_data["racket_left_size"] > self.game_data["ball_posy"] - (self.game_data["ball_size"] / 2)):
			self.bounce('l')
		elif ( self.game_data["ball_posx"] + (self.game_data["ball_size"] / 2) >= 985
			and self.game_data["racket_right_pos"] < self.game_data["ball_posy"] + (self.game_data["ball_size"] / 2)
			and self.game_data["racket_right_pos"] + self.game_data["racket_right_size"] > self.game_data["ball_posy"] - (self.game_data["ball_size"] / 2)):
			self.bounce('r')

	def bounce(self, side):
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
		self.ball_diry += (racket_pos + racket_half_size - self.game_data["ball_posy"]) / racket_half_size * self.maxdeviation
		if (self.ball_diry > self.maxdiry):
			self.ball_diry = self.maxdiry
		elif (self.ball_diry < -self.maxdiry):
			self.ball_diry = -self.maxdiry
		self.ball_dirx = (1 - abs(self.ball_diry)) * (self.ball_dirx / abs(self.ball_dirx)) # self.ball_dirx cannot be 0
		self.game_data["ball_posx"] = limit + self.ball_dirx * remainingspeed
		self.game_data["ball_posy"] += self.ball_diry * remainingspeed

	def do_score(self):
		if self.game_data["ball_posx"] < 0:
			self.goal('l')
		elif self.game_data["ball_posx"] > 1000:
			self.goal('r')

# doesn't check endgame yet
	def goal(self, side):
		if side == 'l':
			self.game_data["score_right"] += 1
			self.ball_dirx = -1.0
		elif side == 'r':
			self.game_data["score_left"] += 1
			self.ball_dirx = 1.0
		self.ball_diry = 0.0
		self.ball_speed = 10
		self.game_data["ball_posx"] = 500
		self.game_data["ball_posy"] = 500
		self.game_data["racket_left_pos"] = 400
		self.game_data["racket_left_size"] = 200
		self.game_data["racket_right_pos"] = 400
		self.game_data["racket_right_size"] = 200

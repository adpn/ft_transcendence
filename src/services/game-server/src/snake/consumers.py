import time
from random import randrange

GRID_WIDTH = 20		 # play area
GRID_HEIGHT = 20	 # play area
START_SIZE = 3
START_PAUSE = 60
SNAKE_SPEED = 10	# higher = slower, amount of ticks between moves
SNAKE_ACCEL = 2		# subtracts from speed
SNAKE_MAX_SPEED = 4
ACCEL_TIME = 1200	# in ticks
APPLE_SPEED = 100	# same as above

EMPTY = 0	# Background color index (has to be 0)
SNAKE = 1
SNAKE1 = 2
HEAD = 3
HEAD1 = 4
APPLE = 5

GRID_COLORS = ["#202020"]*(APPLE + 1)
GRID_COLORS[EMPTY] = "#202020"
GRID_COLORS[SNAKE] = "#b0b0b0"
GRID_COLORS[SNAKE1] = "#1cad33"
GRID_COLORS[HEAD] = "#ffffff"
GRID_COLORS[HEAD1] = "#5ced73"
GRID_COLORS[APPLE] = "#f01e2c"
# GRID_COLORS = {EMPTY: "#202020", SNAKE: "#b0b0b0", SNAKE1: "#1cad33", HEAD: "#ffffff", HEAD1: "#5ced73", APPLE: "#f01e2c"}

DIR_UP = 0
DIR_DOWN = 3
DIR_LEFT = 1
DIR_RIGHT = 2
OPPOSITES = 3		# always equals sum of opposite directions

class SnakeLogic(object):
	def __init__(self):
		# client data
		# server data
		self.grid = []
		for _ in range(GRID_WIDTH):
			self.grid.append(bytearray(GRID_HEIGHT))
		self.snakes = [[], []]						# [player][tiles][x,y]
		self.input_queue = [[], []]
		self.last_move = [DIR_RIGHT, DIR_LEFT]
		self.growing = [0, 0]
		self.collided = [False, False]
		self.add_tiles = []			# elements: [x, y, thing]
		self.speed = SNAKE_SPEED
		self.idle_time = SNAKE_SPEED
		self.accel_time = ACCEL_TIME / SNAKE_SPEED
		self.apple_time = APPLE_SPEED
		self.time = 0.0
		self.date = ""
		self.game_id = 0
		self.player0_id = 0
		self.player1_id = 0
		self.pause = START_PAUSE
		# event flags
		self.grow = False
		self.playerWin = -1
		# init
		self.initSnakes()

	@property
	def score(self):
		return [len(self.snakes[0]), len(self.snakes[1])]

	def initSnakes(self):
		self.snakes = [[[int(GRID_WIDTH / 4), int(GRID_HEIGHT / 2)]], [[int(GRID_WIDTH * 3 / 4), int(GRID_HEIGHT / 2)]]]
		self.init_addToGrid(self.snakes[0][0], SNAKE)
		self.init_addToGrid(self.snakes[1][0], SNAKE)
		start_size = START_SIZE
		if start_size > int(GRID_WIDTH / 4 - 1):
			start_size = int(GRID_WIDTH / 4 - 1)
		while (start_size > 1):
			self.snakes[0].insert(0, self.init_getNextTile(self.snakes[0][0], DIR_LEFT))
			self.snakes[1].insert(0, self.init_getNextTile(self.snakes[1][0], DIR_RIGHT))
			self.init_addToGrid(self.snakes[0][0], SNAKE)
			self.init_addToGrid(self.snakes[1][0], SNAKE)
			start_size -= 1

	def init_getNextTile(self, tile, dir):
		if dir == DIR_UP:
			return [tile[0], tile[1] - 1]
		if dir == DIR_DOWN:
			return [tile[0], tile[1] + 1]
		if dir == DIR_LEFT:
			return [tile[0] - 1, tile[1]]
		if dir == DIR_RIGHT:
			return [tile[0] + 1, tile[1]]

	def init_addToGrid(self, tile, value):
		self.grid[tile[0]][tile[1]] = value

	# data[1] = direction, data[2] = pressed or released (true or false)
	async def update(self, data, player):
		# give up
		if data[0]:
			await self.gameEnd(1 - player)
			return
		await self.updateInput(data, player)

	async def updateInput(self, data, player):
		# input msg will only be key down for now (data[2] == true):
		if (data[1] not in [DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT]):
			return
		self.input_queue[player].append(data[1])

	async def gameTick(self):
		if (self.pause):
			self.pause -= 1
		else:
			await self.apple()
			await self.move()
		message = {"type": "tick", "tiles": self.add_tiles.copy() }		# tiles to add or clear
		self.add_tiles.clear()
		return message

	async def startEvent(self):
		self.__init__()							# is this fine? does it reset everything? (i don't think so)
		self.time = time.time()
		self.date = time.asctime(time.localtime(self.time)) # IT RETURNS UTC I DON'T KNOW WHY
		return { "type": "start", "grid": [GRID_WIDTH, GRID_HEIGHT], "snakes": self.snakes, "color": [SNAKE, SNAKE1, HEAD, HEAD1], "colors": GRID_COLORS }

	async def sendEvent(self):
		if self.grow:
			self.grow = False
			yield { "type": "grow", "len": [len(self.snakes[0]), len(self.snakes[1])] }
		if self.playerWin != -1:
			yield { "type": "win", "player": self.playerWin, "loser": 1 - self.playerWin, "score": [len(self.snakes[0]), len(self.snakes[1])] }

	async def gameEnd(self, player):
		self.time = time.time() - self.time
		self.playerWin = player
		# add entry to database

	async def apple(self):
		if self.apple_time:
			self.apple_time -= 1
			return
		self.apple_time = APPLE_SPEED
		spawn_tries = 1
		spawn_tile = [randrange(GRID_WIDTH), randrange(GRID_HEIGHT)]
		while (self.grid[spawn_tile[0]][spawn_tile[1]] != EMPTY and spawn_tries < 10):
			spawn_tile = [randrange(GRID_WIDTH), randrange(GRID_HEIGHT)]
			spawn_tries += 1
		if (self.grid[spawn_tile[0]][spawn_tile[1]] == EMPTY):
			await self.addToGrid(spawn_tile, APPLE)

	async def move(self):
		if self.idle_time:
			self.idle_time -= 1
			return
		self.idle_time = self.speed
		if self.speed > SNAKE_MAX_SPEED:
			self.accel_time -= 1
			if self.accel_time <= 0:
				self.speed -= SNAKE_ACCEL
				self.accel_time = ACCEL_TIME / SNAKE_SPEED
		for player in [0, 1]:
			while self.input_queue[player] and (self.last_move[player] == self.input_queue[player][0] or self.last_move[player] + self.input_queue[player][0] == OPPOSITES):
				self.input_queue[player].pop(0)
			if self.input_queue[player]:
				self.last_move[player] = self.input_queue[player].pop(0)
			next_tile = await self.getNextTile(self.snakes[player][-1], self.last_move[player])
			await self.snack(player, next_tile)
			self.snakes[player].append(next_tile)
			if self.growing[player]:
				self.growing[player] -= 1
			else:
				await self.addToGrid(self.snakes[player][0], EMPTY)
				del self.snakes[player][0]
		if await self.collisions():
			await self.addToGrid(self.snakes[0][-2], SNAKE)
			await self.addToGrid(self.snakes[1][-2], SNAKE, SNAKE1)
			await self.addToGrid(self.snakes[0][-1], SNAKE, HEAD)
			await self.addToGrid(self.snakes[1][-1], SNAKE, HEAD1)

	async def collisions(self):
		if self.snakes[0][-1] == self.snakes[1][-1]:
			await self.resolveRemise()
			return
		player_died = -1
		for player in [0, 1]:
			if self.snakes[player][-1][0] < 0 or self.snakes[player][-1][0] >= GRID_WIDTH or self.snakes[player][-1][1] < 0 or self.snakes[player][-1][1] >= GRID_HEIGHT:
				player_died += player + 1
			elif self.grid[self.snakes[player][-1][0]][self.snakes[player][-1][1]] == SNAKE:
				player_died += player + 1
		if player_died == 2:
			await self.resolveRemise()
		elif player_died != -1:
			await self.gameEnd(1 - player_died)
		else: return 1

	async def resolveRemise(self):
		if len(self.snakes[0]) > len(self.snakes[1]):	# biggest snake wins
			await self.gameEnd(0)
		elif len(self.snakes[1]) > len(self.snakes[0]):
			await self.gameEnd(1)
		else:
			await self.gameEnd(randrange(2))			# if same size: random wins (for now)

	async def snack(self, player, tile):
		if tile[0] < 0 or tile[0] >= GRID_WIDTH or tile[1] < 0 or tile[1] >= GRID_HEIGHT:
			return
		if self.grid[tile[0]][tile[1]] == APPLE:
			self.grow = True
			self.growing[player] += 1

	async def getNextTile(self, tile, dir):
		if dir == DIR_UP:
			return [tile[0], tile[1] - 1]
		if dir == DIR_DOWN:
			return [tile[0], tile[1] + 1]
		if dir == DIR_LEFT:
			return [tile[0] - 1, tile[1]]
		if dir == DIR_RIGHT:
			return [tile[0] + 1, tile[1]]

	async def addToGrid(self, tile, value, color = -1):
		if color == -1:
			color = value
		self.add_tiles.append([tile[0], tile[1], color])
		self.grid[tile[0]][tile[1]] = value

from common import game
import time

GRID_WIDTH = 30		 # play area
GRID_HEIGHT = 20	 # play area
START_SIZE = 3
START_PAUSE = 60
SNAKE_SPEED = 10	# higher = slower, amount of ticks between moves
APPLE_SPEED = 100	# same as above

EMPTY = 0	# Background color (has to be 0)
SNAKE = 1
APPLE = 5
grid_colors = {EMPTY: 0x000000, SNAKE: 0xffffff, APPLE: 0xf01e2c}

DIR_UP = 0
DIR_DOWN = 1
DIR_LEFT = 2
DIR_RIGHT = 3

class SnakeLogic(game.GameLogic):
	def __init__(self):
		# client data
		# server data
		self.grid = [bytearray(GRID_HEIGHT)]*GRID_WIDTH
		self.snakes = [[], []]						# [player][tiles][x,y]
		self.input = [[DIR_RIGHT], [DIR_LEFT]]		# [player][pressed]
		self.zombie_input = [True, True]
		self.growing = [0, 0]
		self.collided = [False, False]
		self.add_tiles = []			# elements: [x, y, thing]
		self.idle_time = SNAKE_SPEED
		self.apple_time = APPLE_SPEED
		self.time = 0.0
		self.date = ""
		self.game_id = 0
		self.player0_id = 0
		self.player1_id = 0
		self.pause = START_PAUSE
		# event flags
		self.playerWin = -1
		# init
		self.initSnakes()

	async def initSnakes(self):
		self.snakes = [[[int(GRID_WIDTH / 4), int(GRID_HEIGHT / 2)]], [[int(GRID_WIDTH * 3 / 4), int(GRID_HEIGHT / 2)]]]
		await self.addToGrid(self.snakes[0][0], SNAKE)
		await self.addToGrid(self.snakes[1][0], SNAKE)
		start_size = START_SIZE
		if start_size > int(GRID_WIDTH / 4 - 1):
			start_size = int(GRID_WIDTH / 4 - 1)
		while (start_size > 1):
			self.snakes[0].insert(0, await self.getNextTile(self.snakes[0][0], DIR_LEFT))
			self.snakes[1].insert(0, await self.getNextTile(self.snakes[1][0], DIR_RIGHT))
			await self.addToGrid(self.snakes[0][0], SNAKE)
			await self.addToGrid(self.snakes[1][0], SNAKE)
			start_size -= 1


	# data[1] = direction, data[2] = pressed or released (true or false)
	async def update(self, data, player):
		# give up
		if data[0]:
			await self.gameEnd(1 - player)
			return
		await self.updateInput(data, player)

	async def updateInput(self, data, player):		# there just has to be a cleaner way
		self.input[player].remove(data[1])
		if data[2]:
			if self.zombie_input[player]:
				self.input[player].clear()
				self.zombie_input[player] = False
			self.input[player].append(data[1])
		elif not len(self.input[player]):
			self.input[player].append(data[1])
			self.zombie_input[player] = True

	async def gameTick(self):
		if (self.pause):
			self.pause -= 1
		else:
			await self.apple()
			await self.move()
		message = {"type": "tick", "tiles": self.add_tiles }		# tiles to add or clear
		self.add_tiles.clear()
		return message

	async def startEvent(self):
		self.__init__()
		self.time = time.time()
		self.date = time.asctime(time.localtime(self.time)) # IT RETURNS UTC I DON'T KNOW WHY
		return { "type": "start", "grid": [GRID_WIDTH, GRID_HEIGHT], "snakes": self.snakes, "color": SNAKE, "colors": grid_colors }

	async def sendEvent(self):
		if self.playerWin != -1:
			yield { "type": "win", "player": self.playerWin }

	async def gameEnd(self, player):
		self.time = time.time() - self.time
		self.playerWin = player
		# add entry to database

	async def apple(self):
		if self.apple_time:
			self.apple_time -= 1
			return
		self.apple_time = APPLE_SPEED
		await self.addToGrid([15, 10], APPLE)		# spawn apple in random spot (rotate between field halves?)

	async def move(self):
		if self.idle_time:
			self.idle_time -= 1
			return
		self.idle_time = SNAKE_SPEED
		for player in [0, 1]:
			next_tile = await self.getNextTile(self.snakes[player][-1], self.input[player][-1])
			await self.snack(player, next_tile)
			self.snakes[player].append(next_tile)
			if self.growing[player]:
				self.growing[player] -= 1
			else:
				await self.addToGrid(self.snakes[player][0], EMPTY)
				del self.snakes[player][0]
		await self.collisions()
		await self.addToGrid(self.snakes[0][-1], SNAKE)
		await self.addToGrid(self.snakes[1][-1], SNAKE)

	async def collisions(self):
		if self.snakes[0][-1] == self.snakes[1][-1]:
			await self.resolveRemise()
			return
		player_died = -1
		if self.snakes[0][-1][0] < 0 or self.snakes[0][-1][0] >= GRID_WIDTH or self.snakes[0][-1][1] < 0 or self.snakes[0][-1][1] >= GRID_HEIGHT:
			player_died += 1
		elif self.grid[self.snakes[0][-1][0], self.snakes[0][-1][1]] == SNAKE:
			player_died += 1
		if self.snakes[1][-1][0] < 0 or self.snakes[1][-1][0] >= GRID_WIDTH or self.snakes[1][-1][1] < 0 or self.snakes[1][-1][1] >= GRID_HEIGHT:
			player_died += 2
		elif self.grid[self.snakes[1][-1][0], self.snakes[1][-1][1]] == SNAKE:
			player_died += 2
		if player_died == 2:
			await self.resolveRemise()
		elif player_died != -1:
			await self.gameEnd(1 - player_died)

	async def resolveRemise(self):
		if len(self.snakes[0]) > len(self.snakes[1]):	# biggest snake wins
			await self.gameEnd(0)
		else:
			await self.gameEnd(1)			# if same size: '1' wins (for now)

	async def snack(self, player, tile):
		if tile[0] < 0 or tile[0] >= GRID_WIDTH or tile[1] < 0 or tile[1] >= GRID_HEIGHT:
			return
		if self.grid[tile[0], tile[1]] == APPLE:
			self.growing[player] += 1

	async def getNextTile(self, tile, dir):
		if dir == DIR_UP:
			return [tile[0], tile[1] + 1]
		if dir == DIR_DOWN:
			return [tile[0], tile[1] - 1]
		if dir == DIR_LEFT:
			return [tile[0] - 1, tile[1]]
		if dir == DIR_RIGHT:
			return [tile[0] + 1, tile[1]]

	async def addToGrid(self, tile, value):
		self.add_tiles.append([tile[0], tile[1], value])
		self.grid[tile[0], tile[1]] = value

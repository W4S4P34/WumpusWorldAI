##########################
#   Built-in Libraries   #
import numpy as np
from enum import IntEnum
import os

class State(IntEnum):
	EP = 0 # empty path
	W = 1 # wumpus
	P = 2 # pit
	G = 3 # gold
	B = 4 # breeze
	S = 5 # stench
	BS = 6 # breeze & stench
	GB = 7 # gold & breeze
	GS = 8 # gold & stench
	GBS = 9 # gold & breeze & stench


class MapController:
	__instance = None
	def GetInstance():
		if MapController.__instance == None:
			MapController()
		return MapController.__instance

	def __init__(self):
		if MapController.__instance == None:
			_map,agentPosition = ReadFile()
			self.width = len(_map)
			self.height = len(_map[0])
			self.map = ConvertToMyMap(_map,self.width,self.height)
			self.originMap = self.map
			self.agentPosition = tuple(agentPosition)
			self.agentMap = np.full(self.map.shape,None)
			self.agentMap[self.agentPosition] = self.map[self.agentPosition]
			self.cave = self.agentPosition
			MapController.__instance = self
	def ResetOriginMap(self):
		self.map = self.originMap
		self.agentMap = np.full(self.map.shape,None)
		self.agentPosition = self.cave
		self.agentMap[self.agentPosition] = self.map[self.agentPosition]
	def ConvertToMyIndex(self,_pos):
		pass
	def ConvertStadardIndex(self,_pos):
		pass
	def UpdateAgentMap(self,_pos,state):
		self.agentMap[_pos] = state
		self.map[_pos] = state
	def GetAgentPosition(self):
		return self.agentPosition
	def AgentMove(self,_pos : tuple):
		self.agentPosition = _pos
		self.agentMap[self.agentPosition] = self.map[self.agentPosition]
	def Shoot(self,_pos : tuple):
		if(self.map[_pos] == int(State.W)):
			list_change = []
			adj_cell = [(1,0),(-1,0),(0,1),(0,-1)]
			list_change.append(_pos)
			self.map[_pos] = int(State.EP)
			change = self.ChangeState(_pos)
			self.map[_pos] = change
			self.agentMap[_pos] = change
			for i in adj_cell:
				tmp = (_pos[0]+i[0],_pos[1]+i[1])
				if( not (tmp[0] >= 0 and tmp[0] < self.width and tmp[1] >= 0 and tmp[1] < self.height)):
					continue
				change = self.ChangeState(tmp)
				if(self.agentMap[tmp] != None):
					if(change != int(State.S) and change != int(State.BS) and change != int(State.GS) and change != int(State.GBS)):
						list_change.append(tmp)
					self.agentMap[tmp] = change
					self.map[tmp] = change
				else:
					self.map[tmp] = change
			return list_change
		return []
	def ChangeState(self,_pos : tuple):
		adj_cell = [(1,0),(-1,0),(0,1),(0,-1)]
		is_wumpus = False
		is_pit = False
		for i in adj_cell:
			tmp = (_pos[0]+i[0],_pos[1]+i[1])
			if( not (tmp[0] >= 0 and tmp[0] < self.width and tmp[1] >= 0 and tmp[1] < self.height)):
				continue
			if(self.map[tmp] == int(State.W)):
				is_wumpus = True
			elif(self.map[tmp] == int(State.P)):
				is_pit = True
		if(self.map[_pos] == int(State.G) or self.map[_pos] == int(State.GB) or self.map[_pos] == int(State.GS) or self.map[_pos] == int(State.GBS)):
			if(is_wumpus and is_pit):
				return int(State.GBS)
			if(is_wumpus):
				return int(State.GS)
			if(is_pit):
				return int(State.GB)
			return int(State.G)
		else:
			if(is_wumpus and is_pit):
				return int(State.BS)
			if(is_wumpus):
				return int(State.S)
			if(is_pit):
				return int(State.B)
			return int(State.EP)
def ConvertToMyMap(_map,width,height):
	_maze = np.zeros(_map.shape,dtype = np.uint8)
	for i in range(width):
		for j in range(height):
			if(_map[i,j] == '-'):
				_maze[i,j] += int(State.EP)
			elif(_map[i,j] == 'W'):
				_maze[i,j] += int(State.W)
			elif(_map[i,j] == 'P'):
				_maze[i,j] += int(State.P)
			elif(_map[i,j] == 'G'):
				_maze[i,j] += int(State.G)
			elif(_map[i,j] == 'B'):
				_maze[i,j] += int(State.B)
			elif(_map[i,j] == 'S'):
				_maze[i,j] += int(State.S)
			elif(_map[i,j] == 'BS' or _map[i,j] == 'SB'):
				_maze[i,j] += int(State.BS)
			elif(_map[i,j] == 'GB' or _map[i,j] == 'BG'):
				_maze[i,j] += int(State.GB)
			elif(_map[i,j] == 'GS' or _map[i,j] == 'SG'):
				_maze[i,j] += int(State.GS)
			elif(_map[i,j] == 'GBS' or _map[i,j] == 'GSB' or _map[i,j] == 'BGS' or _map[i,j] == 'BSG' or _map[i,j] == 'SGB' or _map[i,j] == 'SBG'):
				_maze[i,j] += int(State.GBS)
	return _maze

def ReadFile():
	path = os.getcwd() + "\SANDBOX\INPUT\map-10.txt"
	file = open(path,'rt')
	_sizeMap = int(file.readline())
	_list_map = []
	for i in range(_sizeMap):
		line = file.readline().replace('\n','')
		_list_map.append(line.split('.'))
	_map = np.array(_list_map)
	return _map,np.argwhere(_map == 'A')[0]


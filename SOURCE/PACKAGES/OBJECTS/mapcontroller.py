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
			self.agentPosition = tuple(agentPosition)
			self.agentMap = np.full(self.map.shape,None)
			self.agentMap[self.agentPosition] = self.map[self.agentPosition]
			self.cave = self.agentPosition
			MapController.__instance = self
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
	path = os.getcwd() + "\INPUT\map-01.txt"
	file = open(path,'rt')
	_sizeMap = int(file.readline())
	_list_map = []
	for i in range(_sizeMap):
		line = file.readline().replace('\n','')
		_list_map.append(line.split('.'))
	_map = np.array(_list_map)
	return _map,np.argwhere(_map == 'A')[0]

##########################
#    Custom Libraries    #
import mapcontroller as mapctrl
##########################
#   Built-in Libraries   #
from queue import heappop,heappush
from enum import IntEnum
from pysat.solvers import Glucose4


def h_n(start_pos:tuple,des_pos:tuple):
    return abs(start_pos[0] - des_pos[0]) + abs(start_pos[1] - des_pos[1])
def astar_function(_map:list,start_pos:tuple,des_pos:tuple,n_rol:int,n_col:int):
    min_heap = []
    heappush(min_heap,(h_n(start_pos,des_pos),start_pos))
    visited_node = {}
    direction = [(1,0),(0,1),(-1,0),(0,-1)]
    while min_heap:
        cur_f_x,cur_pos = heappop(min_heap)
        cur_h_n = h_n(cur_pos,des_pos)
        if cur_pos == des_pos:
            path = []
            path.append(cur_pos)
            while path[-1] != start_pos:
                path.append(visited_node[path[-1]])
            path.reverse()
            path.pop(0)
            return path, len(path)
        adj_node = ()
        for i in direction: 
            adj_node = ((cur_pos[0] + i[0]),(cur_pos[1] + i[1]))
            if adj_node[0] not in range (n_rol) or adj_node[1] not in range (n_col):
                continue
            if adj_node not in visited_node and _map[adj_node[0]][adj_node[1]] is not None:
                adj_f_x = (cur_f_x - cur_h_n) + 1 + h_n(adj_node,des_pos)
                heappush(min_heap,(adj_f_x,adj_node))
                visited_node[adj_node] = cur_pos
    return None,None
##########################################################################################
class Action(IntEnum):
	sur = 0
	move = 1
	shoot = 2
	pick = 3
##########################################################################################
class KnowledgeBase:
	def __init__(self,sizeMap):
		self.agentBrainWumpus = Glucose4()
		self.agentBrainPit = Glucose4()
		self.agentFormulaWumpus = []
		self.sizeMap = sizeMap

	# Check specified position is safe or not
	def IsWumpusThere(self,agentPos: tuple):
		return self.agentBrainWumpus.solve([self.ConvertPosToNum(agentPos,1)])
	def IsPitThere(self,agentPos : tuple):
		return self.agentBrainPit.solve([self.ConvertPosToNum(agentPos,1)])
	# Add KB for agent (CNF: w -> a ^ b ^ c ^ d)
	def GotoSchool(self):
		_adjCell = [(1,0),(0,1),(-1,0),(0,-1)]
		for i in range(self.sizeMap[0]):
			for j in range(self.sizeMap[1]):
				_cur_position = self.ConvertPosToNum((i,j),-1)
				for k in _adjCell:
					tmp = (i+k[0],j+k[1])
					if(IsValid(tmp[0],tmp[1],self.sizeMap)):
						self.agentFormulaWumpus.append([_cur_position,self.ConvertPosToNum((tmp[0],tmp[1]),1,1)])
		self.agentBrainWumpus.append_formula(self.agentFormulaWumpus)
		self.agentBrainPit.append_formula(self.agentFormulaWumpus)
	# Add new KB when perceive new sign
	def AddNewKB(self,agentPos : tuple,stench : bool,breeze : bool):
		tmp = 0
		if(stench):
			tmp = self.ConvertPosToNum(agentPos,1,1)
		else:
			tmp = self.ConvertPosToNum(agentPos,-1,1)
		self.agentFormulaWumpus.append([tmp])
		self.agentBrainWumpus.add_clause([tmp])
		if(breeze):
			tmp = self.ConvertPosToNum(agentPos,1,1)
		else:
			tmp = self.ConvertPosToNum(agentPos,-1,1)
		self.agentBrainPit.add_clause([tmp])
	# Remove KB about Stench when shooting
	def RemoveKB(self,_list_pos):
		# Tell KB that wumpus disappear
		tmp = _list_pos.pop(0)
		self.agentFormulaWumpus.append([self.ConvertPosToNum(tmp,-1)])
		# Remove Stench
		for i in range(_list_pos):
			tmp = self.ConvertPosToNum(i,1,1)
			try:
				self.agentFormulaWumpus.remove([tmp])
			except:
				print("Stench is not exists in formula")
			self.agentFormulaWumpus.append([tmp*-1])
		self.agentBrainWumpus.delete()
		self.agentBrainWumpus.append_formula(self.agentFormulaWumpus)
	def ConvertPosToNum(self,pos : tuple,sign = 1,is_stench = 0):
		return int((pos[1]*self.sizeMap[0]+pos[0]+1 + is_stench*self.sizeMap[0]*self.sizeMap[1])*sign)

def IsValid(x,y,_size):
	return x >= 0 and x < _size[0] and y >= 0 and y < _size[1]

##########################################################################################
class AgentController:
	def __init__(self):
		self.map_controller = mapctrl.MapController.GetInstance()
		self.sizeMap = (self.map_controller.width,self.map_controller.height)
		self.agentKB = KnowledgeBase((self.sizeMap[0],self.sizeMap[1]))
		self.score = 0
		self.visit = []
		self.action = []
		self.wumpus_pos = []
	def Probing(self):
		# Current position of agent
		cur_pos = self.map_controller.agentPosition
		stack_safe_move = []
		self.visit.append(cur_pos)
		while True:
			action,safe_move = self.GetAction(cur_pos)
			if(action is not None):
				if(action == Action.pick):
					stack_safe_move.append(cur_pos)
					self.PickGold(cur_pos,self.map_controller.agentMap[cur_pos])
					self.action.append((Action.pick,cur_pos))
					continue
				elif(action == Action.move):
					for ele in safe_move:
						if ele not in stack_safe_move:
							stack_safe_move.append(ele)
			try:
				next_move = stack_safe_move.pop()
			except:
				# That mean over, too much pit and wumpus agent can perceive
				break
			move_path = self.Move(cur_pos,next_move)
			for i in move_path:
				self.action.append((Action.move,i))
			cur_pos = next_move
			self.visit.append(cur_pos)
		# Back to cave


	def GetAction(self,_pos):
		cur_state = self.map_controller.agentMap[_pos]
		# State found Gold
		if(cur_state == int(mapctrl.State.G) or cur_state >= int(mapctrl.State.GB) and cur_state <= int(mapctrl.State.GBS)):
			return (Action.pick,None)
		# Agent sense perceive sign in current position(breeze or stench)
		self.AgentSense(_pos)
		safe_move = []
		_adj_cell = [(0,-1),(-1,0),(0,1),(1,0)]
		for i in _adj_cell:
			tmp = (_pos[0]+i[0],_pos[1]+i[1])
			if tmp in self.visit or not IsValid(tmp[0],tmp[1],self.sizeMap):
				continue
			# Check is Pit there by logic inference
			if(self.agentKB.IsPitThere(tmp)):
				continue
			# Check is Wumpus there by logic inference
			elif(self.agentKB.IsWumpusThere(tmp)):
				self.wumpus_pos.append(tmp)
				continue
			# Safe
			safe_move.append(tmp)
		if(len(safe_move) > 0):
			return (Action.move,safe_move)
		return None,None
		# Is valid, is not visit and is safe
	def AgentSense(self,_pos):
		cur_state = self.map_controller.agentMap[_pos]
		breeze_sense = False
		stench_sense = False
		if(cur_state == int(mapctrl.State.B) or cur_state == int(mapctrl.State.BS)):
			breeze_sense = True
		if(cur_state == int(mapctrl.State.S) or cur_state == int(mapctrl.State.BS)):
			stench_sense = True
		self.agentKB.AddNewKB(_pos,stench_sense,breeze_sense)
	def Move(self,cur_pos,next_pos):
		self.map_controller.AgentMove(next_pos)
		path,cost = astar_function(self.map_controller.agentMap,cur_pos,next_pos,self.sizeMap[0],self.sizeMap[1])
		if(path is not None):
			self.score -= 10*cost
		return path
	def Shoot(self,_pos):
		self.score -= 100
		pass
	def PickGold(self,_pos,state = int(mapctrl.State.G)):
		if(state == int(mapctrl.State.G)):
			self.map_controller.UpdateAgentMap(_pos,0)
		elif(state == int(mapctrl.State.GB)):
			self.map_controller.UpdateAgentMap(_pos,4)
		elif(state == int(mapctrl.State.GS)):
			self.map_controller.UpdateAgentMap(_pos,5)
		else:
			self.map_controller.UpdateAgentMap(_pos,6)
		# Update Score
		self.score += 100
	def AgentPlay(self):
		self.agentKB.GotoSchool()
		self.Probing()
		print(self.action)
		print(self.score)
	def DelAgent(self):
		# Remove KB

		# Remove AgentMap:

		pass
##########################################################################################


agent = AgentController()
agent.AgentPlay()
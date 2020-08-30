##########################
#    Custom Libraries    #
from ..OBJECTS import mapcontroller as mapctrl
##########################
#   Built-in Libraries   #
from queue import heappop, heappush
from enum import IntEnum
from pysat.solvers import Glucose4
import numpy as np


def h_n(start_pos: tuple, des_pos: tuple):
    return abs(start_pos[0] - des_pos[0]) + abs(start_pos[1] - des_pos[1])

def astar_function(_map: list, start_pos: tuple, des_pos: tuple, n_rol: int, n_col: int):
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
    def IsStenchThere(self,pos : tuple):
        return self.agentBrainWumpus.solve([self.ConvertPosToNum(pos,-1,1)]) == False
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
        self.agentFormulaWumpus.append([self.ConvertPosToNum(tmp, -1)])
        self.agentBrainPit.add_clause([self.ConvertPosToNum(tmp, -1)])
        # Remove Stench
        for i in _list_pos:
            tmp = self.ConvertPosToNum(i, 1, 1)
            try:
                self.agentFormulaWumpus.remove([tmp])
            except:
                print("Stench is not exists in formula")
            self.agentFormulaWumpus.append([tmp*-1])
        self.agentBrainWumpus.delete()
        self.agentBrainWumpus = Glucose4()
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
        self.score = 1000
        self.visit = []
        self.action = []
        self.bound_risk = 1
        self.wumpus_pos = []
        self.shoot_pos = None
        self.is_climb_out = False

    def Probing(self):
        # Current position of agent
        cur_pos = self.map_controller.agentPosition
        self.visit.append(cur_pos)
        action = None
        if(not self.is_climb_out and self.shoot_pos is None):
            action,safe_move = self.GetAction(cur_pos)

        if(action is not None):
            if(action == Action.pick):
                self.PickGold(cur_pos,self.map_controller.agentMap[cur_pos])
                return (Action.pick,cur_pos)
            elif(action == Action.move):
                for ele in safe_move:
                    if ele not in self.action:
                        self.action.append(ele)
        next_move = None
        try:
            next_move = self.action.pop()
        except:
            # That mean over, too much pit and wumpus agent can perceive
            # Back to cave or take risk use arrow
            if(self.shoot_pos is not None):
                self.bound_risk -= 1
                return self.Shoot()
            elif(next_move is None and self.bound_risk > 0):
                self.wumpus_pos.sort(reverse=True)
                wumpus = None
                while True:
                    try:
                        wumpus = self.wumpus_pos.pop(0)
                    except:
                        wumpus = None
                        break
                    if(wumpus[0] <= 3 and self.agentKB.IsWumpusThere(wumpus[1])):
                        wumpus = wumpus[1]
                        break
                if(wumpus is None):
                    self.shoot_pos = None
                    self.bound_risk = 0
                    return self.Probing()
                adj_cell = [(0, -1), (-1, 0), (0, 1), (1, 0)]
                for i in adj_cell:
                    tmp = (wumpus[0]+i[0], wumpus[1]+i[1])
                    if (IsValid(tmp[0], tmp[1], self.sizeMap) and self.map_controller.agentMap[tmp[0], tmp[1]] is not None):
                        next_move = (tmp[0], tmp[1])
                        break
                self.shoot_pos = wumpus
                if(next_move == cur_pos):
                    return self.Probing()
            elif(not self.is_climb_out):
                    next_move = self.map_controller.cave
                    self.is_climb_out = True
        if(next_move == None):
            return None,None
        move_path = self.Move(cur_pos,next_move)
        if(move_path != next_move):
            self.action.append(next_move)
        return (Action.move,move_path)


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
            # Check is Wumpus there by logic inference
            if(self.agentKB.IsWumpusThere(tmp)):
                amount_of_stench = 0
                for j in _adj_cell:
                    if(self.agentKB.IsStenchThere((j[0]+tmp[0],j[1]+tmp[1]))):
                        amount_of_stench += 1
                if(amount_of_stench >= 2):
                    flag_append = True
                    for k in range(len(self.wumpus_pos)):
                        if(self.wumpus_pos[k][1] == tmp):
                            self.wumpus_pos[k] = (amount_of_stench,tmp)
                            flag_append = False
                            break
                    if(flag_append):
                        self.wumpus_pos.append((amount_of_stench,tmp))
                continue
            # Check is Pit there by logic inference
            if(self.agentKB.IsPitThere(tmp)):
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
        tmp_map = np.copy(self.map_controller.agentMap)
        tmp_map[next_pos] = 0
        path,cost = astar_function(tmp_map,cur_pos,next_pos,self.sizeMap[0],self.sizeMap[1])
        if(len(path) > 0):
            self.map_controller.AgentMove(path[0])
            return path[0]
        return None
    def Shoot(self):
        state_change = self.map_controller.Shoot(self.shoot_pos)
        if(len(state_change) > 0):
            self.agentKB.RemoveKB(state_change)
        tmp = self.shoot_pos
        for i in self.wumpus_pos:
            if(i[1] == tmp):
                self.wumpus_pos.remove(i)
        self.shoot_pos = None
        return Action.shoot,tmp
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
    def AgentInitialize(self):
        self.agentKB.GotoSchool()
        return self.map_controller.agentPosition,self.score,self.map_controller.agentMap
    def AgentPlay(self):
        action,next_move = self.Probing()
        if(action is None):
            return None,None,None
        if(action == Action.move):
            self.score -= 10
        elif(action == Action.pick):
            self.score += 100
        else:
            self.score -= 100
        return (action,next_move),self.score,self.map_controller.agentMap

    def DelAgent(self):
        # Remove KB
        self.agentKB = None
        # Remove AgentMap:
        self.map_controller = None
##########################################################################################

import random
import os
def RandomMap():
    size_map = 10
    ind = 1
    map = np.full((10,10),None)
    max_randomtext = 10
    while True:
        if(max_randomtext == 0):
            break
        map = np.full((10,10),None)
        max_gold = random.randint(5,15)
        max_pit = random.randint(3,5)
        max_wumpus = random.randint(1,3)
        while True:
            if(max_gold > 0):
                list = []
                gold_pos = (random.randint(0,9),random.randint(0,9))
                if(map[gold_pos] is None):
                    list.append('G')
                    map[gold_pos] = np.array(list)[0]
                    max_gold -= 1
            if(max_pit > 0):
                list = []
                pit_pos = (random.randint(0,9),random.randint(0,9))
                if(map[pit_pos] is None):
                    list.append('P')
                    map[pit_pos] = np.array(list)[0]
                    max_pit -= 1
            if(max_wumpus > 0):
                list = []
                wumpus_pos = (random.randint(0,9),random.randint(0,9))
                if(map[wumpus_pos] is None):
                    list.append('W')
                    map[wumpus_pos] = np.array(list)[0]
                    max_wumpus -= 1
            if(max_wumpus == 0 and max_pit == 0 and max_gold == 0):
                break
        adj = [(1,0),(-1,0),(0,1),(0,-1)]
        for i in range(size_map):
            for j in range(size_map):
                if(map[i,j] is None or map[i,j] == 'G'):
                    lists = ""
                    if(map[i,j] == 'G'):
                        lists += "G"
                    is_Stench = False
                    is_Breeze = False
                    for k in adj:
                        tmp = (i+k[0],j+k[1])
                        if(IsValid(tmp[0],tmp[1],(size_map,size_map))):
                            if(map[tmp[0],tmp[1]] == 'P' and ('B' not in lists)):
                                lists += "B"
                            elif(map[tmp[0],tmp[1]] == 'W' and ('S' not in lists)):
                                lists += "S"
                    if(len(lists) == 0):
                        lists += "-"
                    map[i,j] = np.array(lists)
        agent_pos = None
        while True:
            agent_pos = (random.randint(0,9),random.randint(0,9))
            if(map[agent_pos] == "-"):
                break
        map[agent_pos] = "A"
        path = os.getcwd() + "\SANDBOX\INPUT\map"
        path = path + "-" + str(ind) + ".txt"
        f = open(path,"w")
        f.write("10\n")
        for i in range(len(map)):
            for j in range(len(map[0])):
                ele = str(map[i,j])
                f.write(ele)
                if(j != len(map[0])-1):
                    f.write(".")
            f.write("\n")
        f.close()
        ind += 1
        max_randomtext -= 1

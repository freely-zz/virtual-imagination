import gym
from gym import error, spaces, utils
from gym.utils import seeding
import time
from random import randint
import numpy as np
from .render import Imagination
import math

class DPP1(gym.Env):
    """
    Environment using gym-compatible class structure. Maintains state. Gridsize set on init, goal and agent starting pos set in reset().
    """
    
    def __init__(self):
        """Constructor. In trivial example, number of states = gridsize"""
        self.gridsize = 11
        self.info = "Find ambiguous path."
        #self.actions = [[0,1], [0,-1], [1,0], [-1,0]]   #EWSN
        self.actions = [[0,1], [0,-1], [1,0], [-1,0], [1,1], [-1,-1],[1,-1],[-1,1]]   #plus diags

        self.grid = np.zeros((self.gridsize,self.gridsize))
        midpoint = round(self.gridsize/2)
        self.agent_starting_pos = np.array([5,0])  # top centre
        self.general_pos = [self.gridsize-1,self.gridsize-1]    #bottom right
        self.fake_pos = [0, self.gridsize-1]    #bottom left
        self.memory = 12

        self.img = Imagination(self, self.agent_starting_pos, [self.general_pos,self.fake_pos], self.memory)

        self.realoptcost = self.roughcost(self.agent_starting_pos,self.general_pos)
        self.fakeoptcost = self.roughcost(self.agent_starting_pos,self.fake_pos)
            
    def reset(self):
        #clear grid
        for i in range(self.gridsize):
            for j in range(self.gridsize):
                self.grid[i,j]= -1
        self.agent_pos = self.agent_starting_pos
        self.goal = self.general_pos
        self.grid[self.goal]=100
        self.done = False
        return self.agent_pos
 
    def citycost(self, posA, posB):
        #uses city block heuristic to estimate cost
        return abs(posA[0]-posB[0])+abs(posA[1]-posB[1])    

    def octile(self, posA, posB):
        #uses octile heuristic
        xlen = math.fabs(posA[0] - posB[0])
        ylen = math.fabs(posA[1] - posB[1])
        return max(xlen, ylen) + math.sqrt(2) - 1 * min(xlen, ylen)  

    def roughcost(self, posA, posB):
        #uses variation on octile heuristic - returns actual cost for empty 8-way grid
        xlen = abs(posA[0] - posB[0])
        ylen = abs(posA[1] - posB[1])
        diag = min(xlen, ylen)
        return max(xlen, ylen) + math.sqrt(2) * diag


    def isInGrid(self, loc):
        return loc[0]>=0 and loc[0]<self.gridsize and loc[1]>=0 and loc[1]<self.gridsize
    
    def isAMatch(self, a, b):
        return ((a[0]==b[0]) and (a[1]==b[1]))
            
    def step(self, action_num):
        action = self.actions[action_num]
        proposed_pos = self.agent_pos + action
        
        if (self.isInGrid(proposed_pos)): #check it's a legal position
            self.agent_pos = proposed_pos
         
        obs = (self.agent_pos)
 
       
        if self.isAMatch(self.agent_pos, self.goal):
            reward = 500
            self.done = True
        elif self.isAMatch(self.agent_pos, self.fake_pos):
            reward = -100
        else:
            cdreal = self.roughcost(self.agent_pos,self.goal)-self.realoptcost
            cdfalse = self.roughcost(self.agent_pos, self.fake_pos)-self.fakeoptcost
            if cdreal==cdfalse:
                reward = -1
            else:
                reward = -10

        return obs, reward, self.done, self.info

    def render(self, steps, left="left", right = "right", pause = False):
        self.img.reset()
        self.img.writestatus(left,right)

        for istr in steps:
            time.sleep(0.25)
            self.img.moveAmbo(istr)
            self.img.canvas.update()       

        if pause:   
            self.img.wait()
        


import gym
from gym import error, spaces, utils
from gym.utils import seeding
import time
from random import randint
import numpy as np
from .render import Imagination
import math

class DPP2(gym.Env):
    """
    Environment using gym-compatible class structure. Maintains state. Gridsize set on init, goal and agent starting pos set in reset().
    """
    
    def __init__(self):
        """Constructor. In trivial example, number of states = gridsize"""
        self.gridsize = 11
        self.info = "Find simulating path."
        #self.actions = [[0,1], [0,-1], [1,0], [-1,0]]   #EWSN
        self.actions = [[0,1], [0,-1], [1,0], [-1,0], [1,1], [-1,-1],[1,-1],[-1,1]]   #plus diags

        self.grid = np.zeros((self.gridsize,self.gridsize))
        midpoint = round(self.gridsize/2)
        self.agent_starting_pos = np.array([5,0])  # top centre
        self.general_pos = [self.gridsize-1,self.gridsize-1]    #bottom right
        self.fake_pos = [0, self.gridsize-1]    #bottom left
        self.memory = 24

        self.img = Imagination(self, self.agent_starting_pos, [self.general_pos,self.fake_pos], self.memory)
        self.generateHeatmap()

    def generateHeatmap(self):
        print("Calculating probability heatmap, please wait...")
        gridsize = self.gridsize
        self.realcds = np.zeros((gridsize,gridsize))
        self.fakecds = np.zeros((gridsize,gridsize))
        self.realprobs = np.zeros((gridsize,gridsize))
        self.fakeprobs = np.zeros((gridsize,gridsize))
        realoptcost = self.roughcost(self.agent_starting_pos,self.general_pos)
        print("realoptcost: " + str(realoptcost))
        fakeoptcost = self.roughcost(self.agent_starting_pos,self.fake_pos)
        print("fakeoptcost: " + str(fakeoptcost))

        for i in range(self.gridsize):
            for j in range(self.gridsize):
                print (self.roughcost((i,j), self.general_pos))
                print (self.roughcost((i,j), self.fake_pos))
                real_cd = self.roughcost((i,j), self.general_pos) - realoptcost
                fake_cd = self.roughcost((i,j), self.fake_pos) - fakeoptcost  
                real_l = 1/math.exp(real_cd)
                fake_l = 1/math.exp(fake_cd)
                normconst = real_l + fake_l
                self.realprobs[i,j]= real_l/normconst
                self.fakeprobs[i,j]= 1 - self.realprobs[i,j]
                assert(self.realprobs[i,j]+self.fakeprobs[i,j]==1)
                self.realcds[i,j]= real_cd
                self.fakecds[i,j]= fake_cd
  
            
    def reset(self):
        self.agent_pos = self.agent_starting_pos
        self.goal = self.general_pos
        self.grid[self.goal]=100
        self.done = False
        return self.agent_pos #, self.goal
 
    def cityblock(self, posA, posB):
        #uses city block heuristic to estimate cost
        return abs(posA[0]-posB[0])+abs(posA[1]-posB[1])    

    def roughcost(self, posA, posB):
        #uses variation on octile heuristic - returns actual cost for empty 8-way grid
        xlen = abs(posA[0] - posB[0])
        ylen = abs(posA[1] - posB[1])
        diag = min(xlen, ylen)
        return max(xlen, ylen)-diag + math.sqrt(2) * diag

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
            reward = 100
            self.done = True
        elif self.isAMatch(self.agent_pos, self.fake_pos):
            reward = -100        
        else:
            #get from grids
            simplex = self.agent_pos[0]
            simpley = self.agent_pos[1]
            reward = ((self.fakeprobs[simplex,simpley]-self.realprobs[simplex,simpley])-1)*5
            assert(reward<0)

        return obs, round(reward,2), self.done, self.info

    def render(self, steps, left="left", right = "right", pause = False):
        self.img.reset()
        self.img.writestatus(left,right)

        for istr in steps:
            time.sleep(0.25)
            self.img.moveAmbo(istr)
            self.img.canvas.update()       

        if pause:   
            self.img.wait()
        


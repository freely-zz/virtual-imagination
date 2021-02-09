import gym
from gym import error, spaces, utils
from gym.utils import seeding
import time
from random import randint
import numpy as np
from .render import Imagination

class DPP(gym.Env):
    """
    Environment using gym-compatible class structure. Maintains state. Gridsize set on init, goal and agent starting pos set in reset().
    """
    
    def __init__(self):
        """Constructor. In trivial example, number of states = gridsize"""
        self.gridsize = 10
        self.info = "Find shortest path."
        #self.actions = [[0,1], [0,-1], [1,0], [-1,0]]   #EWSN
        self.actions = [[0,1], [0,-1], [1,0], [-1,0], [1,1], [-1,-1],[1,-1],[-1,1]]   #plus diags
        self.grid = np.zeros((self.gridsize,self.gridsize))
        self.agent_starting_pos = np.array([0,0])  # top left
        self.general_pos = [self.gridsize-1,self.gridsize-1]    #bottom right
        self.memory = 12

        self.img = Imagination(self, self.agent_starting_pos, [self.general_pos], self.memory)

            
    def reset(self):
        """
        """
        #clear grid
        for i in range(self.gridsize):
            for j in range(self.gridsize):
                self.grid[i,j]= -1
        self.agent_pos = self.agent_starting_pos
        self.goal = self.general_pos
        self.grid[self.goal]=100
        self.done = False
        return self.agent_pos
 
    
    def isInGrid(self, loc):
        return loc[0]>=0 and loc[0]<self.gridsize and loc[1]>=0 and loc[1]<self.gridsize
    
    def isAMatch(self, a, b):
        return ((a[0]==b[0]) and (a[1]==b[1]))
            
    def step(self, action_num):
        """
        """       
        action = self.actions[action_num]
        proposed_pos = self.agent_pos + action
        
        if (self.isInGrid(proposed_pos)): #check it's a legal position
            self.agent_pos = proposed_pos
         
        obs = (self.agent_pos)
 
       
        if self.isAMatch(self.agent_pos, self.goal):
            reward = 100
            self.done = True
        else:
            reward = -1

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
        


import gym
from gym import error, spaces, utils
from gym.utils import seeding
import time
from random import randint
import numpy as np
from .render import Imagination
import math

class DPP3(gym.Env):
    """
    Environment using gym-compatible class structure. Maintains state. Gridsize set on init, goal and agent starting pos set in reset().
    """
    
    def __init__(self):
        """Constructor. In trivial example, number of states = gridsize"""
        self.gridsize = 11
        self.info = "Towards extended GR."
        self.actions = [(False,[0,1]), (False,[0,-1]), (False,[1,0]), (False,[-1,0]), (True,[0,1]), (True,[0,-1]), (True,[1,0]), (True,[-1,0])]	#NSEW with and without decoy
        self.grid = np.zeros((self.gridsize,self.gridsize))
        self.agent_starting_pos = np.array([5,0])  # top centre
        self.general_pos = [self.gridsize-1,self.gridsize-1]    #bottom right
        self.fake_pos = [0, self.gridsize-1]    #bottom left
        self.memory = 24

        self.img = Imagination(self, self.agent_starting_pos, [self.general_pos,self.fake_pos], self.memory)
        self.fakesteps = [[4,1],[3,2],[2,3],[1,4],[0,5],[0,6],[0,7],[0,8],[0,9]]	#stub effectively
        self.gen = self.pathgen()

        self.decay,self.epsilon,self.priors, self.defaultmag = 0.8, 0.1, [0.5,0.5], 1.0
        self.obseq=[[self.agent_starting_pos,self.defaultmag]] #list of available observations
        self.counter = 0
        

    def getdecoystep(self):       
        return next(self.gen)
        
    def pathgen(self):     
        for f in self.fakesteps:
            yield f
          

    def reset(self):
        self.gen = self.pathgen()
        #clear grid
        for i in range(self.gridsize):
            for j in range(self.gridsize):
                self.grid[i,j]= -1
        self.agent_pos = self.agent_starting_pos
        self.obseq=[[self.agent_starting_pos,self.defaultmag]]
        self.goal = self.general_pos
        self.grid[self.goal]=100
        self.done = False
        self.nextdecoy=0
        self.counter = 0
        return self.agent_pos
 
    
    def isInGrid(self, loc):
        return loc[0]>=0 and loc[0]<self.gridsize and loc[1]>=0 and loc[1]<self.gridsize
    
    def isAMatch(self, a, b):
        return ((a[0]==b[0]) and (a[1]==b[1]))
            
        
    def step(self, action_num):
        """
        """       
        action = self.actions[action_num]
        proposed_pos = self.agent_pos + action[1]
        if action[0]: #decoy requested
            if self.nextdecoy<len(self.fakesteps):#decoy can be played
                decoypos = self.fakesteps[self.nextdecoy]
                penalty = self.roughcost(decoypos,proposed_pos)
                self.nextdecoy = self.nextdecoy+1
            else:   #decoy requested but not available
                decoypos = None
                penalty = 1000
        else:
            decoypos = None
            penalty = 0
        
        if (self.isInGrid(proposed_pos)): #check it's a legal position
            self.agent_pos = proposed_pos
         
        obs = (self.agent_pos)
        
        if self.isAMatch(self.agent_pos, self.goal):
            reward = 100
            self.done = True
        elif self.isAMatch(self.agent_pos, self.fake_pos):
            reward = -100        
        else:
            self.obseq.append([obs,self.defaultmag])
            realprob, fakeprob = self.extendedGR((self.goal,self.fake_pos), self.obseq, (proposed_pos,decoypos),self.decay,self.epsilon,self.priors)
            reward = ((fakeprob-realprob)-1.01)*5-penalty
            assert(reward<0)

        return obs, reward, self.done, self.info

    def extendedGR(self, goals, obseq, poss_obs, decay, epsilon, priors):
        #assumes step has been received and obs now passed in as poss_obs
        newob = self.most_rel(obseq, poss_obs, goals)#given obs so far and known goals, which ob is most relevant?      
        obseq = self.forget(obseq,decay,epsilon)
        obseq.append(newob)
        start = obseq[0][0]
        current = obseq[len(obseq)-1][0]
        probs = []
        for i in range(len(goals)):
            cd = self.cd(goals[i], start, current)
            probs.append((1/math.exp(cd))*priors[i])
        totlikes = sum(probs)
        for i in range(len(probs)):
            probs[i] = probs[i]/totlikes
        return probs

    def most_rel(self, obseq, poss_obs, goals):
        if poss_obs[1] is None:#max 2 in current implementation
            return [poss_obs[0],self.defaultmag]
        obsonly = [x[0] for x in obseq]
        for eachob in poss_obs:
            toprel,maxrel = 0,0
            for goal in goals:   #max 2 in current implementation
                rel = self.roughcost(obsonly[0],goal)/(self.calccost(obsonly)+self.roughcost(obsonly[len(obsonly)-1],eachob))
                if rel>toprel:
                    toprel = rel
            if toprel > maxrel:
                maxrel = toprel
                bestob = eachob
        return [bestob,self.defaultmag]
 

    def calccost(self, obseq):
        totalcost = 0
        for i in range(len(obseq)-1):
            #assumes consecutive obs - since direct from path
            totalcost += self.conseccost(obseq[i],obseq[i+1])
        return totalcost


    def forget(self, obseq, decay, epsilon):
        #returns revised obslist where members of list are tuples (loc,magnitude)
        indices = []
        for i in range(len(obseq)):
            obseq[i][1] = obseq[i][1]*decay
            if obseq[i][1]<epsilon:
                indices.append(i)
        for each in indices:
            obseq.pop(each)
        return obseq

    def conseccost(self, posA, posB):
        difX = posA[0]-posB[0]
        difY = posA[1]-posB[1]
        if difX == 0 or difY == 0:
            return 1
        else:
            return 1.4 #approx sqrt2

    def cd(self, goal, start, current):
        return self.roughcost(current, goal) - self.roughcost(start, goal)

    def roughcost(self, posA, posB):
        #uses variation on octile heuristic - returns actual cost for empty 8-way grid
        xlen = abs(posA[0] - posB[0])
        ylen = abs(posA[1] - posB[1])
        diag = min(xlen, ylen)
        return max(xlen, ylen)-diag + math.sqrt(2) * diag


    def render(self, steps, left="left", right = "right", pause = False):
        #print(steps)#list of actions
        self.img.reset()
        self.img.writestatus(left,right)

        for istr in steps:
            time.sleep(0.25)
            self.img.moveAmbo(istr)
            self.img.canvas.update()       

        if pause:   
            self.img.wait()
        


from tkinter import *
from tkinter import messagebox  #not routinely exported from module
import time
import random #for testing purposes only


class Imagination(object):
        
    def __init__(self, env, apos, goals, memory):  
        #colours are set here, other parameters from env
        root = Tk()
        root.title("Virtual Imagination")
        fullsize = 500
        self.bgcol = (235,235,235)
        bgcolhex = self.rgbtohex(self.bgcol)
        ambocol = (0,0,235)
        self.ambocolhex = self.rgbtohex(ambocol)
        decoycol = (0,170,0)
        self.decoycolhex = self.rgbtohex(decoycol)

        self.memory = memory
        self.apos = apos    #ambulance starting position
        self.actions = env.actions 
        self.step_r, self.step_g, self.step_b =self.calcfades(ambocol,self.bgcol,self.memory)    
        #print(ambocol, self.step_r, self.step_g, self.step_b)

        self.memsteps = [self.apos]  #path so far

        #build grid
        canvas_frame = Frame(root,height=fullsize, width=fullsize)

        self.gridsize = env.gridsize
        self.canvas = Canvas(canvas_frame, bg=bgcolhex, width=fullsize, height=fullsize, highlightbackground="#476042", highlightthickness=4)
        self.cellsize = int(fullsize/self.gridsize)
        self.offset = int(self.cellsize/2)

        for x in range(self.cellsize,fullsize,self.cellsize):
            self.canvas.create_line(x,0,x,fullsize, fill="#476042")
            self.canvas.create_line(0,x,fullsize, x, fill="#476042")
        
        self.canvas.pack()

        #build canvas
        status_frame = Frame(root, bd=1, relief=SUNKEN, height=20)
        self.right_text = StringVar()
        self.left_text = StringVar()
        Label(status_frame, textvariable=self.left_text).pack(side=LEFT)
        Label(status_frame, textvariable=self.right_text).pack(side=RIGHT)
        Label(status_frame, text = env.info).pack()


        #position actors
        self.setGeneral(goals[0]) 
        try:
            self.setFakes(goals[1:])    #set fakegoal if there is one
        except:
            pass    

        self.traces=[self.setAmbo(self.apos)]    #list of ambo traces, matching to memsteps, so that they can be deleted at reset

        status_frame.pack(side=BOTTOM, fill=X)
        canvas_frame.pack(side=TOP, fill=BOTH, expand=YES)
        self.env = env
     
    def calcfades(self, colB, colA, steps):
        #colors are assumed rgb
        step_r = round((colA[0]-colB[0]) / steps)
        step_g = round((colA[1]-colB[1]) / steps)
        step_b = round((colA[2]-colB[2]) / steps)
        return step_r, step_g, step_b

    def writestatus(self, left,right):
        self.left_text.set(left)
        self.right_text.set(right)

    def wait(self):
        messagebox.showinfo("Best idea so far", "click to close")

    def reset(self):
        for i in range(1,len(self.traces)):
            self.canvas.delete(self.traces[i])
        self.traces=[self.traces[0]]
        self.canvas.itemconfig(self.traces[0],fill=self.ambocolhex)
        self.memsteps = [self.memsteps[0]]
        self.canvas.update()
        self.ambopos = self.apos
        print("update complete")

    def demo(self):
        limit = len(self.actions)-1
        for i in range(0,9):
            actionnum = random.randint(0,limit)
            time.sleep(0.25)
            self.moveAmbo(actionnum)
            self.canvas.update()
        self.reset()

    def moveAmbo(self, action):      
        try:
            direction = self.actions[action][1]
            row = direction[1] #check for dual action
            isDecoy = self.actions[action][0]
            if isDecoy:
                decoystep = self.env.getdecoystep()
            else:
                decoystep = None
        except StopIteration:
            decoystep=None
        except TypeError:
            direction = self.actions[action]
            decoystep=None
        
        pos = tuple(map(sum, zip(self.ambopos, direction)))

        if (self.isInGrid(pos)): #check it's a legal position
            self.forget()
            self.traces.append(self.setAmbo(pos))
            self.memsteps.append(pos)
        if decoystep is not None:
           self.traces.append(self.setDecoy(decoystep))


    #Takes (col,row) of grid and returns canvas coords
    def getCanvasPos(self, rawpos):
        x = rawpos[0]*self.cellsize+self.offset
        y = rawpos[1]*self.cellsize+self.offset
        returncoord = (x,y)
        return returncoord


    def isInGrid(self, loc):
        return loc[0]>=0 and loc[0]<self.gridsize and loc[1]>=0 and loc[1]<self.gridsize

    def setGeneral(self, pos):
        realpos = self.getCanvasPos(pos)       
        self.create_star(realpos, "yellow")

    def setAmbo(self, pos):
        self.ambopos = pos
        realpos = self.getCanvasPos(pos)     
        return self.create_circle(realpos,self.ambocolhex)

    def setDecoy(self, pos):
        self.decoypos = pos
        realpos = self.getCanvasPos(pos)
        return self.create_circle(realpos,self.decoycolhex)

    def setFakes(self, fakelist):
        for pos in fakelist:
            realpos = self.getCanvasPos(pos)
            self.create_star(realpos,"orange")

    def create_circle(self,pos, col): #center coordinates
        r = int(self.offset/2)
        x = pos[0]
        y = pos[1]
        x0 = x - r
        y0 = y - r
        x1 = x + r
        y1 = y + r
        return self.canvas.create_oval(x0, y0, x1, y1, fill = col,outline="")

    def create_star(self, pos, col):
        p = self.offset      #1/2 cellwidth, diameter of star
        t = self.offset/10*3 #proportional to get arm-length of star
        x = pos[0]
        y = pos[1]
        points = []
        for i in (1, -1):
            points.extend((x, y + i*p))
            points.extend((x+i*t, y+i*t))
            points.extend((x+i*p,y))
            points.extend((x+i*t,y-i*t))
        self.canvas.create_polygon(points, fill=col,outline="")

    def clamp(self, x): 
        return max(0, min(x, 255))

    def rgbtohex(self, rgb):  
        #return '#%02x%02x%02x' % (rgb[0], rgb[1], rgb[2])
        return "#{0:02x}{1:02x}{2:02x}".format(self.clamp(rgb[0]), self.clamp(rgb[1]), self.clamp(rgb[2]))

    def hextorgb(self, hexstring):
        hexstring = hexstring.lstrip('#')
        return tuple(int(hexstring[i:i+2], 16) for i in (0, 2, 4))

    def forget(self):
        #print(len(self.traces))
        for i in range(0,len(self.traces)):
            try:
                oldrgb = self.hextorgb(self.canvas.itemcget(self.traces[i],"fill"))

                newr = oldrgb[0]+self.step_r
                if newr > self.bgcol[0]:
                     newr = self.bgcol[0]
                newg = oldrgb[1]+self.step_g
                if newg > self.bgcol[1]:
                    newg = self.bgcol[1]
                newb = oldrgb[2]+self.step_b
                if newb > self.bgcol[2]:   
                    newb = self.bgcol[2]
                newhex = self.rgbtohex((newr,newg,newb))
                self.canvas.itemconfig(self.traces[i],fill=newhex)
            except:
                pass










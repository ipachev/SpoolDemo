from pyprocessing import *
import time
import sys
import select

class Table:
    def __init__(self, tableheight):
        self.height = tableheight

    def draw(self):
        pushMatrix()
        fill(150,100,10)
        rect(0, height-self.height, width, 30)
        popMatrix()


class Spool:
    def __init__(self, x, y, minor, major, mass):
        self.x = x
        self.y = y
        self.initialx = x
        self.initialy = y
        self.angle = 0
        self.minor = minor
        self.major = major
        self.vel = 0
        self.angvel = 0
        self.mass = mass
        self.scalefactor = 4
        self.paused = True
        self.initialstringlength = 6*self.minor*2*PI
        self.stringlength = self.initialstringlength

    def draw(self):
        drawmajor = self.major*self.scalefactor
        drawminor = self.minor*self.scalefactor
        fill(255)
        pushMatrix()
        translate(self.x, self.y)
        rotate(self.angle)
        if self.minor>self.major:
            ellipse(0, 0, drawminor*2, drawminor*2)
            ellipse(0, 0, drawmajor*2, drawmajor*2)
        else:
            ellipse(0, 0, drawmajor*2, drawmajor*2)
            ellipse(0, 0, drawminor*2, drawminor*2)

        ellipse(drawmajor, 0, self.scalefactor, self.scalefactor)
        ellipse(drawminor, 0, self.scalefactor, self.scalefactor)
        ellipse(-1*drawmajor, 0, self.scalefactor, self.scalefactor)
        ellipse(-1*drawminor, 0, self.scalefactor, self.scalefactor)

        popMatrix()
        pushMatrix()
        translate(self.x, self.y+drawminor)
        line(0, 0, self.stringlength*self.scalefactor, 0)
        popMatrix()

    def setMinor(self, minor):
        self.minor = minor

    def setMajor(self, major):
        self.major = major
        self.setOnTable(self.table)

    def setOnTable(self, table):
        self.table = table
        self.y = height-table.height-self.major*self.scalefactor

    def setAngle(self, angle):
        self.angle = angle

    def incrementAngle(self, increment):
        self.angle -= increment
        self.stringlength += increment*self.minor
        
        if self.stringlength < 3:
            self.paused = True

        #print self.stringlength
            
        

    def incrementPosition(self, x, y):
        self.x += x*self.scalefactor
        self.y += y*self.scalefactor

    def resetPosition(self):
        self.x = self.initialx
        self.vel = 0
        self.angvel = 0
        self.stringlength = self.initialstringlength
        self.angle = 0

    def pause(self):
        self.paused = not self.paused


class Button:
    def __init__(self, x, y, text):
        self.x = x
        self.y = y
        self.width = 100
        self.height = 50
        self.text = text

    def draw(self):
        pushMatrix()
        translate(self.x, self.y)
        fill(255)
        rect(0, 0, self.width, self.height)
        fill(0)
        textSize(20)
        text(self.text, 11, 30)
        popMatrix()

    def checkClicked(self, xpos, ypos):
        return xpos > self.x and xpos < self.x + self.width and ypos > self.y and ypos < self.y + self.height


def setup():
    size(1200, 600)
    frameRate(50)
    smooth()
    
    global major
    major = 6.0
    global minor
    minor = 2.0
    global force
    force = 20.0

    global resetButton
    resetButton = Button(width/2 - 50, height-50, "Reset")
    global pauseButton
    pauseButton = Button(width/2 + 100, height-50, "   ||>")
    global spool 
    spool = Spool(width/3, 0, minor, major, 5.0)
    global table
    table = Table(200)

    spool.setOnTable(table)

def draw():
    global force
    global minor
    global major
    global spool
    global table
    background(102)
    spool.draw()
    table.draw()

    resetButton.draw()
    pauseButton.draw()
    #print "Mass %s" % mass
    #print "major %s" % major
    #print "minor %s" % minor
    
    

    if select.select([sys.stdin],[],[],0.0)[0]:
        someinput = raw_input()
        if someinput[0:2] == "p=":
            try:
                force = float(someinput[2:])
                print "set force to %f" % force
            except:
                print "invalid input entered!"
        elif someinput[0:2] == "m=":
            try:
                spool.mass = float(someinput[2:])
                print "set mass to %f" % mass
            except:
                print "invalid input entered!"
        elif someinput[0:2] == "R=":
            try:
                major = float(someinput[2:])
                spool.setMajor(major)
                print "set major to %f" % major
            except:
                print "invalid input entered!"
        elif someinput[0:2] == "r=":
            try:
                minor = float(someinput[2:])
                spool.setMinor(minor)
                print "set minor to %f" % minor
            except:
                print "invalid input entered!"
        elif someinput[0:2] == "rst":
            spool.resetPosition()
    if not spool.paused:
        calc(spool, major, minor, force)


def mousePressed():
    if resetButton.checkClicked(mouse.x, mouse.y):
        spool.resetPosition()
        spool.paused = True
    if pauseButton.checkClicked(mouse.x, mouse.y):
        spool.pause()
    



def calc(spool, major, minor, pull):

    # Calculate Mass Moment of Inertia
    inertia = 1.0/2.0*(2.0*spool.mass/3.0*major**2.0+spool.mass/3.0*minor**2.0)
    #print "inertia is %f" % inertia
    
    
    # Force Friction
    friction = -1.0*pull*(minor+(inertia/(major*spool.mass)))/(major+(inertia/(major*spool.mass)))
    #print "friction is %f" % friction
    
    # Slip Condition
    mew = .19
    mewk = .95*mew
    frictionmax = -spool.mass*9.81*mew
    #print "frictionmax is %f" % frictionmax    
    
    # Test if Spool is slipping
    
    if max(friction, -friction) > max(frictionmax, -frictionmax):
        friction = -1.0*spool.mass*9.81*mewk  
    #print "friction: %f frictionmax %f" % (friction, frictionmax)
    
    # Calculate accelerations
    a = (pull+friction)/spool.mass
    #print "Acceleration is %f" % a
    alpha = (major*friction+minor*pull)/inertia

    #print "alpha is %f" % alpha
    #print 'a is %f' % a

    # Calculate Position increments Using Basic Kinematics
    dt = 1.0/50 # a time step is one frame
    dx = 1.0/2.0*a*dt**2.0+spool.vel*dt
    dtheta = 1.0/2.0*alpha*dt**2.0+spool.angvel*dt

    #print "x moved by: %f, angle moved by %f" % (dx, dtheta)
    
    # Increment Spool Positions
    spool.incrementPosition(dx, 0)
    spool.incrementAngle(dtheta)

    # Increment the Spool's Velocity
    spool.vel += a*dt
    spool.angvel += alpha*dt

if __name__== "__main__":
    run()



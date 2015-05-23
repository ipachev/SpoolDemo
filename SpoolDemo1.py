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
    def __init__(self, x, y, angle, minor, major):
        self.x = x
        self.y = y
        self.initialx = x
        self.initialy = y
        self.angle = angle
        self.minor = minor
        self.major = major

    def draw(self):
        fill(255)
        pushMatrix()
        translate(self.x, self.y)
        rotate(self.angle)
        ellipse(0, 0, self.major*2, self.major*2)
        ellipse(0, 0, self.minor*2, self.minor*2)
        ellipse(self.major, 0, 10, 10)
        ellipse(-1*self.major, 0, 10, 10)

        popMatrix()
        pushMatrix()
        translate(self.x, self.y+self.minor)
        line(0, 0, 500, 0)
        popMatrix()

    def setMinor(self, minor):
        self.minor = minor

    def setMajor(self, major):
        self.major = major
        self.setOnTable(self.table)

    def setOnTable(self, table):
        self.table = table
        self.y = height-table.height-self.major

    def setAngle(self, angle):
        self.angle = angle

    def incrementAngle(self, increment):
        self.angle = self.angle - increment

    def incrementPosition(self, x, y):
        self.x += x
        self.y += y

    def resetPosition(self):
        self.x = self.initialx


class ResetButton:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 100
        self.height = 50

    def draw(self):
        pushMatrix()
        translate(self.x, self.y)
        fill(255)
        rect(0, 0, self.width, self.height)
        fill(0)
        textSize(20)
        text("Reset", 11, 30)
        popMatrix()

    def checkClicked(self, xpos, ypos):
        return xpos > self.x and xpos < self.x + self.width and ypos > self.y and ypos < self.y + self.height


def setup():
    size(1200, 600)
    frameRate(50)
    smooth()
    
    global mass
    mass = 5.0
    global major
    major = 6.0
    global minor
    minor = 2.0
    global force
    force = 2.0
    global scalefactor
    scalefactor = 10

    global resetButton
    resetButton = ResetButton(height-50, width/2 - 50)

    global spool 
    spool = Spool(width/3, 0, 0, scalefactor*minor, scalefactor*major)
    global table
    table = Table(200)

    spool.setOnTable(table)

def draw():
    global force
    global mass
    global minor
    global major
    global spool
    global table
    background(102)
    spool.draw()
    table.draw()

    resetButton.draw()
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
                mass = float(someinput[2:])
                print "set mass to %f" % mass
            except:
                print "invalid input entered!"
        elif someinput[0:2] == "R=":
            try:
                major = float(someinput[2:])
                spool.setMajor(major*scalefactor)
                print "set major to %f" % major
            except:
                print "invalid input entered!"
        elif someinput[0:2] == "r=":
            try:
                minor = float(someinput[2:])
                spool.setMinor(minor*scalefactor)
                print "set minor to %f" % minor
            except:
                print "invalid input entered!"
        elif someinput[0:2] == "rst":
            spool.resetPosition()

    calculated = calc(mass, major, minor, force)
    spool.incrementAngle(calculated[1])
    spool.incrementPosition(calculated[0]*scalefactor, 0)


def mousePressed():
    if resetButton.checkClicked(mouse.x, mouse.y):
        spool.resetPosition()
    



def calc(m, R, r, P):
    # p = input('Input Pulling Force: ')
    #print "Force is %f" % P
    # Calculate Mass Moment of Inertia
    I = 1.0/2.0*(2.0*m/3.0*R**2.0+m/3.0*r**2.0)
    #print "I is %f" % I
    
    # Force Matrix for Plot
    #P = np.arange(0,3.1,.1)
    
    # Force Friction
    #Ff = P - m*(-P*(R*(r-R)/(I-R**2.0)))
    Ff = -1.0*P*(r+(I/(R*m)))/(R+(I/(R*m)))
    #print "Ff is %f" % Ff
    
    # Slip Condition
    mew = .19
    mewk = .95*mew
    Ffmax = -m*9.81*mew
    #print "Ffmax is %f" % Ffmax    
    
    # Test if Spool is slipping
    #for i in range(0,Ff.size):  
    
    if max(Ff, -Ff) > max(Ffmax, -Ffmax):
        Ff = -1.0*m*9.81*mewk  
    #print "Ff: %f Ffmax %f" % (Ff, Ffmax)
    
    # Calculate accelerations
    a = (P+Ff)/m
    #print "Acceleration is %f" % a
    alpha = (R*Ff+r*P)/I

    #print "alpha is %f" % alpha
    #print('a = ', a)

    # Calculate Position increments Using Basic Kinematics
    dt = 1.0 # a time step is one frame
    dx = 1.0/2.0*a*dt**2.0
    dtheta = 1.0/2.0*alpha*dt**2.0

    #print "x moved by: %f, angle moved by %f" % (dx, dtheta)
    return [dx, dtheta]

if __name__== "__main__":
    run()



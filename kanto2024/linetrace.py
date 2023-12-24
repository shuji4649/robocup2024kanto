#!/usr/bin/env pybricks-micropython

from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (Motor, ColorSensor,)
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.robotics import DriveBase
from pybricks.media.ev3dev import SoundFile, ImageFile
from pybricks.iodevices import UARTDevice
import time
P_GAIN=4
I_GAIN=0.001
D_GAIN=0
SPEED=100

class LineTrace():
    
    def __init__(self,a_motor,d_motor,cs_r,cs_l):
        
        self.dif0=0
        self.dif1=0
        self.difSum=0
        self.a_motor,self.d_motor = a_motor,d_motor 
        self.cs_r,self.cs_l = cs_r,cs_l
        self.isRedOnce=False

    def pid_run(self):
        """PIDライントレースをします
        """        
        self.dif1=self.dif0
        self.dif0 = sum(self.cs_r.rgb()) - sum(self.cs_l.rgb())*0.78  # 0.78 は補正値 
        self.difSum += self.dif0
        P = self.dif0*P_GAIN
        I = self.difSum*I_GAIN 
        D = (self.dif0-self.dif1)*D_GAIN 
        speed=SPEED
        self.a_motor.run(speed-(P+I+D))
        self.d_motor.run(speed+(P+I+D))

    def checkRed(self):
        """停止の赤検知

        Returns:
            bool : 赤ならTrueを返します
        """
        if self.cs_r.color() == Color.RED:
            if self.isRedOnce:  
                self.a_motor.stop()
                self.d_motor.stop()
                return True
            else:
                self.isRedOnce=True
                return False
        else:
            self.isRedOnce=False
            return False


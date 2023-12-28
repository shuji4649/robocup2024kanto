#!/usr/bin/env pybricks-micropython

from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (Motor, ColorSensor,)
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.robotics import DriveBase
from pybricks.media.ev3dev import SoundFile, ImageFile
from pybricks.iodevices import UARTDevice
import time
import random
from collections import deque
#高速モード
P_GAIN_fast=12
I_GAIN_fast=0.00
D_GAIN_fast=20
SPEED_fast=350

#標準
P_GAIN=7
I_GAIN=0.1
D_GAIN=12
SPEED=200
#低速モード
P_GAIN_slow=2.2
I_GAIN_slow=0.11
D_GAIN_slow=1.2
SPEED_slow=140

# def initialize():
#     P_GAIN=4
#     I_GAIN=0.001
#     D_GAIN=0
#     SPEED=100
#     a_motor,d_motor = Motor(Port.A),Motor(Port.D)  # 移動用モーター
#     rescue_arm=Motor(Port.C)
#     cs_r,cs_l = ColorSensor(Port.S2),ColorSensor(Port.S3)  # 左のColorSensor
#     dif0=dif1=difSum=0
#     isRedOnce=False

# def pid_run():
#     """PIDライントレースをします
#     """        
#     dif1=dif0
#     dif0 = sum(cs_r.rgb()) - sum(cs_l.rgb())*0.78  # 0.78 は補正値 
#     difSum += dif0
#     P = dif0*P_GAIN
#     I = difSum*I_GAIN 
#     D = (dif0-dif1)*D_GAIN 
#     speed=SPEED
#     a_motor.run(speed-(P+I+D))
#     d_motor.run(speed+(P+I+D))

class LineTrace():
    
    def __init__(self,a_motor,d_motor,cs_r,cs_l,robot):
        
        self.dif0=0
        self.dif1=0
        self.difSuml=deque([0]*20)
        self.difSum=0
        self.a_motor,self.d_motor = a_motor,d_motor 
        self.cs_r,self.cs_l = cs_r,cs_l
        self.isRedOnce=False
        self.robot=robot
        self.ev3=EV3Brick()
        self.straightcount=0
        self.straightcount_s=0
        print(self.a_motor)

    def pid_run(self):
        """PIDライントレースをします
        """        
        self.dif1=self.dif0
        self.dif0 = sum(self.cs_r.rgb()) - sum(self.cs_l.rgb())*1.05  # 0.78 は補正値 

        self.difSuml.append(self.dif0)
        self.difSum+=(self.dif0)
        self.difSum-=self.difSuml.popleft()


        speed_r=1
        ev3=EV3Brick()
        # if abs(self.dif0)<=30: 
        #     if self.straightcount>5:
        #         speed_r=1
        #         if abs(self.dif0)<=20:
        #             if self.straightcount_s>5:
        #                 speed_r=1.4
        #                 ev3.speaker.beep(880)
        #             else: ev3.speaker.beep(440)
        #             self.straightcount_s+=1
        #         else:
        #             self.straightcount_s=0
        #             ev3.speaker.beep(440)
        #     self.straightcount+=1
        # else:
        #     if self.straightcount_s>0:
        #         speed_r=-1
        #     if self.straightcount>0:
        #         speed_r=-0.8
        #     self.straightcount=0
        #     self.straightcount_s=0
        
        print(self.dif0)
        if abs(self.dif0)>=240:
            ev3.speaker.beep(880)
            print(self.dif0)
            self.a_motor.stop()
            self.d_motor.stop()

            self.robot.straight(30)
            f=1 if self.dif0>0 else -1 #左へ曲がるなら1
            for i in range(5,16,5):
                self.robot.turn(5*f)
                if (f==1 and sum(self.cs_r.rgb())<40) or (f==-1 and sum(self.cs_l.rgb())<40):
                    ev3.speaker.beep()

                    self.robot.turn(-i*f)
                    self.robot.stop()
                    return
            else:
                self.robot.turn(-15*f)
                if f==1:

                    while sum(self.cs_l.rgb())>40:
                        hoge=1
                        self.robot.turn(4)
                else:
                    self.robot.drive(100,-20)
                    while sum(self.cs_r.rgb())>40:
                        fuga=1
                        self.robot.turn(-4)
                self.robot.turn(30*f)
                self.robot.stop()
                return

        if abs(self.dif0)<=10:
            self.straightcount_s+=1
            if self.straightcount>3:
                P = self.dif0*P_GAIN_fast
                I = self.difSum*I_GAIN_fast
                D = (self.dif0-self.dif1)*D_GAIN_fast
                speed=SPEED_fast
            else:
                P = self.dif0*P_GAIN
                I = self.difSum*I_GAIN 
                D = (self.dif0-self.dif1)*D_GAIN 
                speed=SPEED
            #print("Hey!!!!!")
        elif abs(self.dif0)<=40:
            self.straightcount_s=0
            P = self.dif0*P_GAIN
            I = self.difSum*I_GAIN 
            D = (self.dif0-self.dif1)*D_GAIN 
            speed=SPEED
            #print("hoi--")

        else:
            self.straightcount_s=0
            P = self.dif0*P_GAIN_slow
            I = self.difSum*I_GAIN_slow
            D = (self.dif0-self.dif1)*D_GAIN_slow
            speed=SPEED_slow
            #print("nyo")
        # P = self.dif0*P_GAIN_fast
        # I = self.difSum*I_GAIN_fast
        # D = (self.dif0-self.dif1)*D_GAIN_fast
        # speed=SPEED_fast

        P = self.dif0*P_GAIN
        I = self.difSum*I_GAIN 
        D = (self.dif0-self.dif1)*D_GAIN 
        speed=SPEED


        k=min(max(P+I+D,-600),600)
        self.a_motor.run(speed-k)
        self.d_motor.run(speed+k)


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


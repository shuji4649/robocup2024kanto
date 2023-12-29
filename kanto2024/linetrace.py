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
import threading

#高速モード
P_GAIN_fast=1.5
I_GAIN_fast=0.00
D_GAIN_fast=0
SPEED_fast=350

#標準
P_GAIN=1.2
I_GAIN=0.0
D_GAIN=0
SPEED=200
#低速モード
P_GAIN_slow=2.2
I_GAIN_slow=0.11
D_GAIN_slow=1.2
SPEED_slow=140


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
        global timer_done
        ev3=EV3Brick()
        # if isGreen(self.cs_r.rgb()):
        #     ev3.speaker.beep()
        #     self.a_motor.stop()
        #     self.d_motor.stop()
        
        #     print("Green")
        #     exit()

        self.dif1=self.dif0
        self.dif0 = sum(self.cs_r.rgb()) - sum(self.cs_l.rgb())*1.05  # 0.78 は補正値 

        self.difSuml.append(self.dif0)
        self.difSum+=(self.dif0)
        self.difSum-=self.difSuml.popleft()


        speed_r=1

        #トの字/直角
        if abs(self.dif0)>=260:
            
            self.a_motor.stop()
            self.d_motor.stop()
            ev3.speaker.beep(880,100)
            f=1 if self.dif0>0 else -1 #左へ曲がるなら1
            self.robot.straight(20)
            #self.robot.turn(-15*f)
            self.robot.stop()


            ev3.speaker.beep()
            time.sleep(0.5)
            timer_set(3.2*40/90)
            black_white_threshould=70
            check_turn_speed=300
            self.a_motor.run(-check_turn_speed*f)
            self.d_motor.run(check_turn_speed*f)
            while True:
                if (f==1 and sum(self.cs_r.rgb())<black_white_threshould) or (f==-1 and sum(self.cs_l.rgb())<black_white_threshould): #トの字だった
                    
                    self.a_motor.stop()
                    self.d_motor.stop()
                    ev3.speaker.beep(523)
                    self.a_motor.run(check_turn_speed*f)
                    self.d_motor.run(-check_turn_speed*f)
                    while (abs(sum(self.cs_l.rgb())-sum(self.cs_r.rgb()))>15):
                        hoge=1

                    break
                if timer_done:
                    timer_done=False
                if (f==1 and sum(self.cs_l.rgb())<black_white_threshould) or (f==-1 and sum(self.cs_r.rgb())<black_white_threshould): #直角だった
                    while abs(sum(self.cs_l.rgb())-sum(self.cs_r.rgb()))>10:
                        hoge=1

                    break
            self.a_motor.stop()
            self.d_motor.stop()
                    
            notgreen_thread=threading.Thread(target=not_see_green_set)
            notgreen_thread.start()
            return


        #直線をまたいだ後は緑検知しない
        if sum(self.cs_l.rgb())<40 and sum(self.cs_r.rgb())<40:
            notgreen_thread=threading.Thread(target=not_see_green_set)
            notgreen_thread.start()



        if abs(self.dif0)<=25:
            self.straightcount_s+=1
            if self.straightcount_s>5:
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
        elif abs(self.dif0)<=60:
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

        # P = self.dif0*P_GAIN
        # I = self.difSum*I_GAIN 
        # D = (self.dif0-self.dif1)*D_GAIN 
        # speed=SPEED

        # P = self.dif0*P_GAIN_slow
        # I = self.difSum*I_GAIN_slow
        # D = (self.dif0-self.dif1)*D_GAIN_slow
        # speed=SPEED_slow




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
    def checkGreen(self):
        if not_see_green: return
        whichGo=0 #1右2左 3引き返す
        if isGreen(self.cs_r.rgb()) or isGreen(self.cs_l.rgb()):
            self.a_motor.stop()
            self.d_motor.stop()
            if isGreen(self.cs_r.rgb()): whichGo+=1
            if isGreen(self.cs_l.rgb()): whichGo+=2
            
        else:
            return
        print("green!!!")
        timer_set(0.5)
        self.a_motor.run(200)
        self.d_motor.run(200)
        found_black=False
        while not timer_done:
            if sum(self.cs_r.rgb())<40 or sum(self.cs_l.rgb())<40: 
                found_black=True
                self.a_motor.stop()
                self.d_motor.stop()
        self.a_motor.stop()
        self.d_motor.stop()
        if found_black:
            turnspeed=300
            ev3=EV3Brick()
            ev3.speaker.beep()
            time.sleep(1)
            if whichGo==3:#Uターン
                self.robot.straight(-50)
                self.robot.turn(140)
                self.robot.stop()
                self.a_motor.run(-turnspeed)
                self.d_motor.run(turnspeed)
                while sum(self.cs_l.rgb())>70:
                    hoge=1
                while abs(sum(self.cs_l.rgb())-sum(self.cs_r.rgb()))>10:
                    hoge=1
                self.a_motor.stop()
                self.d_motor.stop()
            else:
                f=1 if whichGo==2 else -1 #
                # self.robot.drive(60,30*f)
                # time.sleep(1.2)
                # self.robot.stop()
                # time.sleep(1)
                self.robot.straight(26)
                self.robot.turn(40*f)
                self.robot.stop()
                self.a_motor.run(-turnspeed*f)
                self.d_motor.run(turnspeed*f)
                while (f==1 and sum(self.cs_l.rgb())>70) or (f==-1 and sum(self.cs_r.rgb())>70):
                    hoge=1
                self.a_motor.stop()
                self.d_motor.stop()
                self.robot.turn(40*f)
                # while (abs(sum(self.cs_l.rgb())-sum(self.cs_r.rgb())))>15:
                #     hoge=1
                self.robot.straight(10)
                self.robot.stop()
                self.a_motor.stop()
                self.d_motor.stop()
            notgreen_thread=threading.Thread(target=not_see_green_set)
            notgreen_thread.start()
            return
        else:
            return

timer_done=False
timer_num=0
def timer():
    global timer_done
    time.sleep(timer_num)
    timer_done=True
def timer_set(num):
    global timer_done,timer_num
    timer_done=False
    timer_num=num
    timer_thread=threading.Thread(target=timer)
    timer_thread.start()
# 使い方
# timer_set(秒数)
# while not timer_done:
#     制御
    

def isGreen(rgb):
    """r,g,bの値を配列で与えると緑かどうかを判定します。

    Args:
        rgb (list): rgbの値の配列

    Returns:
        bool : 緑ならTrueを返します。
    """    
    r, g, b = rgb
    # print(r,g,b)

    if (g >= 2.5*r and g > 20):
        return True
    else:
        return False

not_see_green=False

def not_see_green_set():
    global not_see_green
    not_see_green=True
    time.sleep(2)
    not_see_green=False
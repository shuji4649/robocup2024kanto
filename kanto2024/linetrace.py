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
import ard_uart

#高速モード
P_GAIN_fast=1.2
I_GAIN_fast=0.01
D_GAIN_fast=10
SPEED_fast=350

#標準
P_GAIN=1.5
I_GAIN=0.012
D_GAIN=12
SPEED=200
#低速モード
P_GAIN_slow=1
I_GAIN_slow=0.014
D_GAIN_slow=15
SPEED_slow=140


class LineTrace():
    
    def __init__(self,a_motor,d_motor,cs_r,cs_l,robot):
        
        self.dif0=0
        self.dif1=0
        self.difSuml=deque([0]*40)
        self.difSum=0
        self.a_motor,self.d_motor = a_motor,d_motor 
        self.cs_r,self.cs_l = cs_r,cs_l
        self.isRedOnce=False
        self.robot=robot
        self.ev3=EV3Brick()
        self.straightcount=0
        self.straightcount_s=0


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

        if ard_uart.line_photo[1] != ard_uart.line_photo[2]:
            
            self.a_motor.stop()
            self.d_motor.stop()
            ev3.speaker.beep(523)
            # f=1 if self.dif0>0 else -1 #左へ曲がるなら1
            f=1 if ard_uart.line_photo[2] else -1 #左へ曲がるなら1
            self.robot.straight(30)
            #self.robot.turn(-15*f)
            self.robot.stop()
            ard_uart.get_sensors()
            check_turn_speed=300
            if ard_uart.line_photo[0]==False: #直角です
                ev3.speaker.beep(440)

                #位置調整。下がって黒を認識してから前に出る
                self.robot.drive(-50,0)
                while ard_uart.line_photo[0]==False:
                    ard_uart.get_sensors()
                    hoge=1
                self.robot.stop()
                self.robot.straight(15)
                self.robot.stop()

                #黒を認識するまで待った後ちょっと前に出て角度調整
                self.a_motor.run(-check_turn_speed*f)
                self.d_motor.run(check_turn_speed*f)
                while  (f==1 and sum(self.cs_l.rgb())>70) or (f==-1 and sum(self.cs_r.rgb())>70):
                    hoge=1
                self.a_motor.stop()
                self.d_motor.stop()
                
                #黒線を挟むまで

                self.a_motor.run(-check_turn_speed*f)
                self.d_motor.run(check_turn_speed*f)
                while  (f==1 and sum(self.cs_l.rgb())>70) or (f==-1 and sum(self.cs_r.rgb())>70):
                    hoge=1
                while (abs(sum(self.cs_l.rgb())-sum(self.cs_r.rgb()))>20 ):
                    hoge=1
            self.a_motor.stop()
            self.d_motor.stop()
                    
            notgreen_thread=threading.Thread(target=not_see_green_set)
            notgreen_thread.start()
            return

        # if sum(self.cs_l.rgb())<40 and sum(self.cs_r.rgb())<40:
        # #直線をまたいだ後は緑検知しない
        if ard_uart.line_photo[1] and ard_uart.line_photo[2]:
            notgreen_thread=threading.Thread(target=not_see_green_set)
            notgreen_thread.start()


        if abs(self.dif0)<=15:
            self.straightcount_s+=1
            if self.straightcount_s>2:
                P = self.dif0*P_GAIN_fast
                I = self.difSum*I_GAIN_fast
                D = (self.dif0-self.dif1)*D_GAIN_fast
                speed=SPEED_fast
            else:
                P = self.dif0*P_GAIN
                I = self.difSum*I_GAIN 
                D = (self.dif0-self.dif1)*D_GAIN 
                speed=SPEED
        elif abs(self.dif0)<=40:
            self.straightcount_s=0
            P = self.dif0*P_GAIN
            I = self.difSum*I_GAIN 
            D = (self.dif0-self.dif1)*D_GAIN 
            speed=SPEED
        else:
            self.straightcount_s=0
            P = self.dif0*P_GAIN_slow
            I = self.difSum*I_GAIN_slow
            D = (self.dif0-self.dif1)*D_GAIN_slow
            speed=SPEED_slow
            #print("nyo")

        debug_speeds=0
        if debug_speeds==1:
            P = self.dif0*P_GAIN_fast
            I = self.difSum*I_GAIN_fast
            D = (self.dif0-self.dif1)*D_GAIN_fast
            speed=SPEED_fast
        if debug_speeds==2:
            P = self.dif0*P_GAIN
            I = self.difSum*I_GAIN 
            D = (self.dif0-self.dif1)*D_GAIN 
            speed=SPEED
        if debug_speeds==3:
            P = self.dif0*P_GAIN_slow
            I = self.difSum*I_GAIN_slow
            D = (self.dif0-self.dif1)*D_GAIN_slow
            speed=SPEED_slow
        
        k=min(max(P+I+D,-speed*3),speed*3)

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
            self.robot.straight(-15)
            self.robot.reset()
            foundRgreen=False
            foundLgreen=False
            self.robot.drive(60,0)
            while self.robot.distance()<=20:
                if isGreen(self.cs_r.rgb()): foundRgreen=True
                if isGreen(self.cs_l.rgb()): foundLgreen=True
            self.robot.stop()
            if foundRgreen: whichGo+=1
            if foundLgreen: whichGo+=2
            print(whichGo)
        else:
            return
        print("green!!!")
        
        timer_set(0.5)
        self.a_motor.run(200)
        self.d_motor.run(200)
        found_black=False
        while not timer_done:
            ard_uart.get_sensors()
            if ard_uart.line_photo[1] or ard_uart.line_photo[2]: 
                found_black=True
                self.a_motor.stop()
                self.d_motor.stop()
        self.a_motor.stop()
        self.d_motor.stop()

        if found_black:
            print("foundGreen!!")
            turnspeed=400
            ev3=EV3Brick()
            ev3.speaker.beep()
            if whichGo==3:#Uターン
                self.robot.drive(-60,60)
                time.sleep(0.3)
                self.robot.straight(-50)
                self.robot.turn(130)
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
                f=1 if whichGo==2 else -1 #左に曲がるなら1
                # self.robot.drive(60,30*f)
                # time.sleep(1.2)
                # self.robot.stop()
                # time.sleep(1)
                self.robot.straight(26)
                self.robot.turn(30*f)
                self.robot.stop()
                self.a_motor.run(-turnspeed*f)
                self.d_motor.run(turnspeed*f)
                while (f==1 and sum(self.cs_l.rgb())>70) or (f==-1 and sum(self.cs_r.rgb())>70):
                    hoge=1
                self.a_motor.stop()
                self.d_motor.stop()
                self.robot.turn(30*f)
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
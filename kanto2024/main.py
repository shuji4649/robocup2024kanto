#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (Motor, ColorSensor,)
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.robotics import DriveBase
from pybricks.media.ev3dev import SoundFile, ImageFile
from pybricks.iodevices import UARTDevice
import time
import sys

from linetrace import LineTrace

import ard_uart

from music import music

from rescue import rescue

import threading
ev3 = EV3Brick()
# モータ・センサ設定

a_motor= Motor(Port.B)
d_motor = Motor(Port.D)  # 移動用モーター
rescue_arm=Motor(Port.C)
cs_r,cs_l = ColorSensor(Port.S2),ColorSensor(Port.S3)  # 左のColorSensor
cs_side=ColorSensor(Port.S4)
a_motor.reset_angle(0)
d_motor.reset_angle(0)

# drivebaseを設定　機体を変えるならここを再設定
robot = DriveBase(d_motor, a_motor, 35, 240)
line=LineTrace(a_motor,d_motor,cs_r,cs_l,robot)
rc=rescue(a_motor,d_motor,rescue_arm,robot,cs_l,cs_r,cs_side)
ev3_music=music()


def main():


    ev3.light.on(Color.ORANGE)
    ev3.speaker.beep()
    #レスキューのアームを上にあげる
    rescue.UpRescueArm()
    robot.stop()
    #rescue.DownRescueArm()
    #rescue.rescuekit_drop()

    while True:
        
        ard_uart.get_sensors()


        if ObjectEscape(): continue 
            
        line.pid_run()
        


        #rescue.PickUpRescueKit()
        
        if line.checkRed():
            robot.stop()
            a_motor.stop()
            d_motor.stop()
            break
        line.checkGreen() 



        continue
        if isEnterRescue():
            ev3.speaker.beep(440)

            robot.straight(300)#前に出る
            robot.stop()
            robot.reset()
            Rescue()
            continue



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

def isEnterRescue():
    """レスキューゾーン入口の銀色テープを検知します。

    Returns:
        bool: 銀色テープを検知したならばTrueを返します。
    """    
    if(cs_r.rgb()[0]>=92 and cs_r.rgb()[1]>=92 and cs_r.rgb()[2]>=92):
        return True
    else:
        return False





speed=100
def check_green():
    """ 緑マーカー検知
    """
    global dif0,dif1,difSum
    # 緑検知

    if isGreen(cs_r.rgb()):
        robot.stop()
        ev3.speaker.beep(440)


        # 少し前に出る
        #robot.straight(3*chosei)
        robot.drive(speed, 0)
        time.sleep(0.04)

        if isGreen(cs_l.rgb()):  # 左も緑か？
            # 下がって黒か確認
            #robot.straight(-20*chosei)
            robot.turn(5)
            robot.drive(-speed, 0)
            time.sleep(0.2)
            if cs_r.color() == Color.BLACK:
                # 黒なら無視
                #robot.straight(40*chosei)
                robot.drive(speed, 0)
                time.sleep(1.1)

            else:  # 引き返す
                robot.turn(180)

        else:
            # 少しバック
            #robot.straight(-20*chosei)
            robot.drive(-speed, 0)
            time.sleep(0.4)
            robot.stop()

            if cs_r.color() == Color.BLACK:
                # 黒なら無視
                robot.turn(5)
                #robot.straight(40*chosei)
                robot.drive(speed, 0)
                time.sleep(1.1)


            else:
                # 白なら右に曲がる
                ev3.speaker.beep(391)
                robot.stop()
                #robot.straight(40*chosei)
                robot.drive(speed, 0)
                time.sleep(1.0)
                robot.turn(-75)
                #robot.straight(25*chosei)
                robot.drive(speed, 0)
                time.sleep(0.2)
        dif0 = 0
        dif1 = 0
        difSum = 0
        robot.stop()

    if isGreen(cs_l.rgb()):
        robot.stop()
        ev3.speaker.beep(440)

        # 少し前に出る
        #robot.straight(5*chosei)
        robot.drive(speed, 0)
        time.sleep(0.04)

        if isGreen(cs_r.rgb()):  # 左も緑か？
            # 下がって黒か確認
            #robot.straight(-20*chosei)
            robot.drive(-speed, 0)
            time.sleep(0.2)
            if cs_l.color() == Color.BLACK:
                # 黒なら無視
                #robot.straight(40*chosei)
                robot.drive(speed, 0)
                time.sleep(1.1)
            else:  # 引き返す
                robot.turn(180)
        else:
            # 少しバック
            #robot.straight(-20*chosei)
            robot.drive(-speed, 0)
            time.sleep(0.3)

            if cs_l.color() == Color.BLACK:
                # 黒なら無視
                robot.turn(-25)
                #robot.straight(40*chosei)
                robot.drive(speed, 0)
                time.sleep(1.1)


            else:
                # 白なら右に曲がる

                #robot.straight(40*chosei)
                robot.drive(speed, 0)
                time.sleep(1.0)
                robot.turn(75)
                #robot.straight(40*chosei)
                robot.drive(speed, 0)
                time.sleep(0.8)


        
        dif0 = 0
        dif1 = 0
        difSum = 0

isObject_R=False
def ObjectEscape():
    global isObject_R
    if isObject_R:  # 障害物右回避中の時
        if (cs_r.color() == Color.BLACK or cs_l.color() == Color.BLACK):
            a_motor.stop()
            d_motor.stop()
            robot.stop()
            ev3.speaker.beep(523)
            time.sleep(0.2)
            robot.straight(-80) # 後ろへ

            robot.stop()
            robot.turn(-20)
            robot.drive(100,0)
            while sum(cs_l.rgb())>100 and sum(cs_r.rgb())>100:
                hoge=1
            robot.stop()
            a_motor.run(200)
            d_motor.run(-200)
            while sum(cs_l.rgb())<100 or sum(cs_r.rgb())<100 or abs(sum(cs_l.rgb())-sum(cs_r.rgb()))>15:
                hoge=1
            a_motor.stop()
            d_motor.stop()
            
            
            ev3.speaker.beep(240)
            isObject_R = False
        else:
            if ard_uart.touch_sensor[1]:
                a_motor.run(200)
                d_motor.run(200)
            else:
                a_motor.run(-300)
                d_motor.run(300)
        return True

    if ard_uart.touch_sensor[0] or ard_uart.touch_sensor[1]:
        ev3.speaker.beep()
        robot.straight(-50)  # 下がって
        robot.turn(-60)  # 右折
        robot.straight(60) 
        robot.stop()
        isObject_R=True
        return True



def UpRescueArm():
    """ アームを上げる
    """
    rescue_arm.run(1000)
    time.sleep(1.5)
    #rescue_arm.stop()

def DownRescueArm():
    """ アームを下げる
    """
    rescue_arm.run(-1000)
    time.sleep(1.5)
    rescue_arm.stop()




def exitCheck():
    ev3=EV3Brick()
    while True:
        if ev3.buttons.pressed():
            robot.stop()
            a_motor.stop()
            d_motor.stop()
            ev3.speaker.beep()
            sys.exit()


if __name__=="__main__":
    print("hogee")
    main_thread=threading.Thread(target=main)
    main_thread.daemon=True
    main_thread.start()
    exitCheck()

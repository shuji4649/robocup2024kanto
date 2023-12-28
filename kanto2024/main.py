#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (Motor, ColorSensor,)
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.robotics import DriveBase
from pybricks.media.ev3dev import SoundFile, ImageFile
from pybricks.iodevices import UARTDevice
import time
from linetrace import LineTrace
import ard_uart
from music import music
from rescue import rescue

ev3 = EV3Brick()
# モータ・センサ設定
a_motor,d_motor = Motor(Port.A),Motor(Port.D)  # 移動用モーター
rescue_arm=Motor(Port.C)
cs_r,cs_l = ColorSensor(Port.S2),ColorSensor(Port.S3)  # 左のColorSensor
a_motor.reset_angle(0)
d_motor.reset_angle(0)

# drivebaseを設定　機体を変えるならここを再設定
robot = DriveBase(d_motor, a_motor, 35, 240)
line=LineTrace(a_motor,d_motor,cs_r,cs_l,robot)
rc=rescue(a_motor,d_motor,rescue_arm,robot)
ev3_music=music()
print(a_motor)


def main():


    ev3.speaker.beep()
    #レスキューのアームを上にあげる
    robot.stop()

    while True:

        #ard_uart.get_sensors()

        # if ard_uart.photo_ball:
        #     ard_uart.OpenArms(2)
        #     time.sleep(0.4)
        #     robot.stop()
        #     UpRescueArm()
        #     ard_uart.OpenArms(4)
        #     time.sleep(0.4)
        #     ard_uart.OpenArms(1)
        #     time.sleep(0.6)
        #     DownRescueArm()
        #     robot.drive(100,0)


        line.pid_run()

        # rescue.PickUpRescueKit()
        
        if line.checkRed():
            robot.stop()
            break
        check_green() 
        continue
        if ObjectEscape(): continue 

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
    if isObject_R:  # 障害物右回避中の時
        if (cs_r.color() == Color.BLACK or cs_l.color() == Color.BLACK):
            robot.stop()
            ev3.speaker.beep(523)
            time.sleep(0.2)
            robot.straight(-150,0) # 後ろへ
            time.sleep(1.6)
            robot.stop()
            robot.turn(-20)

            time.sleep(0.5)
            robot.stop()

            a_motor.run(400)
            d_motor.run(180)
            time.sleep(2.8)
            a_motor.stop()
            d_motor.stop()
            
            
            ev3.speaker.beep(240)
            isObject_R = False
        else:
            if ard_uart.touch_sensor[1]:
                robot.drive(speed, 0)
            else:
                robot.drive(speed,60)
        return True

    if ard_uart.touch_sensor[0] or ard_uart.touch_sensor[1]:
        ev3.speaker.beep()
        robot.straight(-20)  # 下がって
        robot.turn(-70)  # 右折
        robot.straight(20) 
        isObject_R=True
        return True

#障害物回避
isObject_first_L = isObject_first_R=False #左右それぞれの回避のはじめにぶつかるまで
isObject_L = isObject_R = False  # どっち側で障害物回避中？
def ObjectEscape():
    global touch_L,touch_R,isObject_first_L,isObject_first_R,isObject_L,isObject_R
    if isObject_first_R:
        if touch_L:
            ev3.speaker.beep(587)
            isObject_R=True
            isObject_first_R=False
        else:
            robot.drive(speed,0)
            time.sleep(0.1)
            robot.drive(speed,60)
            time.sleep(0.2)
        return True
    # if isObject_first_L:
    #     if touch_R:
    #         ev3.speaker.beep(587)
    #         isObject_L=True
    #         isObject_first_L=False
    #     else:
    #         robot.drive(speed,0)
    #         time.sleep(0.1)
    #         robot.drive(speed,-60)
    #         time.sleep(0.2)
    #     return True 
  

    if isObject_R:  # 障害物右回避中の時
        if (cs_r.color() == Color.BLACK or cs_l.color() == Color.BLACK):
            robot.stop()
            ev3.speaker.beep(523)
            time.sleep(0.2)
            robot.drive(-speed, 0)  # 後ろへ
            time.sleep(1.6)
            robot.stop()
            robot.turn(-20)

            time.sleep(0.5)
            robot.stop()

            a_motor.run(400)
            d_motor.run(180)
            time.sleep(2.8)
            a_motor.stop()
            d_motor.stop()
            

            #robot.turn(-90)  # 右に曲がる
            ev3.speaker.beep(240)
            isObject_R = False
        else:
            if touch_L == 1:
                robot.drive(speed, 0)
            else:
                robot.drive(speed,60)
        return True
    return False
    # if isObject_L:  # 障害物右回避中の時
    #     if (cs_r.color() == Color.BLACK or cs_l.color() == Color.BLACK):
    #         robot.stop()
    #         ev3.speaker.beep(523)
    #         time.sleep(0.2)
    #         robot.drive(-speed, 0)  # 後ろへ
    #         time.sleep(1.6)
    #         robot.stop()
    #         time.sleep(0.5)

    #         a_motor.run(120)
    #         d_motor.run(400)
    #         time.sleep(2.5)
    #         a_motor.stop()
    #         d_motor.stop()
            

    #         #robot.turn(-90)  # 右に曲がる
    #         ev3.speaker.beep(240)
    #         isObject_L = False
    #     else:
    #         if touch_R == 1:
    #             robot.drive(speed, 0)
    #         else:
    #             robot.drive(speed,-60)
    #     return True

    #今は必ず右回避
    if touch_L or touch_R:  # 左タッチセンサーが反応したとき
        ev3.speaker.beep()
        robot.drive(-speed, 0)  # 下がって
        time.sleep(0.1)
        robot.turn(-70)  # 右折
        robot.drive(speed,0)
        time.sleep(0.4)

        isObject_first_R = True  # 障害物右回避
        return True
    # if touch_R:  # 右タッチセンサーが反応したとき
    #     ev3.speaker.beep()
    #     robot.drive(-speed, 0)  # 下がって
    #     time.sleep(0.1)
    #     robot.turn(90)  # 左折
    #     robot.drive(speed, 0) 
    #     time.sleep(0.4)
    #     isObject_first_L = True  # 障害物左回避
    #     continue
    return False



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






if __name__=="__main__":
    main()
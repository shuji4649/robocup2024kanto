#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (Motor, ColorSensor,)
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.robotics import DriveBase
from pybricks.media.ev3dev import SoundFile, ImageFile
from pybricks.iodevices import UARTDevice
import time
import ard_uart

class rescue:
    """レスキュー系のクラス
        モータ類はクラス変数
    Returns:
        _type_: _description_
    """    
    rescue_arm = Motor(Port.C)
    a_motor=Motor(Port.A)
    d_motor=Motor(Port.D)

    def __init__(self,a_motor,d_motor,rescue_arm,robot) :
        """rescueクラスの初期化

        Args:
            a_motor (Motor): _description_
            d_motor (Motor): _description_
            rescue_arm (Motor): _description_
            robot (robot): _description_
        """
        rescue.a_motor,rescue.d_motor,rescue.rescue_arm =a_motor,d_motor,rescue_arm
        rescue.robot=robot


        
    @classmethod
    def UpRescueArm():
        """ アームを上げる
        """
        rescue.rescue_arm.run(1000)
        time.sleep(1.5)
        rescue.rescue_arm.stop()
    @classmethod
    def DownRescueArm():
        """ アームを下げる
        """
        rescue.rescue_arm.run(-1000)
        time.sleep(1.5)
        rescue.rescue_arm.stop()

    #レスキューキットを回収
    def PickUpRescueKit():
        if ard_uart.ard_sensors.rescue_photo:
            robot.straight(-30)
            rescue.DownRescueArm()
            robot.drive(0,speed)
            while True:
                get_sensors()
                if photo_ball:
                    break
            robot.stop()
            OpenArms(2)
            rescue.UpRescueArm()
            OpenArms(3)
            

        


    def turnHinanjo(isLeftTurn):
        if isLeftTurn:
            robot.turn(45)
            robot.straight(150)
            if(cs_rescue.color()==Color.GREEN):
                robot.turn(90)
                robot.drive(-speed,0)
                time.sleep(0.4)
                robot.drive(speed,0)
                time.sleep(0.4)
                robot.turn(-90)
                return True
            robot.straight(150)
            robot.turn(45)
            return False
        else:
            robot.turn(-45)
            robot.straight(150)
            robot.turn(-45)   



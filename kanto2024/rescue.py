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
    # rescue_arm = Motor(Port.C)
    # d_motor=Motor(Port.D)
    # a_motor=Motor(Port.A)


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
    def UpRescueArm(cls):
        """ アームを上げる
        """
        rescue.rescue_arm.run(1600)
        time.sleep(1.5)
        #rescue.rescue_arm.stop()
    @classmethod
    def DownRescueArm(cls):
        """ アームを下げる
        """
        rescue.rescue_arm.run(-500)
        time.sleep(2.0)
        rescue.rescue_arm.stop()

    #レスキューキットを回収
    @classmethod
    def PickUpRescueKit(cls):
        if ard_uart.rescue_photo:
            ard_uart.get_sensors()
            rescue.robot.straight(-130)
            rescue.DownRescueArm()
            rescue.robot.straight(30)
            ard_uart.OpenArms(2)
            time.sleep(0.4)

            rescue.UpRescueArm()
            ard_uart.OpenArms(3)
            time.sleep(0.4)
            ard_uart.OpenArms(1)
            rescue.robot.straight(100)
            rescue.robot.stop()

        


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



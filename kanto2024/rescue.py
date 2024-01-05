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


    def __init__(self,a_motor,d_motor,rescue_arm,robot,cs_l,cs_r,cs_side) :
        """rescueクラスの初期化

        Args:
            a_motor (Motor): _description_
            d_motor (Motor): _description_
            rescue_arm (Motor): _description_
            robot (robot): _description_
        """
        rescue.a_motor,rescue.d_motor,rescue.rescue_arm =a_motor,d_motor,rescue_arm
        rescue.robot=robot
        rescue.cs_l,rescue.cs_r=cs_l,cs_r
        rescue.cs_side=cs_side
        rescue.LiveBall=True
        rescue.DeadBall=False


    @classmethod
    def rescuekit_drop(cls):
        """レスキューキットを落とすための周回
        """
        rescue.robot.drive(160,0)

        while True:
            ard_uart.get_sensors()
            if rescue.isEnterRescue() or rescue.isExitRescue():
                rescue.UpRescueArm()
                rescue.robot.straight(-70)
                rescue.robot.turn(90)
                rescue.robot.drive(160,0)
                continue
            if ard_uart.touch_sensor[3]:
                rescue.robot.straight(20)
                ard_uart.get_sensors()
                if ard_uart.touch_sensor[4]: #壁でした
                    rescue.robot.straight(-30)
                    rescue.UpRescueArm()
                    rescue.robot.turn(90)
                    rescue.robot.drive(160,0)
                else:
                    rescue.robot.straight(-30)
                    rescue.TurnHinanjo()
                



    @classmethod
    def rescue_search(cls):
        turn_dir=-1 #次に左折するなら-1,次に右折するなら1
        rescue.DownRescueArm()
        while True:
            rescue.robot.drive(160,0)
            ard_uart.get_sensors()
            while not (ard_uart.touch_sensor[2] or ard_uart.touch_sensor[3]):
                ard_uart.get_sensors()
                rescue.PickUpRescueBalls()
            time.sleep(0.2)
            if ard_uart.touch_sensor[3]==False:
                print("Only Right")
                exit()
            if ard_uart.touch_sensor[2]==False:
                print("Only Left")
                exit()
            ard_uart.get_sensors()
            rescue.PickUpRescueBalls()
            rescue.robot.straight(-50)
            rescue.UpRescueArm()
            rescue.robot.straight(140)
            rescue.robot.turn(-90*turn_dir)
            rescue.robot.straight(200)
            rescue.robot.turn(-90*turn_dir)

            #rescue.robot.turn(180)
            rescue.robot.straight(100)
            rescue.robot.straight(-250)
            rescue.DownRescueArm()
            turn_dir*=-1




        
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
        rescue.rescue_arm.run(-400)
        time.sleep(1.5)
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
    @classmethod
    def PickUpRescueBalls(cls):
        if ard_uart.photo_ball:
            ard_uart.OpenArms(2)
            
            rescue.robot.stop()
            time.sleep(0.5)
            rescue.UpRescueArm()
            ard_uart.get_sensors()
            if ard_uart.check_ball:
                ard_uart.OpenArms(3)
            else:
                ard_uart.OpenArms(4)
            time.sleep(0.5)
            ard_uart.OpenArms(1)
            time.sleep(0.5)
            rescue.robot.straight(-50)
            rescue.DownRescueArm()
            rescue.robot.drive(100,0)
    @classmethod
    def TurnHinanjo(cls,isRightTurn=-1):
        rescue.a_motor.run(250+150*isRightTurn)
        rescue.d_motor.run(250-150*isRightTurn)
        time.sleep(2)
        rescue.robot.straight(50)


        
        rescue.robot.turn(-90*isRightTurn)
        rescue.robot.straight(-50)
        rescue.robot.straight(20)
        hinanjocolor=rescue.cs_side.color()#緑？赤？
        if hinanjocolor==Color.GREEN:
            ard_uart.OpenArms(5)
            rescue.LiveBall=False
        else:
            ard_uart.OpenArms(6)
            rescue.DeadBall=False
        time.sleep(2)
        ard_uart.OpenArms(7)
        rescue.robot.straight(30)
        rescue.robot.turn(90*isRightTurn)

        rescue.a_motor.run(250+150*isRightTurn)
        rescue.d_motor.run(250-150*isRightTurn)
        time.sleep(2)
        rescue.robot.straight(50)



    @classmethod
    def isEnterRescue():
        """レスキューゾーン入口の銀色テープを検知します。

        Returns:
            bool: 銀色テープを検知したならばTrueを返します。
        """    
        return (sum(rescue.cs_r.rgb())>=280)
    @classmethod
    def isExitRescue():
        """レスキューゾーン出口の黒色テープを検知します。

        Returns:
            bool: 黒色テープを検知したならばTrueを返します。
        """    
        return (sum(rescue.cs_r.rgb())<=40)
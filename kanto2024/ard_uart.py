#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (Motor, ColorSensor,)
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.robotics import DriveBase
from pybricks.media.ev3dev import SoundFile, ImageFile
from pybricks.iodevices import UARTDevice
import time

#Arduinoをつかさどるモジュール。
#値を更新するときはard_uart.get_sensors()
#値はこの下の変数を参照。

touch_sensor=[False,False,False,False]  # 右、左、レスキュー用右、左
line_photo=[False,False,False] #ライントレース用のフォトリフレクタ、中央、右、左　白ならFalse、黒ならTrue
line_photo_threshoulds=[240,240,240] #フォトリフレクタの黒か白かの閾値
rescue_photo = False #レスキューキット用のフォトリフレクタ　反応すればTrue
photo_rescue_threshould=235
ultrasonic = 0  # 超音波センサー右 cm
photo_ball = False #アームの中に物体があるか検知　あればTrue
check_ball = False #アームの導電性を確認、電気が流れればTrue
isEnterRescue_byPoto=False
isEnterrescue_photo_threshould=100
ard = UARTDevice(Port.S1, baudrate=9600)

def get_sensors():
    global touch_sensor,line_photo,rescue_photo,ultrasonic,photo_ball,check_ball,ard,isEnterRescue_byPoto
    """ Arduinoからセンサーの値を取得し,値に格納します
    """
    ard.clear()


    date = ard.read(1)

    while date != b'\xff':
        date = ard.read(1)

    touch = get_int_date()  # タッチセンサーの通信データ
    for i in range(4):  touch_sensor[i]=(touch >> i) & 1 #ビットで割り当てていくぅ

    for i in range(3):
        date_int=get_int_date()

        # print(i,date_int)
        line_photo[i]=( date_int > line_photo_threshoulds[i] )
        if date_int <isEnterrescue_photo_threshould:
            isEnterRescue_byPoto=True


    # # フォトリフレクタ・レスキュー

    date_int=get_int_date()
    rescue_photo=( date_int < photo_rescue_threshould )
    print(date_int)

    # 超音波センサ
    #ultrasonic = get_int_date()  # 超音波センサー右の通信データ
    

    # ボール検知フォトトランジスタ
    photo_ball_threshould=240 #ボール検知の閾値
    date_int=get_int_date()


    photo_ball=(date_int>photo_ball_threshould)

    date_int=get_int_date()  # ボール判別導電性センサ
    check_ball=(date_int==1)

    #date10 = ard.read(1)  # I2Cカラーセンサ
    ard.clear()

def get_int_date():
    """arduinoから受け取った値を数字で返す
    Returns:
        int: arduinoから受け取ったデータ
    """
    return int.from_bytes(ard.read(1),"big")

#アーム開閉
def OpenArms(num):
    """アームを開閉します。
        Arduinoに指示を送ります。
        開閉の時間分待つ分までここに含まれます。
    Args:
        num (int): 指示コード 1:両方開く 2:両方閉じる 3: 右だけ開く 4:左だけ閉める 5:後ろ右だけ開ける 6:後ろ左だけ開ける 7:後ろ閉める 8:ライントレースモード 9:レスキューモード
    """    
    ard.write(num.to_bytes(1, "big"))
    time.sleep(0.4)


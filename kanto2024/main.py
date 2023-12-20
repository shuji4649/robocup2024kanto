#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor,
                                 InfraredSensor, UltrasonicSensor, GyroSensor)
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait, StopWatch, DataLog
from pybricks.robotics import DriveBase
from pybricks.media.ev3dev import SoundFile, ImageFile
from pybricks.iodevices import UARTDevice
import time




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


def PlayMusic(s,haku=500):
    """音楽を流します。

    Args:
        s (_type_): doremifasolatidoのテキストで流す音声
        haku (int, optional): 速さ（一つの音符にかけるミリ秒）. Defaults to 500.
    """    
    scores={"do":261,"re":293,"mi":329,"fa":349,"so":391,"la":440,"ti":493}
    l=len(s)//2
    for i in range(l):
        new_s=s[l*2:l*(2+1)]
        ev3.speaker.beep(scores[new_s],haku)


ev3 = EV3Brick()
ev3.speaker.beep()

ev3.speaker.set_volume(100)


# モータ・センサ設定
a_motor,d_motor = Motor(Port.A),Motor(Port.D)  # 移動用モーター
rescue_arm = Motor(Port.C) #アーム
cs_r,cs_l = ColorSensor(Port.S2),ColorSensor(Port.S3)  # 左のColorSensor
a_motor.reset_angle(0)
d_motor.reset_angle(0)
# drivebaseを設定　機体を変えるならここを再設定
robot = DriveBase(d_motor, a_motor, 35, 240)



# arduinoをUARTデバイスとして設定
ard = UARTDevice(Port.S1, baudrate=9600)
# arduinoからくるデータの格納場所
touch_sensor=[False,False,False,False]  # 右、左、レスキュー用右、左
line_photo=[False,False,False] #ライントレース用のフォトリフレクタ、中央、右、左　白ならFalse、黒ならTrue
rescue_photo = False #レスキューキット用のフォトリフレクタ　反応すればTrue
ultrasonic = 0  # 赤外線センサー右 cm
photo_ball = False #アームの中に物体があるか検知　あればTrue
check_ball = False #アームの導電性を確認、電気が流れればTrue


def get_sensors():
    """ Arduinoからセンサーの値を取得します
    """
    global touch_sensor,line_photo,rescue_photo,ultrasonic,photo_ball,check_ball

    ard.clear()
    date = ard.read(1)
    while date != b'\xff':
        date = ard.read(1)

    touch = int.from_bytes(ard.read(1), "big")  # タッチセンサーの通信データ
    for i in range(4):  touch_sensor[i]=(touch >> i) & 1 #ビットで割り当てていくぅ

    photo_threshould=250 #フォトリフレクタの黒か白かの閾値
    for i in range(3):
        date_int=int.from_bytes(ard.read(1) ,"big")
        line_photo[i]=( date_int > photo_threshould )

    # フォトリフレクタ・レスキュー
    date_int=int.from_bytes(ard.read(1) ,"big")
    rescue_photo=( date_int > photo_threshould )

    # 超音波センサ
    ultrasonic = int.from_bytes(ard.read(1), "big")  # 超音波センサー右の通信データ

    # ボール検知フォトトランジスタ
    photo_ball_threshould=200 #ボール検知の閾値
    date_int=int.from_bytes(ard.read(1),"big")
    photo_ball=(date_int<photo_ball_threshould)

    date_int=int.from_bytes(ard.read(1),"big")  # ボール判別導電性センサ
    check_ball=(date_int==1)
    
    date10 = ard.read(1)  # I2Cカラーセンサ
    ard.clear()






# PID用の変数
P = I = D = 0
dif0 = dif1 = difSum = 0
speed = 350
def pid_run():
    """ PID制御でライントレースをします
    """
    global dif0,dif1,difSum,P,I,D
    # PID制御
    dif1 = dif0
    dif0 = (cs_r.rgb()[0]+cs_r.rgb()[1]+cs_r.rgb()[2]) - \
        (cs_l.rgb()[0]+cs_l.rgb()[1]+cs_l.rgb()[2])*0.78  # 0.78 は補正値 

    difSum += dif0


    P = dif0*0.4
    I = difSum*0.001 # 0.007
    D = (dif0-dif1)*0 #0.002 #21
    #直線では速く
    # if (abs(dif0) > 30):
    #     runspeed = speed/3
    # else:
    runspeed = speed
    a_motor.run(speed-5*(P+I+D))
    d_motor.run(speed+5*(P+I+D))
    #robot.drive(runspeed, (P+I+D))


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
                robot.turn(-80)
                #robot.straight(25*chosei)
                robot.drive(speed, 0)
                time.sleep(0.8)
        dif0 = 0
        dif1 = 0
        difSum = 0

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
                ev3.speaker.beep(391)
                robot.stop()
                turnLeft()
                # #robot.straight(40*chosei)
                # robot.drive(speed, 0)
                # time.sleep(1.0)
                # robot.turn(80)
                # #robot.straight(40*chosei)
                # robot.drive(speed, 0)
                # time.sleep(0.8)
        dif0 = 0
        dif1 = 0
        difSum = 0


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



#赤検知
isRedOnce=False
def checkRed():
    """停止の赤検知

    Returns:
        bool : 赤ならTrueを返します
    """
    global isRedOnce
    if cs_r.color() == Color.RED:
        if isRedOnce:
            robot.stop()
            return True
        else:
            isRedOnce=True
            return False
    else:
        isRedOnce=False
        return False


def UpRescueArm():
    """ アームを上げる
    """
    rescue_arm.run(1000)
    time.sleep(1.5)
    rescue_arm.stop()
def DownRescueArm():
    """ アームを下げる
    """
    rescue_arm.run(-1000)
    time.sleep(1.5)
    rescue_arm.stop()

#アーム開閉 0:閉じる 1:右を開ける 2: 左を開ける 3:両方開ける
def OpenArms(num):
    """アームを開閉します。
        Arduinoに指示を送ります。
        開閉の時間分待つ分までここに含まれます。
    Args:
        num (int): 指示コード 1:両方開く 2:両方閉じる 3: 右だけ開く 4:右だけ閉める
    """    
    ard.write(num.to_bytes(1, 'big'))
    time.sleep(0.4)





#レスキューキットを回収
def PickUpRescueKit():
    if rescue_photo:
        robot.straight(-30)
        DownRescueArm()
        robot.drive(0,speed)
        while True:
            get_sensors()
            if photo_ball:
                break
        robot.stop()
        OpenArms(2)
        UpRescueArm()
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

#レスキューゾーンに入ったときに実行。出るまでこの関数の中で完結。
isSearch=False #避難所、出口、入口の探索中　モード判定
def Rescue():
    
    dropped=False
    while True:
        get_sensors()
        if touch_R:
            robot.drive(speed,10)
        else:
            robot.drive(speed,-20)

        if cs_rescue.color()==Color.GREEN and (not dropped):
            domiso()
            robot.straight(300)
            robot.turn(90)
            robot.drive(-speed,0)
            time.sleep(0.2)
            robot.drive(speed,0)
            time.sleep(0.2)
            robot.turn(-90)
            dropped=True
        if cs_r.color()==Color.BLACK :
            if dropped:
                robot.stop()
                somido()
                return
            else:
                robot.straight(-300)
                robot.turn(90)
    

#レスキューのアームを上にあげる
UpRescueArm()

robot.stop()

while True:

    get_sensors()

    pid_run() 
    check_green() 
    if checkRed(): break
    if ObjectEscape(): continue 
    if isEnterRescue():
        ev3.speaker.beep(440)

        robot.straight(300)#前に出る
        robot.stop()
        robot.reset()
        Rescue()
        continue

    PickUpRescueKit()

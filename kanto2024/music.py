#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
class music:
    def __init__(self):
       self.ev3 = EV3Brick()
       self.ev3.speaker.set_volume(10)
       
    
    def PlayMusic(self,s,haku=500):
        """音楽を流します。

        Args:
            s (_type_): doremifasolatidoのテキストで流す音声
            haku (int, optional): 速さ（一つの音符にかけるミリ秒）. Defaults to 500.
        """    
        scores={"do":261,"re":293,"mi":329,"fa":349,"so":391,"la":440,"ti":493}
        l=len(s)//2
        for i in range(l):
            new_s=s[l*2:l*(2+1)]
            self.ev3.speaker.beep(scores[new_s],haku)


        
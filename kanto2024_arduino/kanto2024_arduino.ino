
// Arduinoのコードじゃあ

const int touch[4] = { 12, 11, 4, 5 };  // マクロスイッチ　右、左、アーム右、左

const int line_photo[3] = { A1, A3, A2 };  // ライントレース用のフォトリフレクタ 中央、右、左
const int photo_rescue = A7;

const int photo_ball = A0;
const int check_ball = 8;
const int arm_servo_R = 10;
const int arm_servo_L = 9;
const int back_servo = 6;
const int stop_btn = 4;


#include <Servo.h>  //サーボのためのライブラリ
Servo right;
Servo left;
void OpenRight() {
  right.write(70);
}
void CloseRight() {
  right.write(120);
}
void OpenLeft() {
  left.write(120);
}
void CloseLeft() {
  left.write(65);
}

int my_pow(int num) {
  int date = 1;
  for (int i = 0; i < num; i++) {
    date *= 2;
  }
  return date;
}

float Duration = 0;
float Distance = 0;
int GetUltrasonic() {
  const int echoPin = 2;
  const int trigPin = 3;
  pinMode(echoPin, INPUT);
  pinMode(trigPin, OUTPUT);

  digitalWrite(trigPin, LOW);

  delayMicroseconds(2);

  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  Duration = pulseIn(echoPin, HIGH);
  Duration = Duration / 2;
  Distance = Duration * 340 * 100 / 1000000;
  return ((int)Distance);
}

int GetTouch() {
  int date = 0;
  for (int i = 0; i < 4; i++) {
    if (!digitalRead(touch[i])) {
      date += my_pow(i);
    }
  }
  return date;
}

int getCheckBall() {
  if (!digitalRead(check_ball)) {
    return 1;
  } else {
    return 0;
  }
}

int GetPhoto(int num) {
  int val = analogRead(num);
  return val;
}

int GetColor() {
  return 0;
}
void setup() {
  // put your setup code here, to run once:
  Serial1.begin(9600);
  Serial.begin(9600);

  for (int i = 0; i < 4; i++) {
    pinMode(touch[i], INPUT_PULLUP);
  }

  pinMode(check_ball, INPUT_PULLUP);
  right.attach(10);
  left.attach(9);
  CloseRight();
  CloseLeft();
  delay(500);
  OpenRight();
  OpenLeft();
}

void forDebug() {

  //Serial.println(GetTouch());
  // for (int i = 0; i < 3; i++) {
  //   Serial.print(i);
  //   Serial.print(":");
  //   Serial.println(GetPhoto(line_photo[i]));
  // }
  // delay(1000);
  //  Serial.println(GetPhoto(photo_rescue));

  Serial.println(GetUltrasonic());

  //Serial.println(GetPhoto(photo_ball));
  //Serial.println(getCheckBall());

  // Serial.println(GetColor());
}

void loop() {
  //forDebug();
  // アーム開閉信号受信
  if (Serial1.available()) {
    int key = Serial1.read();
    Serial.println(key);
    switch (key) {
      case 1:
        OpenRight();
        OpenLeft();
        break;
      case 2:
        CloseRight();
        CloseLeft();
        Serial.println("nida");
        break;
      case 3:
        OpenRight();
        Serial.println("sanda");
        break;
      case 4:
        OpenLeft();
        break;
    }
  }
  // 信号　1.255 2.タッチセンサ 3.レスキューキット 4.超音波 5.ボール検知フォト 6.伝導性 7.カラーセンサ
  Serial1.write(255);

  Serial1.write(GetTouch());

  Serial1.write(GetPhoto(photo_rescue));

  //Serial1.write(GetUltrasonic());

  Serial1.write(GetPhoto(photo_ball));
  Serial1.write(getCheckBall());
  //Serial1.write(GetColor());
}

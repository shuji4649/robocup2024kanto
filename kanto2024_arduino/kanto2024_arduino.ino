
// Arduinoのコードじゃあ

const int touch[4] = {12, 11, 4, 5}; // マクロスイッチ　右、左、アーム右、左

const int line_photo[3] = {A1, A3, A2}; // ライントレース用のフォトリフレクタ 中央、右、左
const int photo_rescue = A7;

const int photo_ball = A3;
const int check_ball = 8;
const int arm_servo_R = 10;
const int arm_servo_L = 9;
const int back_servo = 6;
const int stop_btn = 4;
const int echoPin = 2;
const int trigPin = 3;

int my_pow(int num)
{
  int date = 1;
  for (int i = 0; i < num; i++)
  {
    date *= 2;
  }
  return date;
}
float Duration = 0;
float Distance = 0;
int GetUltrasonic()
{
  
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

int GetTouch()
{
  int date = 0;
  for (int i = 0; i < 4; i++)
  {
    if (!digitalRead(touch[i]))
    {
      date += my_pow(i);
    }
  }
  return date;
}

int getCheckBall()
{
  if (!digitalRead(check_ball))
  {
    return 1;
  }
  else
  {
    return 0;
  }
}

int GetPhoto(int num)
{
  int val = analogRead(A3);
  return val;
}

int GetColor()
{
  return 0;
}
void setup()
{
  // put your setup code here, to run once:
  Serial1.begin(9600);
  Serial.begin(9600);

  for (int i = 0; i < 4; i++)
  {
    pinMode(touch[i], INPUT_PULLUP);
  }

  pinMode(check_ball, INPUT_PULLUP);

}

void forDebug()
{

  // Serial.println(GetTouch());
  //  for (int i = 0; i < 3; i++)
  //  {
  //    Serial.println(GetPhoto(line_photo[i]));
  //  }

  Serial.println(GetPhoto(photo_rescue));

  //Serial.println(GetUltrasonic());

  // Serial.println(GetPhoto(photo_ball));
  // Serial.println(getCheckBall());
  return;
  Serial.println(GetColor());
}

void loop()
{
  forDebug();
  return;
  Serial1.write(255);

  Serial1.write(GetTouch());

  for (int i = 0; i < 3; i++)
  {
    Serial1.write(GetPhoto(line_photo[i]));
  }

  Serial1.write(GetPhoto(photo_rescue));

  Serial1.write(GetUltrasonic());

  Serial1.write(GetPhoto(photo_ball));
  Serial1.write(getCheckBall());
  Serial1.write(GetColor());
}

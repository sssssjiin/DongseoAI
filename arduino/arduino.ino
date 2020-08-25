const int motorPin = 9;     //상수 선언 : 모터 핀 번호
const int ledPin = 10;     //상수 선언 : LED 핀번호

void setup() {
	pinMode(motorPin, OUTPUT);//모터 핀 출력 생성
	pinMode(ledPin, OUTPUT);//LED 핀 출력 생성
	Serial.begin(9600);
}

void loop() {
	spiningMotor();//모터 출력 FUNCTION
	led();//LED 출력 FUNCTION
}

void led()
{
	int chk;//CHECK 값
	while (Serial.available() == 0) {}//시리얼 안받으면 씹힘
	chk = Serial.parseInt();//0~1로 CHEKING
	if (chk == true)
	{
		digitalWrite(ledPin, HIGH);//LED 출력
		Serial.println("LED : ON");
	}
	else
	{
		digitalWrite(ledPin, LOW);//LED 끔
		Serial.println("LED : OFF");
	}



}
void spiningMotor()
{
	int speed;//속도 값
	while (Serial.available() == 0) {}//시리얼 안받으면 씹힘
	speed = Serial.parseInt();//속도 입력
	speed = constrain(speed, 0, 255);     //속도를 PWM 출력 값 범위로 고정

	analogWrite(motorPin, speed);         //speed만큼으로 모터 돌리기

	//speed : 값을 출력
	Serial.print("speed : ");
	Serial.println(speed);

}
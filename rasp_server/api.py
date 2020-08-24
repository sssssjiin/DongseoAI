import RPi.GPIO as GPIO
from flask_restful import Resource, reqparse

LED_PIN = 1
MOTOR_PIN = 2

GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.setup(MOTOR_PIN, GPIO.OUT)

pwm = GPIO.PWM()
pwm.start(0)


class LEDController:
    class On(Resource):
        @staticmethod
        def get():
            try:
                GPIO.output(LED_PIN, True)
                return {"status": "Success"}
            except Exception as e:
                return {"status": "Fail", "reason": str(e)}

    class Off(Resource):
        @staticmethod
        def get():
            try:
                GPIO.output(LED_PIN, False)
                return {"status": "Success"}
            except Exception as e:
                return {"status": "Fail", "reason": str(e)}


class MotorController:
    speed = 0

    class SetSpeed(Resource):
        @staticmethod
        def get():
            try:
                parser = reqparse.RequestParser()
                parser.add_argument("speed", type=int)
                args = parser.parse_args()
                MotorController.speed = args.get("speed", 0)
                pwm.ChangeDutyCycle(MotorController.speed)
                return {"status": "Success"}
            except Exception as e:
                return {"status": "Fail", "reason": str(e)}

    class GetSpeed(Resource):
        @staticmethod
        def get():
            try:
                return {"status": "Success", "value": MotorController.speed}
            except Exception as e:
                return {"status": "Fail", "reason": str(e)}

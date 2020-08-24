from flask import Flask
from flask_restful import Api

from api import LEDController, MotorController

app = Flask(__name__)
api = Api(app)

api.add_resource(LEDController.On, "/led/on")
api.add_resource(LEDController.Off, "/led/off")

api.add_resource(MotorController.SetSpeed, "/motor/set_speed")
api.add_resource(MotorController.GetSpeed, "/motor/get_speed")

app.run(host="0.0.0.0", debug=True)

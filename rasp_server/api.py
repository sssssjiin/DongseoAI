from flask_restful import Resource


class LEDController:
    class On(Resource):
        pass

    class Off(Resource):
        pass


class MotorController:
    class SetSpeed(Resource):
        pass

    class GetSpeed(Resource):
        pass

    class On(Resource):
        pass

    class Off(Resource):
        pass

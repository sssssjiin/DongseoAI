import numpy as np

__eye_timestamp = list()
__eye_warning = list()


def pow_handler(data):
    right = data["AF3/theta"] / data["AF3/gamma"]
    left = data["AF4/theta"] / data["AF4/gamma"]

    flicker = (right + left) / 2

    if len(__eye_timestamp) > 10:
        __eye_timestamp.pop(0)
        __eye_warning.pop(0)

    __eye_timestamp.append(flicker)

    eye_flicker_std = np.std(__eye_timestamp)
    eye_flicker_mean = np.mean(__eye_timestamp)

    if 20 < eye_flicker_mean:
        __eye_warning.append(True)
    else:
        __eye_warning.append(False)

    if __eye_warning.count(True) > 5:
        # TODO 경고 메세지 전송
        print("경고")


def met_handler(data):
    eng = data["eng"]
    exc = data["exc"]
    stress = data["str"]
    rel = data["rel"]
    interest = data["int"]
    foc = data["foc"]

    val = (exc + stress) / (foc + rel)
    print(val)


def mot_handler(data):
    pass

import cortex


class PowerListener(cortex.Listener):
    cols: list

    def __init__(self, callback):
        self.callback = callback

    @cortex.Listener.handler(cortex.ID.SUBSCRIPTION.SUBSCRIBE)
    def handle_subscribe(self, data):
        for stream in data["success"]:
            if stream["streamName"] == "pow":
                self.cols = stream["cols"]

    @cortex.Listener.handler("pow")
    def handle_pow(self, data):
        dat = {k: v for (k, v) in zip(self.cols, data["pow"])}
        self.callback(dat)


class MetricListener(cortex.Listener):
    cols: list

    def __init__(self, callback):
        self.callback = callback

    @cortex.Listener.handler(cortex.ID.SUBSCRIPTION.SUBSCRIBE)
    def handle_subscribe(self, data):
        for stream in data["success"]:
            if stream["streamName"] == "met":
                self.cols = stream["cols"]

    @cortex.Listener.handler("met")
    def handle_metric(self, data):
        dat = {k: v for (k, v) in zip(self.cols, data["met"])}
        self.callback(dat)


class MotionListener(cortex.Listener):
    cols: list

    def __init__(self, callback):
        self.callback = callback

    @cortex.Listener.handler(cortex.ID.SUBSCRIPTION.SUBSCRIBE)
    def handle_subscribe(self, data):
        for stream in data["success"]:
            if stream["streamName"] == "mot":
                self.cols = stream["cols"]

    @cortex.Listener.handler("mot")
    def handle_metric(self, data):
        dat = {k: v for (k, v) in zip(self.cols, data["mot"])}
        self.callback(dat)

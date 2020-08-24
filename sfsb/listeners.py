import cortex.api as cortex


class PowerListener(cortex.Listener):
    def __init__(self):
        pass

    @cortex.Listener.handler(cortex.ID.SUBSCRIPTION.SUBSCRIBE)
    def handle_subscribe(self, data):
        pass

    @cortex.Listener.handler("pow")
    def handle_pow(self, data):
        pass


class MetricListener(cortex.Listener):
    def __init__(self):
        pass

    @cortex.Listener.handler(cortex.ID.SUBSCRIPTION.SUBSCRIBE)
    def handle_subscribe(self, data):
        pass

    @cortex.Listener.handler("met")
    def handle_metric(self, data):
        pass


class MotionListener(cortex.Listener):
    def __init__(self):
        pass

    @cortex.Listener.handler(cortex.ID.SUBSCRIPTION.SUBSCRIBE)
    def handle_subscribe(self, data):
        pass

    @cortex.Listener.handler("mot")
    def handle_metric(self, data):
        pass

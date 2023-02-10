import machine


class Timer():
    def __init__(self, timer: int, interrupt_handler=None):
        self.timer = machine.Timer(timer)
        self.interrupt_handler = interrupt_handler

    def start(self, time_ms, periodic=False):
        if periodic:
            self._start_periodic_timer(time_ms)
        else:
            self._start_oneshot_timer(time_ms)

    def _start_periodic_timer(self, time_ms):
        self.timer.init(period=time_ms, mode=machine.Timer.PERIODIC, callback=self.interrupt_handler)

    def _start_oneshot_timer(self, time_ms):
        self.timer.init(period=time_ms, mode=machine.Timer.ONE_SHOT, callback=self.interrupt_handler)

    def stop(self):
        self.timer.deinit()

    def update(self, time_ms):
        self.start(time_ms)

import machine


class Timer:
    def __init__(self, timer: int, interrupt_handler=None):
        self.__timer = machine.Timer(timer)
        self.interrupt_handler = interrupt_handler

    def start(self, time_ms, interrupt_handler=None, periodic=False):
        self.interrupt_handler = interrupt_handler or self.interrupt_handler
        if periodic:
            self.__start_periodic_timer(time_ms)
        else:
            self.__start_oneshot_timer(time_ms)

    def __start_periodic_timer(self, time_ms):
        self.__timer.init(period=time_ms, mode=machine.Timer.PERIODIC, callback=self.__interrupt_handler)

    def __start_oneshot_timer(self, time_ms):
        self.__timer.init(period=time_ms, mode=machine.Timer.ONE_SHOT, callback=self.__interrupt_handler)

    def __interrupt_handler(self, _=None):
        self.interrupt_handler()

    def stop(self):
        self.__timer.deinit()

    def update(self, time_ms):
        self.start(time_ms)

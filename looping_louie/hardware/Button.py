import machine

try:
    from python_louie.hardware.hw_config import DEBOUNCE_TIMER, ONBOARD_BUTTON_PIN
    from python_louie.hardware.Timer import Timer
except ImportError:
    import sys
    print(sys.path)
    sys.path.append('/hardware/')
    from hw_config import DEBOUNCE_TIMER, ONBOARD_BUTTON_PIN
    from Timer import Timer


class Button:
    def __init__(self, pin, handler_short_press, handler_long_press=None,
                 pin_state_pressed=True, debounce_time_ms: int = 200):
        self.pin = pin
        self.debounce_time_ms = debounce_time_ms
        self.__pin_state_pressed = pin_state_pressed
        self.interrupt_handler_short_press = handler_short_press
        self.interrupt_handler_long_press = handler_long_press if handler_long_press else handler_short_press

        self.__check_button_pressed_timer_ms = 50
        self.__long_press_minimum_time_ms = 250

        self.__time_pressed = 0

        self.__init_button()
        self.__enable_interrupt()

    def __init_button(self):
        self.button = machine.Pin(self.pin, machine.Pin.IN)

    @property
    def pressed(self):
        return self.button.value() == self.__pin_state_pressed

    def interrupt_handler(self, _=None):
        print(f"DEBUG | Button {self.pin} running interrupt handler")
        self.__disable_interrupt()
        self.__time_pressed = 0
        self.__debounce()

    def __enable_interrupt(self):
        trigger = machine.Pin.IRQ_RISING if self.__pin_state_pressed else machine.Pin.IRQ_FALLING
        self.button.irq(trigger=trigger, handler=self.interrupt_handler)
        print(f"DEBUG | Button {self.pin} interrupt enabled")

    def __disable_interrupt(self):
        self.__init_button()
        print(f"DEBUG | Button {self.pin} interrupt disabled")

    def __debounce(self):
        print(f"DEBUG | Button {self.pin} debouncing...")
        debounce_timer = Timer(DEBOUNCE_TIMER, interrupt_handler=self.__debounce_timer_handler)
        debounce_timer.start(self.debounce_time_ms)

    def __debounce_timer_handler(self, _=None):
        print(f"DEBUG | Button {self.pin} debouncing finished")
        self.__check_state()

    def __check_state(self, _=None):
        if self.pressed:
            print(f"DEBUG | Button {self.pin} waiting to be released")
            self.__time_pressed += 1
            # start timer for 100 ms and check again
            wait_timer = Timer(DEBOUNCE_TIMER, interrupt_handler=self.__check_state)
            wait_timer.start(self.__check_button_pressed_timer_ms)
            return
        self.__enable_interrupt()
        self.__evaluate_button_press()

    def __evaluate_button_press(self):
        print(f"DEBUG | Button {self.pin} evaluating button press")
        print(f"DEBUG | Button {self.pin} was pressed for more than {self.__time_pressed * self.__check_button_pressed_timer_ms} ms")
        if self.__time_pressed * self.__check_button_pressed_timer_ms >= self.__long_press_minimum_time_ms:
            print(f"DEBUG | Button {self.pin} long press detected")
            self.interrupt_handler_long_press()
        else:
            print(f"DEBUG | Button {self.pin} short press detected")
            self.interrupt_handler_short_press()


class OnboardButton(Button):
    def __init__(self, handler_short_press, handler_long_press=None, debounce_time_ms: int = 200):
        super().__init__(ONBOARD_BUTTON_PIN, handler_short_press, handler_long_press, pin_state_pressed=False,
                         debounce_time_ms=debounce_time_ms)

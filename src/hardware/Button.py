import machine

class Button():
    def __init__(self, button_pin, interrupt_handler):
        self.button = machine.Pin(button_pin, machine.Pin.IN)
        self.button.irq(trigger=machine.Pin.IRQ_RISING | machine.Pin.IRQ_FALLING, handler=interrupt_handler)
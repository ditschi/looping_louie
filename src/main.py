
# import machine
# import socket
# import time
# import network
# from hardware.Motor import MotorConfig
# from hardware.LoopingLouie import LoopingLouie
# from hardware.Led import OnboardLed
try:
    from hardware.Motor import MotorConfig
    from hardware.LoopingLouie import LoopingLouie
    from hardware.Led import OnboardLed
except ImportError:
    import sys
    sys.path.append('/hardware/')
    from Motor import MotorConfig
    from LoopingLouie import LoopingLouie
    from Led import OnboardLed


# def backup():
#     sta_if = network.WLAN(network.STA_IF)

#     if not sta_if.isconnected():
#         print('connecting to network...')
#         sta_if.active(True)
#         sta_if.connect('ssidname', 'ssidpassword')
#         while not sta_if.isconnected():
#             pass
#     print('network config:', sta_if.ifconfig())
#     html='''<!DOCTYPE html>
#     <html>
#     <head><title>ESP32 LED on/off</title></head>
#     <center><h2>WebServer for turning LED on </h2></center>
#     <form>
#     <button name="LED" value='ON' type='submit'> LED ON </button>
#     <button name="LED" value='OFF' type='submit'> LED OFF </button>
#     <br><br>
#     '''
#     LED0 = machine.Pin(2,machine.Pin.OUT)
#     LED0.value(0)
#     s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
#     s.bind(('',80))
#     s.listen(5)

#     while True:
#         conn,addr=s.accept()
#         print("GOT a connection from %s" % str(addr))
#         request=conn.recv(1024)
#         print("Content %s" % str(request))
#         request=str(request)
#         LEDON=request.find('/?LED=ON')
#         LEDOFF=request.find('/?LED=OFF')
#         if(LEDON==6):
#             LED0.value(1)
#         if(LEDOFF==6):
#             LED0.value(0)
#         response=html
#         conn.send(response)
#     conn.close()


# def on_off_switch_interrupt_handler():
#     led = OnboardLed()
#     led.toggle()

# def game_timer_interrupt_handler():
#     led = OnboardLed()
#     led.toggle()

# def motor_timer_interrupt_handler():
#     led = OnboardLed()
#     led.toggle()




def main():
    print("main()")
    # motor_config = MotorConfig(limit_speedchange=False)
    # louie = LoopingLouie(on_off_switch_interrupt_handler, game_timer_interrupt_handler, motor_config=motor_config)
    # #louie.motor.start(50)
    # led = OnboardLed()
    # led.blink(5)
    # led.off()


if __name__ in "__main__":
    print("DEBUG | running main.py")
    main()
    print("DEBUG | running main.py")

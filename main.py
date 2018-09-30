import machine
import network
import socket

ONBOARD_LED_PIN = 2  # Onboard Led Esp8266

#HTML to send to browsers
html = """<!DOCTYPE html>
<html>
<head> <title>ESP8266 LED ON/OFF</title> </head>
<center><h2>A simple webserver for turning LED's on and off with Micropython</h2></center>
<center><h3>(for noobs to both the ESP8266 and Micropython)</h3></center>
<form>
LED: 
<button name="LED" value="ON" type="submit">LED ON</button>
<button name="LED" value="OFF" type="submit">LED OFF</button><br><br>
</form>
</html>
"""

#Setup PINS
LED = machine.Pin(ONBOARD_LED_PIN, machine.Pin.OUT)

sta_if = network.WLAN(network.STA_IF)
ifconfig = sta_if.ifconfig()
current_ip = ifconfig[0]



#Setup Socket WebServer
addr = socket.getaddrinfo(current_ip, 80)[0][-1]
s = socket.socket()
s.bind(addr)
s.listen(1)

print('listening on', addr)

while True:
    cl, addr = s.accept()
    print('client connected from', addr)
    cl_file = cl.makefile('rwb', 0)
    # while True:
    #     line = cl_file.readline()
    #     if not line or line == b'\r\n':
    #         break
    request = cl.recv(1024)
    print("Content = %s" % str(request))
    request = str(request)
    LEDON = request.find('/?LED=ON')
    LEDOFF = request.find('/?LED=OFF')
    if LEDON == 6:
        print('TURN LED ON')
        LED.off()  # for ESP onboard led on/off are reversed
    if LEDOFF == 6:
        print('TURN LED OFF')
        LED.on()  # for ESP onboard led on/off are reversed
    response = html
    cl.send(response)
    cl.close()

# Looping Louie controlled with ESP8266

A little project to control the looping louie game using  wifi.

We are using microPython on a  ESP8266 to provide a  webserver.

There will be multiple game modes to choose from.


 ## Tricks

 ### Read ttyUSB0 and connect with mpfshell in parallell

```bash
mpfshell -o ttyUSB0
cat < /dev/ttyUSB0
```
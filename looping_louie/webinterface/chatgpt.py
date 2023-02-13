import socket
import network
import random

# Minimal- und Maximalwerte konfigurieren
MIN_SPEED = 100
MAX_SPEED = 200
MIN_DURATION = 1000
MAX_DURATION = 5000

# Funktion zum Verändern der Geschwindigkeit des Motors
def change_motor_speed(pwm):
  speed = random.uniform(MIN_SPEED, MAX_SPEED)
  pwm.duty(speed)

# Funktion zum Senden der Webseite
def send_html_page(conn):
  global MIN_SPEED, MAX_SPEED, MIN_DURATION, MAX_DURATION
  html = """
  <html>
    <body>
      <form action="/" method="post">
        <label>Minimal Geschwindigkeit (100-500):</label><input type="number" name="min_speed" value={}><br>
        <label>Maximal Geschwindigkeit (100-500):</label><input type="number" name="max_speed" value={}><br>
        <label>Minimal Dauer (1000-10000):</label><input type="number" name="min_duration" value={}><br>
        <label>Maximal Dauer (1000-10000):</label><input type="number" name="max_duration" value={}><br>
        <input type="submit" value="Speichern">
      </form>
    </body>
  </html>
  """.format(MIN_SPEED, MAX_SPEED, MIN_DURATION, MAX_DURATION)
  conn.send("HTTP/1.0 200 OK\r\n")
  conn.send("Content-Type: text/html\r\n")
  conn.send("Content-Length: {}\r\n".format(len(html)))
  conn.send("\r\n")
  conn.send(html)
  conn.close()

# Funktion zum Verarbeiten der Formulareingaben
def process_form_input(conn, request):
  global MIN_SPEED, MAX_SPEED, MIN_DURATION, MAX_DURATION
  form_input = request.split("\r\n")[-1]
  min_speed = int(form_input.split("min_speed=")[1].split("&")[0])
  max_speed = int(form_input.split("max_speed=")[1].split("&")[0])
  min_duration = int(form_input.split("min_duration=")[1].split("&")[0])
  max_duration = int(form_input.split("max_duration=")[1].split("&")[0])
  MIN_SPEED = min_speed
  MAX_SPEED = max_speed
  MIN_DURATION = min_duration
  MAX_DURATION = max_duration


# -------------------------------------------------------------

import machine, time
from machine import Pin, PWM
import uasyncio as asyncio
from uasyncio import Lock

# Set up the PWM output for controlling the speed of the motor
motor = PWM(Pin(12), freq=50)
motor.duty(0)

# Set up the lock for synchronizing access to the motor
motor_lock = Lock()

# Define the default minimum and maximum speeds and times
min_speed = 10
max_speed = 90
min_time = 1
max_time = 5

# Define the endpoint for controlling the speed of the motor
async def speed(request, response):
    await motor_lock.acquire()
    motor.duty(random.randint(min_speed, max_speed))
    await asyncio.sleep(random.randint(min_time, max_time))
    motor.duty(0)
    motor_lock.release()

# Define the endpoint for returning the current configuration
async def config(request, response):
    response.content_type = "application/json"
    response.write(json.dumps({"min_speed": min_speed, "max_speed": max_speed, "min_time": min_time, "max_time": max_time}))

# Define the endpoint for updating the configuration
async def update_config(request, response):
    global min_speed, max_speed, min_time, max_time
    data = await request.json()
    min_speed = data.get("min_speed", min_speed)
    max_speed = data.get("max_speed", max_speed)
    min_time = data.get("min_time", min_time)
    max_time = data.get("max_time", max_time)
    response.write("Configuration updated")

# Initialize the Picoweb app and add the defined endpoints
import picoweb
app = picoweb.WebApp(__name__)
app.route("/speed", "POST", speed)
app.route("/config", "GET", config)
app.route("/config", "POST", update_config)

# Start the app
app.run(debug=True, host="0.0.0.0")


# ---------------------------------------------------------


import picoweb

app = picoweb.WebApp(__name__)

@app.route("/")
def index(req, resp):
    yield from picoweb.start_response(resp)
    yield from resp.awrite("""
<!DOCTYPE html>
<html>
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    .slider {
      width: 100%;
    }
  </style>
</head>
<body>

<h2>Speed and Time Settings</h2>

<p>Set speed:</p>
<input type="range" min="0" max="100" value="50" class="slider" id="speedSlider">
<p id="speedValue">50</p>

<p>Set time:</p>
<input type="range" min="0" max="100" value="50" class="slider" id="timeSlider">
<p id="timeValue">50</p>

<button id="submitButton">Submit</button>

<script>
const speedSlider = document.getElementById("speedSlider");
const speedValue = document.getElementById("speedValue");
speedValue.innerHTML = speedSlider.value;

speedSlider.oninput = function() {
  speedValue.innerHTML = this.value;
}

const timeSlider = document.getElementById("timeSlider");
const timeValue = document.getElementById("timeValue");
timeValue.innerHTML = timeSlider.value;

timeSlider.oninput = function() {
  timeValue.innerHTML = this.value;
}

const submitButton = document.getElementById("submitButton");
submitButton.onclick = function() {
  const xhr = new XMLHttpRequest();
  xhr.open("POST", "/settings", true);
  xhr.setRequestHeader("Content-Type", "application/json");
  xhr.send(JSON.stringify({
    speed: speedSlider.value,
    time: timeSlider.value
  }));
}
</script>

</body>
</html>
    """)

@app.route("/settings", methods=["POST"])
def settings(req, resp):
    yield from req.read_form_data()
    speed = int(req.form["speed"])
    time = int(req.form["time"])
    # Hier kann der Code zur Verarbeitung der Einstellungen für Geschwindigkeit und Zeit eingefügt werden
    return "Settings saved"

app.run(debug=True)


# -----------------------

@app.route("/")
def index(req, resp):
    if req.method == "POST":
        # Parse the form data from the request
        form = req.form()
        # Access the values from the form
        speed_value = form["speed"]
        time_value = form["time"]
        # Do something with the values, such as saving them or using them to control the motor
        # ...
    else:
        # Render the form for the first time
        yield from picoweb.start_response(resp)
        yield from resp.awrite("<html><body><form method='post'>")
        yield from resp.awrite("Speed: <input type='text' name='speed'><br>")
        yield from resp.awrite("Time: <input type='text' name='time'><br>")
        yield from resp.awrite("<input type='submit' value='Submit'><br>")
        yield from resp.awrite("</form></body></html>")

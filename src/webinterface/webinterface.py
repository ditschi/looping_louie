import picoweb
import uasyncio as asyncio
from uasyncio import Lock


app = picoweb.WebApp(__name__)

# Set up the lock for synchronizing access to the motor
motor_lock = Lock()

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

# Define the endpoint for controlling the speed of the motor
@app.route("/speed", methods=["POST"])
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
async def update_config(min_speedrequest, response):
    data = await request.json()
    min_speed = data.get("min_speed", data["min_speed"])
    max_speed = data.get("max_speed", data["max_speed"])
    min_time = data.get("min_time", data["min_time"])
    max_time = data.get("max_time", data["max_time"])
    response.write("Configuration updated")

app.route("/config", "GET", config)
app.route("/config", "POST", update_config)
app.run(debug=True)
import network
import lib.picoweb as picoweb
from config import WIFI_SSID, WIFI_PASSWORD, PORT
from pins import Pins
from time import sleep, ticks_ms
import uasyncio as asyncio

app = picoweb.WebApp(__name__)


def setup():
    print("Starting...")

    # Turn off relays.
    Pins.change_relays_state(False)

    # Connect to wifi and return ip
    return connect()


def connect():
    Pins.on_board_led.off()
    print(f"Starting to connect to {WIFI_SSID}")
    # Connect to WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)

    while not wlan.isconnected():
        print('Waiting for connection...')
        sleep(1)

    Pins.on_board_led.on()
    ip = wlan.ifconfig()[0]
    print(f'Connected on {ip}')
    return ip


async def check_for_button_presses():
    last_pressed = ticks_ms()
    still_on = False
    while True:
        if Pins.button.value() == True:
            new_time = ticks_ms()
            if (new_time - last_pressed) > 1000 and not still_on:
                Pins.toggle_relays_state()
                still_on = True
                last_pressed = new_time
        else:
            still_on = False
        await asyncio.sleep(0.1)


@app.route("/")
def home(req, resp):
    app.log.info(req.qs)
    yield from picoweb.start_response(resp)
    with open("./static/index.html", "r") as index:
        yield from resp.awrite(index.read())


@app.route("/led/on")
def turn_led_on(req, resp):
    Pins.change_relays_state(True)
    return picoweb.jsonify(resp, Pins.get_state())


@app.route("/led/off")
def turn_led_off(req, resp):
    Pins.change_relays_state(False)
    return picoweb.jsonify(resp, Pins.get_state())


@app.route("/state")
def state(req, resp):
    return picoweb.jsonify(resp, Pins.get_state())


if __name__ == "__main__":
    ip = setup()

    loop = asyncio.get_event_loop()
    loop.create_task(check_for_button_presses())

    app.run(debug=True, host=ip, port=PORT)

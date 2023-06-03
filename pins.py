import machine
from sensor import TempSensors, Relays, CurrentSensor

class Pins:
    on_board_led: machine.Pin = machine.Pin('LED', machine.Pin.OUT)
    temp_sensor_18 = TempSensors(18)
    temp_sensor_20 = TempSensors(20)
    relays = Relays(13)
    current_sensor = CurrentSensor(pin=27, minimal_on_val=7000)
    button = machine.Pin(19, machine.Pin.IN, machine.Pin.PULL_UP)
    
    @staticmethod
    def change_relays_state(state: bool):
        Pins.relays.change_state(not state)
    
    @staticmethod
    def toggle_relays_state():
        Pins.relays.toggle_state()
        
    @staticmethod
    def get_state():        
        return {"is_on": Pins.relays.get_state(), "tempratures": {"18": Pins.temp_sensor_18.get_temps(), "20": Pins.temp_sensor_20.get_temps()}, "current": Pins.current_sensor.is_on()}

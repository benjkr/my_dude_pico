import onewire, ds18x20, time
from sys import maxsize
from machine import ADC, Pin

class TempSensors:
    def __init__(self, pin_num:int):
        try:
            self.pin = Pin(pin_num)
            self.ds_sensor = ds18x20.DS18X20(onewire.OneWire(self.pin))
            self.temps = self.get_temps()
        except Exception as e:
            print(e)
            self.ds_sensor = None
        
    def get_temps(self):
        if self.ds_sensor is None:
            return None
        
        roms = self.ds_sensor.scan()
        
        self.ds_sensor.convert_temp()
        #time.sleep_ms(750)
        return self.ds_sensor.read_temp(roms[0])
        #return [{"name": bytes(rom), "value": self.ds_sensor.read_temp(rom)} for rom in roms]

class CurrentSensor:
    # VREF = 5.0
    # ACTectionRange = 20
    
    def __init__(self, pin: int, minimal_on_val: int):
        self.pin = ADC(Pin(pin))
        self.minimal_on_val = minimal_on_val
        
    def normalize(self, num):
        return num
        # voltageVirtualValue = num * 0.707    #change the peak voltage to the Virtual Value of voltage
        
        # voltageVirtualValue = (voltageVirtualValue / 1024 * VREF ) / 2

        # ACCurrtntValue = voltageVirtualValue * ACTectionRange

        # return ACCurrtntValue

    def read_current(self):
        maxVal = 0
        minVal = maxsize
        # ACCurrtntValue = 0
        # peakVoltage = 0
        # voltageVirtualValue = 0;  #Vrms
        
        counter = 0
        start_time = time.ticks_ms()
        while time.ticks_diff(time.ticks_ms(), start_time) < 30:
            val = self.pin.read_u16()
            maxVal = max(maxVal, val)  #read peak voltage
            minVal = min(minVal, val)  #read peak voltage
            counter += 1
            time.sleep_us(100)
        #print(counter)
        norm_max = self.normalize(maxVal)
        norm_min = self.normalize(minVal)
        
        return norm_max, norm_min, norm_max - norm_min
    
    def is_on(self):
        norm_max, norm_min, diff = self.read_current()
        #diff = (diff - 2000) / 10000 / 5
        
        # print(norm_max, norm_min, diff)
        
        return diff >= self.minimal_on_val

class Relays:
    def __init__(self, pin:int):
        self.relay = Pin(pin, Pin.OUT)
        
    def change_state(self, state: bool):
        self.relay.value(int(state))
    
    def toggle_state(self):
        self.relay.toggle()
    
    def get_state(self):
        return not self.relay.value()
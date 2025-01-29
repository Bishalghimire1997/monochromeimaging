from pyvisa import ResourceManager
class LEDPulseModeController():
    def __init__(self, instrument):
        self._instrument = instrument
        instrument.write("SOURce:MODE PULS")     
        self.on_time = 0.009
        self.off_time =0.01
        self.pulse_amplitude = 100
        self.pulse_count =1
        self.__initialize()
    def on(self):
        """turns the led on
        """
        self._instrument.write("OUTPut:STATe ON")
    def off(self):
        """turns the led off
        """
        self._instrument.write("OUTPut:STATe OFF")

    def set_pulse_count(self,val:int):
        self._instrument.write('SOURce:PULS:COUNt '+str(val))

    def set_on_time(self,val):
        self._instrument.write('SOURce:PULS:ONt '+str(val))

    def set_off_time(self,val):
        self._instrument.write('SOURce:PULS:OFFt '+str(val))

    def set_pulse_amplitude(self,val):        
        self._instrument.write('SOURce:PULS:BRIGhtness:LEVel:AMPLitude '+str(val))
    def get_led_status(self):
        return self._instrument.query('OUTP:STATe?').strip()
    def __initialize(self):
        self.set_off_time(self.off_time)
        self.set_on_time(self.on_time)
        self.set_pulse_amplitude(self.pulse_amplitude)
        self.set_pulse_count(self.pulse_count)    
        
    
class LedConfig():
    def __init__(self):
        self._resource_manager = ResourceManager()
        self._leds = self._detect_led()
        self.blue_led = LEDPulseModeController(self._leds[0])
        self.red_led = LEDPulseModeController(self._leds[2])
        self.green_led = LEDPulseModeController(self._leds[1])

    def get_blue_led(self):
        return self.blue_led

    def get_red_led(self):
        return self.green_led

    def get_green_led(self):
        return self.red_led
    
    def _detect_led(self):
        relevant_resources=[]
        resources = self._resource_manager.list_resources()
        print(resources)
        relevant_resources.append(resources [0])
        relevant_resources.append(resources [1])
        relevant_resources.append(resources [2])
        return self._open_resources(relevant_resources)

    def _open_resources(self,relevant_resourcss:list):
        temp =[]
        for i in relevant_resourcss:
            temp.append(self._resource_manager.open_resource(i))
        return temp
    def close_resources(self):
        """Method to close the resources
        """
        self._resource_manager.close()





    





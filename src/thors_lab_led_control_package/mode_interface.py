class CommonMethods():
    def __init__(self,instrument):
        self._instrument = instrument
        self._led_state:bool
        pass
    def on(self):
        """turns the led on
        """
        self._led_state=self._instrument.write("OUTPut:STATe ON")
        print(self._led_state)
    def off(self):
        """turns the led off
        """
        self._led_state= self._instrument.write("OUTPut:STATe OFF")
        print(self._led_state)

    # """ def audio_signal(self,activate:bool):
    #     """activete/deacticate the warning signal
    #     """
    #     if activate:
    #        self._beeper_state = self._instrument.write('SYSTem:BEEPer:STATe ON')
    #     else:
    #          self._beeper_state = self._instrument.write("SYSTem:BEEPer:STATe OFF")
    #     print(self._beeper_state)
    #     pass """

    def get_max_opetaing_voltage(self):
        """Query maximum LED forward voltage specified by the head’s onboard info memory
        """
        pass
    def get_led_voltage(self):
        """Returns the measured LED voltage"""
        pass

    def get_max_operating_current(self):
        """Query maximum LED forward current specified by the head’s onboard info memory
        """
        pass
    def get_led_cuttent(self):
        """Returns the measured LED current.
        """
        pass
    def get_led_temperature(self): # give the option to select the temperatue unit as well
        """Returns the measured LED temperature.
        """


    def get_spectrum_info(self):
        """Query the spectrum information of the LED head
        """

    def set_mode(self,mode:str ):#define ENUMS fro Different MODE
        """Set the LED operating mode:"""
        self._instrument.write('SOURce:MODe '+mode)

    
class CommonMethods():
    def __init__(self,instrument):
        self._instrument = instrument
        self._led_state:bool
    def on(self):
        """turns the led on
        """
        print("on")
        self._led_state=self._instrument.write("OUTPut:STATe ON")
    def off(self):
        """turns the led off
        """
        self._led_state= self._instrument.write("OUTPut:STATe OFF")

    def set_mode(self,mode:str ):#define ENUMS fro Different MODE
        """Set the LED operating mode:"""
        self._instrument.write('SOURce:MODe '+mode)
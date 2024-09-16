"""_Runs the LED module in constant brightness mode
    """
from thors_lab_led_control_package.mode_interface import CommonMethods
class ConstantBrightness(CommonMethods):
    """Runs the LED in constant brightness mode

    Args:
        CommonMethods (_type_): children class of CommonMethods
    """
    def __init__(self,instrument):
        self._instrument =instrument
        self._instrument.write('SOURce:MODe CB')
        super().__init__(self._instrument)
        self._forward_current:float           
    def set_forward_current(self,val:float):
        """sets the forward current 

        Args:
            val (float): set value of forward current
        """
        self._instrument.write(':CCURrent:LEVel:AMPLitude '+str(val))
    def get_forward_current(self):
        """returns current forward current value
        """
        return self._instrument.query(':CCURrent:LEVel:AMPLitude?')
    def get_led_brightness(self):
        """Set the maximum brightness in % of limit current
        """
        return self._instrument.query('SOURce:CBRightness:BRIGhtness:LEVel:AMPLitude?')
    def set_led_brigntness(self,val:float):
        """Query the maximum brightness in % of limit current
        """
        self._instrument.write('SOURce:CBRightness:BRIGhtness:LEVel:AMPLitude '+str(val))
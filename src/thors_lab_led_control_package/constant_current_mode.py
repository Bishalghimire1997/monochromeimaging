from thors_lab_led_control_package.mode_interface import CommonMethods
class ConstantCurrent(CommonMethods):
    """_summary_

    Args:
        CommonMethods (_type_): _description_
    """
    def __init__(self,instrument):
        self._instrument = instrument
        self._instrument.write('SOURce:MODe CC')
        super().__init__(self._instrument)
    def set_limit_currrent(self,val:float): #sets cinstant current mode forward current value
        """sets the current limit value for the LED

        Args:
            val : float: Is the value for current limit
        """
        self._instrument.write(':LIMit:AMPLitude '+str(val))

    def get_limit_current(self):
        """returns the current Current limit       
        """
        return  self._instrument.query(':LIMit:AMPLitude?')

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

from thors_lab_led_control_package.pulsemode import LedConfig
from abc import ABC
class StateInterface(ABC):
    """ interface to LED state impl"""

class StateGreen(StateInterface):
    def __init__(self,led:LedConfig):
        self.__led = led.get_green_led()
        self.__next_state = self 
    def set_next_state(self,state):
         self.__next_state = state
    
    def get_next_state(self):
       
        # while int(self.get_status()) == 1:
        #     pass
        return self.__next_state 
    
    def get_flag(self):
        return "G"
    def activate(self):
        self.__led.on()
    def deactivate(self):
        self.__led.off()
    def get_status(self):
        return self.__led.get_led_status()
    
class StateRed(StateInterface):
    def __init__(self,led:LedConfig):
        self.__led = led.get_red_led()
        self.__next_state = self 
            
    def get_flag(self):
        return "R"
    def set_next_state(self,state):
        self.__next_state = state
    def get_next_state(self):
        # while int(self.get_status()) == 1:
        #      pass       
       
        return self.__next_state  
    def activate(self):
        self.__led.on()
    def deactivate(self):
        self.__led.off()        
    def get_status(self):
        return self.__led.get_led_status()

class StateBlue(StateInterface):
    def __init__(self,led:LedConfig):
        self.__led = led.get_blue_led()
        self.__next_state = self 
    def set_next_state(self,state):
         self.__next_state = state 
    def get_flag(self):
        return "B"    
    def get_next_state(self):
        # while int(self.get_status()) == 1:
        #      pass    
        return self.__next_state
    def activate(self):
        self.__led.on()
    def deactivate(self):
        self.__led.off()
    def get_status(self):
        return self.__led.get_led_status()

class StateMachinePulse():
    def __init__(self):
        self.__led = LedConfig() 
        self._b= StateBlue(self.__led)
        self._g= StateGreen(self.__led)
        self._r=StateRed(self.__led)
        self._b.set_next_state(self._g)
        self._g.set_next_state(self._r)
        self._r.set_next_state(self._b)
    def get_first_state(self):
        return self._b
    def close_resources(self):
        self.__led.close_resources()
      
  

    

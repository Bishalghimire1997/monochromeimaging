from thors_lab_led_control_package.led_control import LedControl
from abc import ABC
class StateInterface(ABC):
    """ interface to LED state impl"""

class StateGreen(StateInterface):
    def __init__(self):
        self.__led = LedControl()
        self.__next_state = self 
        self.__cb_object = self.__led.turn_dedicated_on([0,0,0])
        self.__cb_object_off = self.__led.turn_dedicated_on([0,0,0])
    def set_next_state(self,state):
         self.__next_state = state
    def get_next_state(self):
        return self.__next_state  
    def get_flag(self):
        return "G"
    def activate(self):
        print(self.get_flag())
        self.__cb_object = self.__led.turn_dedicated_on([0,0,1])
    def deactivate(self):
        self.__led.turn_dedicated_off(self.__cb_object_off)
        pass
    
class StateRed(StateInterface):
    def __init__(self):
        self.__led = LedControl()
        self.__next_state = self 
        self.__cb_object = self.__led.turn_dedicated_on([0,0,0])
        self.__cb_object_off = self.__led.turn_dedicated_on([0,0,0])
        
    def current_state(self):
        self.__led = LedControl()  
        return self     
    def get_flag(self):
        return "R"
    def set_next_state(self,state):
        self.__next_state = state
    def get_next_state(self):
        return self.__next_state  
    def activate(self):
        print(self.get_flag())
        self.__cb_object = self.__led.turn_dedicated_on([0,1,0])
    def deactivate(self):
        self.__led.turn_dedicated_off(self.__cb_object)        
        pass

class StateBlue(StateInterface):
    def __init__(self):
        self.__led = LedControl() 
        self.__next_state = self 
        self.__cb_object = self.__led.turn_dedicated_on([0,0,0])
        self.__cb_object_off = self.__led.turn_dedicated_on([0,0,0])
    def set_next_state(self,state):
         self.__next_state = state     
    def get_flag(self):
        return "B"    
    def get_next_state(self):
        return self.__next_state
    def activate(self):
        print(self.get_flag())
        self.__cb_object = self.__led.turn_dedicated_on([1,0,0])
    def deactivate(self):
        self.__led.turn_dedicated_off(self.__cb_object)
    

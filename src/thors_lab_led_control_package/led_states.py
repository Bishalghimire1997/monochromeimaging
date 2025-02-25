from thors_lab_led_control_package.led_control import LedControl
from flir_camera_parameter_package.flir_camera_shutter_parameters import ShutterTimeControl
from flir_camera_parameter_package.flir_camera_parameters import FlirCamParam
from abc import ABC
class StateInterface(ABC):
    """ interface to LED state impl"""

class StateGreen(StateInterface):
    def __init__(self,led):
        self.__led = led 
        self.__next_state = self
        self._shutter = ShutterTimeControl() 
        self.param = FlirCamParam()


    def set_next_state(self,state):
         self.__next_state = state
    def get_led_brightness(self):
        return self.__led.get_led_brightness()    
    def get_next_state(self):
        return self.__next_state  
    def get_flag(self):
        return "G"
    def activate(self):
        self.__led.turn_dedicated_on([0,0,0.5])
    def deactivate(self):
        self.__led.turn_dedicated_on([0,0,0])
    def setExp(self,cam):
        cam=self._shutter.manual_shutter(cam,self.param.exp_green)
        return cam   
    
class StateRed(StateInterface):
    def __init__(self,led):
        self.__led = led 
        self._shutter = ShutterTimeControl()
        self.param = FlirCamParam()

            
    def get_flag(self):
        return "R"
    def get_led_brightness(self):
        return self.__led.get_led_brightness()
    def set_next_state(self,state):
        self.__next_state = state
    def get_next_state(self):
        return self.__next_state  
    def activate(self):
        self.__led.turn_dedicated_on([0,0.5,0])
    def deactivate(self):
        self.__led.turn_dedicated_on([0,0,0])    
    def setExp(self,cam):
        cam=self._shutter.manual_shutter(cam,self.param.exp_red)
        return cam    

class StateBlue(StateInterface):
    def __init__(self,led):
        self.__led = led 
        self.__next_state = self
        self._shutter = ShutterTimeControl()
        self.param = FlirCamParam()


    def set_next_state(self,state):
         self.__next_state = state 
    def get_led_brightness(self):
        return self.__led.get_led_brightness()    
    def get_flag(self):
        return "B"    
    def get_next_state(self):
        return self.__next_state
    def activate(self):
        self.__led.turn_dedicated_on([0.5,0,0])
    def deactivate(self):
        self.__led.turn_dedicated_on([0,0,0])    
    def setExp(self,cam):
        cam=self._shutter.manual_shutter(cam,self.param.exp_blue)
        return cam


class StateMachineBGR():
    def __init__(self):
        self.__led = 1#LedControl() 
        self._b= StateBlue(self.__led)
        self._g= StateGreen(self.__led)
        self._r=StateRed(self.__led)
        self._b.set_next_state(self._g)
        self._g.set_next_state(self._r)
        self._r.set_next_state(self._b)
    def get_first_state(self):
        return self._b
    
      
  

    

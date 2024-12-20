from flir_cam_led_and_camera_control_package.state_interface import StateInterface
from thors_lab_led_control_package.led_control import LedControl
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
 
  
    

    def activate(self):
        self.__cb_object = self.__led.turn_dedicated_on([0,0,1])
    def deactivate(self):
        self.__led.turn_dedicated_off(self.__cb_object_off)
        pass
    

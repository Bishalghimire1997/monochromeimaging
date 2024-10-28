import time 
from flir_cam_led_and_camera_control_package.stateblue import StateBlue
from flir_cam_led_and_camera_control_package.state_green import StateGreen
from flir_cam_led_and_camera_control_package.state_red import StateRed

class SequenceControl():
    def __init__(self):
        self._b= StateBlue()
        self._g= StateGreen()
        self._r=StateRed()
        self._b.set_next_state(self._g)
        self._g.set_next_state(self._r)
        self._r.set_next_state(self._b)

    def activate(self):
        state= self._b
        for i in range (102):
            print(i)
            state.activate()
            state = state.get_next_state()
        state.deactivate()

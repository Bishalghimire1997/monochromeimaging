""" teste set for led_control class
    """
import time
from pyvisa import ResourceManager
from thors_lab_led_control_package.led_state_pulse import StateMachinePulse
from thors_lab_led_control_package.led_states import StateMachineBGR
def state_test_constant_brightness(): 
    state = StateMachineBGR().get_first_state()
    for i in range(50):
        state.activate()
        state = state.get_next_state()
    state.deactivate()
def state_test_pulse(): 
    sm = StateMachinePulse()

    state = sm.get_first_state()
    for i in range(10):
        state.activate()
        time.sleep(0.5)
        state= state.get_next_state()
    sm.close_resources()
if __name__ == "__main__":
     state_test_pulse()



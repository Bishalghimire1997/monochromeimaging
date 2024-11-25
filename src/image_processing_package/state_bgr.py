import numpy as np
from image_processing_package.frame_reconstriction_state_interface import FrameReconstructionInterface
class StateBGR(FrameReconstructionInterface):
    def __init__(self):
        self._next_state = self        
    def correct(self,arr):
        """Method to correct BGR to BGR"""        
        return arr
    def set_next_state(self,state):
        self._next_state = state 
        pass
    def get_next_state(self):
        return self._next_state
        pass
    def get_state(self):
        return self
    
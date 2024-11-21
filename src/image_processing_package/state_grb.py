import numpy as np
from image_processing_package.frame_reconstriction_state_interface import FrameReconstructionInterface
class StateGRB(FrameReconstructionInterface):
    def __init__(self,image_list):
        self._img = image_list
        self._next_state = self        
    def correct(self,arr):
        """Method to correct GRB to BGR"""
        temp = []
        temp.append(arr[2])
        temp.append(arr[0])
        temp.append(arr[1])
        return temp
    def set_next_state(self,state):
        self._next_state = state 
        pass
    def get_next_state(self):
        return self._next_state
        pass
    def get_state(self):
        return self
    
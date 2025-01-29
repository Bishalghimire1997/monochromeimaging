
from abc import ABC
class FrameReconstructionInterface(ABC):
    """Interface of the statemachine"""

class StateBGR(FrameReconstructionInterface):
    def __init__(self):
        self._next_state = self        
    def correct(self,arr):
        """Method to correct BGR to BGR"""   
        print("state BGR")     
        return arr
    def set_next_state(self,state):
        self._next_state = state
    def get_next_state(self):
        return self._next_state
    def get_state(self):
        return self

class StateGRB(FrameReconstructionInterface):
    def __init__(self):
        self._next_state = self       
    def correct(self,arr):
        """Method to correct GRB to BGR"""
        temp = []
        temp.append(arr[2])
        temp.append(arr[0])
        temp.append(arr[1])
        print("state GRB")  
        return temp
    def set_next_state(self,state):
        self._next_state = state
    def get_next_state(self):
        return self._next_state
    def get_state(self):
        return self

class StateRBG(FrameReconstructionInterface):
    def __init__(self):
        self._next_state = self
        
    def correct(self,arr):
        """Method to correct RBG to BGR"""
        temp = []
        temp.append(arr[1])
        temp.append(arr[2])
        temp.append(arr[0])
        print("state RBG")  
        return temp
    def set_next_state(self,state):
        """_summary_

        Args:
            state (_type_): _description_
        """
        self._next_state = state 

    def get_next_state(self):
        """returns the nex state
        Returns:
            _type_: object of next state 
        """
        return self._next_state
    def get_state(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return self
    




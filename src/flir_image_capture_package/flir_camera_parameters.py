from parameter_interface import Parameters
class FlirCamParam(Parameters):
   path = "add path"
   snapCount =100
   trigger = False   
   def __init__(self):
       pass
   def get_path(self):
       return self.path
   def set_path(self,val):
       self.path =val   
   def get_snap_counts(self):
        return self.snapCount
   def get_trigger(self):
       return self.trigger
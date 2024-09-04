from ParameterInterface import Parameters
class FlirCamParam(Parameters):
     path = "add path"
     snapCount =1
   
     def getPath(self):
        return self.path
     def setPath(self,val):
        self.path =val
     def getSnapCounts(self):
        return self.snapCount

   
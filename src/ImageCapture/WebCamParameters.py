from ParameterInterface import Parameters
class WebCamParam(Parameters):
    trigger =0
    snapCounts =1
    path = "string"

    def __init__(self):
        pass
    def getTrigger(self):
        return self.trigger
    def setTrigger(self,val):
        self.trigger= val

        pass
    def getPath(self):
        return self.path
        pass
    def setPath(self):
        pass
    def getSnapCounts(self):
        return self.snapCounts

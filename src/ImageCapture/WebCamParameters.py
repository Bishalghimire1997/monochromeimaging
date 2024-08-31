from ParameterInterface import parameters
class Parameters(parameters):
    trigger =0
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

from abc import ABC, abstractmethod

class Parameters (ABC):
    path = "add path"
    snapCpunt =1
    @abstractmethod
    def getPath(self):
        return self.path
    def setPath(self,val):
        self.path =val
    def getSnapCount(self):
        return self.snapCount




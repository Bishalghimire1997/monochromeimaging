from abc import ABC, abstractmethod
class Camera(ABC):
    @abstractmethod
    def capture(self):
        pass
    def save(self):
        pass

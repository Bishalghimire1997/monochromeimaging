

class FlirCamParam():
    """
    FlirCamParam is a class for managing parameters of a FLIR camera.

    Attributes:
        path (str): The file path for saving images.
        snapCount (int): The number of snapshots to take.
        trigger (bool): The trigger status of the camera.
    """
    def __init__(self):
        """
        Initializes the FlirCamParam class with default values.
        """
        self._path:str = "image.h5"
        self._snap_count:int = 1000
        self._trigger:bool = False
        self._default_shutter_time:bool =True
        self._shutter_time:int=3000
    @property
    def default_shutter_time(self):
        """Flag to check if the manual shutter speed is requested.
          Returns: Boolean Flag 
        """
        return self._default_shutter_time
    @property
    def shutter_time(self):
        """gives time period for which the shutter should remain open 
        Returns: shutter open time as integer
        """
        return self._shutter_time
    @property
    def path(self):
        """
        Gets the current file path.

        Returns:
            str: The current file path.
        """
        return self._path
    @property
    def snap_count(self):
        """
        Gets the number of snapshots to take.

        Returns:
            int: The number of snapshots.
        """
        return self._snap_count
    @property
    def trigger(self):
        """
        Gets the trigger status of the camera.

        Returns:
            bool: The trigger status.
        """
        return self._trigger
    @path.setter
    def path(self, val):
        self._path = val

    @snap_count.setter
    def snap_count(self,val):
        self._snap_count=val

    @shutter_time.setter
    def shutter_time(self,val:int):
        self._shutter_time=val

    @default_shutter_time.setter
    def default_shutter_time(self,val:bool):
        self._default_shutter_time =val

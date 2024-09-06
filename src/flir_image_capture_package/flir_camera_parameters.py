from flir_image_capture_package.parameter_interface import Parameters

class FlirCamParam(Parameters):
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
        self._path = "add path"
        self._snap_count = 100
        self._trigger = False

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
           
    
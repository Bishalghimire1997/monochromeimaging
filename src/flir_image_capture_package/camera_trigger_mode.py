import PySpin
from PySpin import Camera
from flir_camera_parameter_package.flir_camera_shutter_parameters import ShutterTimeControl
from flir_camera_parameter_package.flir_camera_parameters import FlirCamParam
class SoftwareTrigger():
    def __init__(self):
        self._system= PySpin.System.GetInstance()
        self._cam:Camera = self._system.GetCameras()[0]
        self._cam.Init()
        self._param = FlirCamParam()
        self._shutter = ShutterTimeControl(self._cam)
        self.nodemap = self._cam.GetNodeMap()
        if not  self._param.default_shutter_time: #Check if manual shutter time is requested
            self._cam =self._shutter.manual_shutter(self._cam,150000) #150000
        else: 
            self.cam = self._shutter.auto_shutter_time(self._cam)
    def _reset_trigger(self):
         node_trigger_mode = PySpin.CEnumerationPtr(self.nodemap.GetNode('TriggerMode'))
         node_trigger_mode_off = node_trigger_mode.GetEntryByName('Off')
         node_trigger_mode.SetIntValue(node_trigger_mode_off.GetValue())       

    def _config_trigger(self):
        node_trigger_mode = PySpin.CEnumerationPtr(self.nodemap.GetNode('TriggerMode'))
        node_trigger_mode_off = node_trigger_mode.GetEntryByName('Off')
        node_trigger_mode.SetIntValue(node_trigger_mode_off.GetValue())
        node_trigger_selector= PySpin.CEnumerationPtr(self.nodemap.GetNode('TriggerSelector'))
        node_trigger_selector_framestart = node_trigger_selector.GetEntryByName('FrameStart')
        node_trigger_selector.SetIntValue(node_trigger_selector_framestart.GetValue())
        node_trigger_source = PySpin.CEnumerationPtr(self.nodemap.GetNode('TriggerSource'))
        node_trigger_source_software = node_trigger_source.GetEntryByName('Software')
        node_trigger_source.SetIntValue(node_trigger_source_software.GetValue())
        node_trigger_mode_on = node_trigger_mode.GetEntryByName('On')
        node_trigger_mode.SetIntValue(node_trigger_mode_on.GetValue())
    def _acquire_image(self):
         node_acquisition_mode = PySpin.CEnumerationPtr(self.nodemap.GetNode('AcquisitionMode'))
         node_acquisition_mode_continuous = node_acquisition_mode.GetEntryByName('Continuous')
         acquisition_mode_continuous = node_acquisition_mode_continuous.GetValue()
         node_acquisition_mode.SetIntValue(acquisition_mode_continuous)
         self._cam.BeginAcquisition()
         self._grab_next_image_by_trigger()
         image_result = self._cam.GetNextImage(1000)
         image = image_result.GetNDArray()
         image_result.Release()
         self._cam.EndAcquisition()
         return image

    def _grab_next_image_by_trigger(self):
        node_softwaretrigger_cmd = PySpin.CCommandPtr(self.nodemap.GetNode('TriggerSoftware'))
        node_softwaretrigger_cmd.Execute()
    def capture(self):
        self._config_trigger()
        image = self._acquire_image()
        self._reset_trigger()
        return image






        
        




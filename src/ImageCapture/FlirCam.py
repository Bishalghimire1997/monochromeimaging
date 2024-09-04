"""/**
* This algorithm is designed for FLIR BFS-U3-51S5M-C Camera
* During the time of development, FLLIR supported Python 3.5, 3.6, 3.7, 3.8 and 3.10.(This algorithm is developed in Python 3.10.14)
* It is importrant to install PySpin (this library is different from exsisting "pyspin" library) go to https://www.flir.com/support-center/iis/machine-vision/downloads/spinnaker-sdk-download/spinnaker-sdk--download-files/

*/"""

"""/**camera can be set to different accusition mode
* Single Frame capture mode -> CAPTURES SINGLE IMAGE
* Multi frame capture mode -> CAPTURES SETS OF MULTIPLE IMAGES
* Continious Mode          -> CAPTURES CONTINIOUS STREAM OF IMAGES

modes can be switched as  PySpin.CEnumerationPtr(nodemap.GetNode('AcquisitionMode')).GetEntryByName('Continuous')
STATE DESIGH PATTERN CAN BE IMPLEMENTED TO SWITCH BETWEEN THESE STAGE IN SINGLE CLICK IF NEEDED
FOR NOW WE WORK ON CONTINIOUS MODE
*/"""       

from CameraInterface import Camera
from FlirCamParameters import FlirCamParam
import PySpin
import threading   

class FlirCam(Camera):   
   

    def initializeCamera(self):
     NUM_IMAGES=10
     
     
    # LOOKING FOR CONNECTED CAMERAS
     system = PySpin.System.GetInstance()
     cam= system.GetCameras()[0] 

    #GETTING NODE MAPS
     
     nodemap_tldevice = cam.GetTLDeviceNodeMap()
     cam.Init()
     nodemap = cam.GetNodeMap() 

    #SETTING STREAM MODE

     streamMode = "TeledyneGigeVision" 
     streamMode1="LWF"
     streamMode2 ="Socket"

     nodemap_tlstream = cam.GetTLStreamNodeMap()
     node_stream_mode = PySpin.CEnumerationPtr(nodemap_tlstream.GetNode('StreamMode'))
     node_stream_mode_custom = PySpin.CEnumEntryPtr(node_stream_mode.GetEntryByName(streamMode))
     stream_mode_custom = node_stream_mode_custom.GetValue()
     node_stream_mode.SetIntValue(stream_mode_custom)
     

    # SELECTING THE CONTINIOUS MODE OF EXECUTION  
     node_acquisition_mode = PySpin.CEnumerationPtr(nodemap.GetNode('AcquisitionMode'))
     node_acquisition_mode_continuous = node_acquisition_mode.GetEntryByName('Continuous') 
     acquisition_mode_continuous = node_acquisition_mode_continuous.GetValue()
     node_acquisition_mode.SetIntValue(acquisition_mode_continuous)

     #START ACQUISITION

     cam.BeginAcquisition()

     device_serial_number = ''
     node_device_serial_number = PySpin.CStringPtr(nodemap_tldevice.GetNode('DeviceSerialNumber'))
     if PySpin.IsReadable(node_device_serial_number):
        device_serial_number = node_device_serial_number.GetValue()
        print('Device serial number retrieved as %s...' % device_serial_number)
    
     processor = PySpin.ImageProcessor()
     processor.SetColorProcessing(PySpin.SPINNAKER_COLOR_PROCESSING_ALGORITHM_HQ_LINEAR)

     for i in range(NUM_IMAGES):
        image_result = cam.GetNextImage(1000)
        if image_result.IsIncomplete():
                    print('Image incomplete with image status %d ...' % image_result.GetImageStatus())

        else:
            width = image_result.GetWidth()
            height = image_result.GetHeight()
            print('Grabbed Image %d, width = %d, height = %d' % (i, width, height))

        image_converted = processor.Convert(image_result, PySpin.PixelFormat_Mono8)
        if device_serial_number:
         filename = 'Acquisition-%s-%d.jpg' % (device_serial_number, i)
        else:  # if serial number is empty
         filename = 'Acquisition-%d.jpg' % i

        image_converted.Save(filename)
        print('Image saved at %s' % filename)
        image_result.Release()
     cam.EndAcquisition()





    
     
     
    
    def capture(self,cam,nodemap,nodemap_tldevice):
       cam.BeginAcquisition()
       image =cam.GetNextImage(1010)
       cam.EndAcquisition()
       return image
    
    def save(self,image,imageProcessor,itter):
     if image.IsIncomplete():
      print("Incomplete Image")
      exit()
     image_converted =imageProcessor.Convert(image, PySpin.PixelFormat_Mono8)
     filename = 'Acquisition-%d.jpg' % itter 
     image_converted.Save(filename)
     image.Release()
    
    def takeSnapshot(self):
         self.initializeCamera()
         
     
        


        
         cam.DeInit()          


obj =FlirCam()
#cmaParaObj = FlirCamParam()
obj.takeSnapshot()

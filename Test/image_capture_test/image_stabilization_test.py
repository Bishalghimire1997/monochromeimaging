import cv2
from h5_file_format_package.h5_format_read import ReadH5
from h5_file_format_package.h5_format import H5Fromat
from image_processing_package.processing_routines import Processing
from image_processing_package.detect_changed_object import DetectChanges 
import multiprocessing
from image_processing_package.tracking import Track

def inaitial_analysis():
    """initial test case"""
    obj2 = ReadH5()
    blue1 = obj2.read_files("image.h5","60")
    green = obj2.read_files("image.h5","61")
    red = obj2.read_files("image.h5","62")
    Processing.open_images(Processing.image_reconstruction(blue1,green,red),'reconstrucrted')
    obj = DetectChanges()
    obj1 = DetectChanges()
    roi,_= obj1.select_and_crop_roi(blue1)
    param=obj.check_for_match_second(roi,blue1,green)
    green= obj.transform(green,param[0],param[1],param[4])
    param= obj1.check_for_match_second(roi, blue1,red)
    red= obj.transform(red,param[0],param[1],param[4])
    Processing.open_images(Processing.image_reconstruction(blue1,green,red),"after transformation ")
    blue2 = obj2.read_files("image.h5","63")
    green = obj2.read_files("image.h5","64")
    red = obj2.read_files("image.h5","65")
    roi = DetectChanges.updateRoi(roi,blue1,blue2)
    print(roi)
    param=obj.check_for_match_second(roi,blue2,green)
    green= obj.transform(green,param[0],param[1],param[4])
    param= obj1.check_for_match_second(roi, blue2,red)
    red= obj.transform(red,param[0],param[1],param[4])
    Processing.open_images(Processing.image_reconstruction(blue2,green,red),"after transformation ")
def loop():      
    read_imaegs = ReadH5()
    saveblue= H5Fromat("blue1")
    savegreen = H5Fromat("green1")
    savered = H5Fromat("red1")
    save_roi = H5Fromat("ROI")
    var=601
    dec_ch = DetectChanges()
    blue = read_imaegs.read_files("image.h5",str(var))
    roi,_ = dec_ch.select_and_crop_roi(blue)
    roib=roi
    roig=False
    roir =False
    tr=Track("MIL")
    tr.start_tracking(blue,roi)
    for i in range(100):
        b = str(var)
        g = str(var+1)
        r= str (var+2)
        var=var+3     
        green = read_imaegs.read_files("image.h5",g)
        red = read_imaegs.read_files("image.h5",r)
        blue = read_imaegs.read_files("image.h5",b)
        if i!= 0:
            _,roib = tr.update_tracking(blue)
            _,roig = tr.update_tracking(green)
            _,roir = tr.update_tracking(red)
            print(roig,roig,roir)
        """Using multi processing"""
        with multiprocessing.Pool(processes=3) as pool:
            result = pool.starmap(DetectChanges.temp,[(blue,roib),(green,roig),(red,roir)])           
        kp1,blue_image_descriptor  = result[0] #DetectChanges.temp(blue,roi)
        kp2,green_image_descriptor  = result[1] #DetectChanges.temp(green,False)
        kp3,red_image_descriptor  = result[2] #DetectChanges.temp(red,False)       

        """Deserializing the keypoints"""
        blue_image_key_points = [cv2.KeyPoint(x[0], x[1], x[2], x[3], x[4], x[5], x[6]) for x in kp1]
        green_image_key_points = [cv2.KeyPoint(x[0], x[1], x[2], x[3], x[4], x[5], x[6]) for x in kp2]
        red_image_key_points = [cv2.KeyPoint(x[0], x[1], x[2], x[3], x[4], x[5], x[6]) for x in kp3]
        param=dec_ch.check_for_match_second(blue_image_descriptor,blue_image_key_points,green_image_descriptor,green_image_key_points)
        green= dec_ch.transform(green,param[0],param[1],param[4])
        param= dec_ch.check_for_match_second(blue_image_descriptor,blue_image_key_points,red_image_descriptor,red_image_key_points)
        red= dec_ch.transform(red,param[0],param[1],param[4])
        saveblue.record_images(blue,str(i))
        savegreen.record_images(green,str(i))
        savered.record_images(red,str(i))
        save_roi.record_images(roib,str(i))
def play_images_as_video( fps=20.0):
    """" Plays the corrected frams as a video"""
    obj2 = ReadH5()
    imagetransformed=[]
    for i in range(90):
        b= obj2.read_files("blue1.h5",str(i))
        g= obj2.read_files("green1.h5",str(i+1))
        r=obj2.read_files("red1.h5",str(i+1))

        imagetransformed.append(Processing.image_reconstruction(b,g,r))
                                                                
    delay = int(1000 / fps)

    for image in imagetransformed:
        cv2.imshow('Image Stream', image)
        if cv2.waitKey(delay) & 0xFF == ord('q'):
            print("Playback interrupted.")
            break
    cv2.destroyAllWindows()

def correct_background():
    """Corects the background after transformation """
    blue_o=[]
    green_o=[]
    red_o=[]
    blue_t=[]
    green_t=[]
    red_t=[]
    roi= []
    read_imaegs = ReadH5()
    var=0
    for i in range(300):
        b = str(var)
        g = str(var+1)
        r= str (var+2)
        blue_o.append(read_imaegs.read_files("image.h5",b))
        green_o.append(read_imaegs.read_files("image.h5",g))
        red_o.append(read_imaegs.read_files("image.h5",r))
        blue_t.append(read_imaegs.read_files("blue.h5",str(i)))
        green_t.append(read_imaegs.read_files("green.h5",str(i)))
        red_t.append(read_imaegs.read_files("red.h5",str(i)))
        roi.append(read_imaegs.read_files("ROI.h5",str(i)))
        var=var+3
    print(roi[0])
    DetectChanges.reconstruct_background(blue_t,red_t,green_t,blue_o,green_o,red_o,roi)
if __name__ == '__main__':
    loop()

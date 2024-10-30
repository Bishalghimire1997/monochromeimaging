from h5_file_format_package.h5_format_read import ReadH5
from image_processing_package.processing_routines import Processing
from image_processing_package.detect_changed_object import DetectChanges 

def inaitial_analysis():
    obj2 = ReadH5()
    blue1 = obj2.read_files("image.h5","45")
    green = obj2.read_files("image.h5","46")
    red = obj2.read_files("image.h5","47")
    Processing.open_images(Processing.image_reconstruction(blue1,green,red),'reconstrucrted')
    obj = DetectChanges()
    obj1 = DetectChanges()
   # Processing.open_images(obj.get_mask())
    roi,crop = obj1.select_and_crop_roi(blue1)
    param=obj.check_for_match_second(roi,blue1,green)
    green= obj.transform(green,param[0],param[1],param[4])

    param= obj1.check_for_match_second(roi, blue1,red)
    red= obj.transform(red,param[0],param[1],param[4])
    Processing.open_images(Processing.image_reconstruction(blue1,green,red),"after transformation ")

    blue2 = obj2.read_files("image.h5","48")
    green = obj2.read_files("image.h5","49")
    red = obj2.read_files("image.h5","50")
    roi = DetectChanges.updateRoi(roi,blue1,blue2)
    print(roi)
    param=obj.check_for_match_second(roi,blue2,green)
    green= obj.transform(green,param[0],param[1],param[4])
    param= obj1.check_for_match_second(roi, blue2,red)
    red= obj.transform(red,param[0],param[1],param[4])
    Processing.open_images(Processing.image_reconstruction(blue2,green,red),"after transformation ")

def loop():
    read_imaegs = ReadH5()
    track =DetectChanges()
    blue = read_imaegs.read_files("image.h5","45")
    blue_old = read_imaegs.read_files("image.h5","48")
    roi,crop = track.select_and_crop_roi(blue)
    x,y,w,h =roi
    var=45
    for i in range(50): 
        b = str(var)
        g = str(var+1)

        r= str (var+2)
        var=var+3
        
        blue = read_imaegs.read_files("image.h5",b)
        if(i!=0):
            print(roi)
            _,y,_,_ =track.updateRoi(roi,blue_old,blue)
            roi = x,y,w,h
            print(roi)
       
       
        
        green = read_imaegs.read_files("image.h5",g)
        red = read_imaegs.read_files("image.h5",r)

        param=track.check_for_match_second(roi,blue,green)
        green= track.transform(green,param[0],param[1],param[4])
        param= track.check_for_match_second(roi, blue,red)
        red= track.transform(red,param[0],param[1],param[4])
        Processing.open_images(Processing.image_reconstruction(blue,green,red),"after transformation ")
        blue_old=blue


        


loop()
from h5_file_format_package.h5_format import H5FormatRead
from h5_file_format_package.h5_format import H5FromatWrite
from image_processing_package.detect_changed_object import DetectChanges
def run_test():
    var=0
    read_imaegs = H5FormatRead()
    dc = DetectChanges()
    result = None 
    saveblue= H5FromatWrite("blue1",override=False)
    savegreen = H5FromatWrite("green1",override=False)
    savered = H5FromatWrite("red1",override=False)
    for i in range(100):
        
        b = str(var)
        g = str(var+1)
        r= str (var+2)
        var=var+3
        
        green = read_imaegs.read_files("image.h5",g)
        red = read_imaegs.read_files("image.h5",r)
        blue = read_imaegs.read_files("image.h5",b)
        if i ==0:
             result = DetectChanges.update_keypoints([blue,green,red],detector_type="SIFT")
             image = [blue,green,red]
        else:
            image,result = dc.run([blue,green,red],i,result)
        saveblue.record_images(image[0],str(i))
        savegreen.record_images(image[1],str(i))
        savered.record_images(image[2],str(i))
if __name__ == "__main__":
    run_test()

        
 
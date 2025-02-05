"""module to save the images in .h5 file format
"""
import numpy as np
import cv2
from h5py import File
class H5FromatWrite():
    """
    class to save the images in .h5 file format
    """  
    def __init__(self,file_name,override:bool):
        self._override = override
        self._filename =file_name
        self._image = File(self._filename+".h5","w", libver='latest')
        self._image.swmr_mode = True
        if not self._override:
            self._image=File(self._filename +".h5","r+")          

    def record_images(self,image,itter) :
        """_summary_ saves the images in h5 file format

        Args:
            image (numpy array): Image captured by camera
            itter (int): the key to the image
        """
        self._image.create_dataset(str(itter),data=image)

    def get_multi_itter_obj(self):
        return self._image
    
    def record_images_multi(self,image,itter,f) :
        """_summary_ saves the images in h5 file format

        Args:
            image (numpy array): Image captured by camera
            itter (int): the key to the image
        """ 
        image_converted = image.GetNDArray()
        f.create_dataset(str(itter),data=image_converted)

class H5FormatRead():
    @staticmethod
    def read_files(path:str,index:str):
        """provided the path, reada the h5 format files
        Args:
        path (str): path to the file 
        Returns:
            _type_: _description_
        """        
        with File(path, 'r') as h5_file:
            image = np.array(h5_file[index])
        return image   
    @staticmethod
    def get_multi_read_obj(path:str):
         file =  File(path, 'r',swmr=True) 
         return   file
       
    @staticmethod
    def pop_first(path:str,index:str):         
         with File(path, 'r',swmr=True) as h5_file:
                 image = np.array(h5_file.pop(index))
         return image 
    @staticmethod
    def read_image_multi(index:str,f):
        image = np.array(f[index])
        return image
    @staticmethod
    def open_images( image):
        """displys the numpy array as image
        Args:
            image (np.Arrayterator): numpy array
        """
        cv2.imshow("image",image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        

        

   

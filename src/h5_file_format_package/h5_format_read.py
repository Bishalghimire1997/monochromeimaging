from h5py import File
import numpy as np
import cv2
class ReadH5():
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
    def open_images( image):
        """displys the numpy array as image
        Args:
            image (np.Arrayterator): numpy array
        """
        cv2.imshow("image",image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
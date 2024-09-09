"""module to save the images in .h5 file format
"""
from h5py import File

class H5Fromat():
    """
    class to save the images in .h5 file format
    """    
    def __init__(self,file_name):
        self._image = File(file_name+".h5","w")
        self._filename =file_name


    def record_images(self,image, itter) : 
        """_summary_ saves the images in h5 file format

        Args:
            image (numpy array): Image captured by camera
            itter (int): the key to the image
        """              
        self._image=File(str(itter),self._filename +".h5","r+")
        self._image.create_dataset(str(itter),data=image)

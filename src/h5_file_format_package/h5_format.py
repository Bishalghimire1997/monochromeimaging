"""module to save the images in .h5 file format
"""
from h5py import File
class H5Fromat():
    """
    class to save the images in .h5 file format
    """    
    def __init__(self,file_name,override:bool):
        self._override = override
        self._filename =file_name
        self._image = File(self._filename+".h5","w")
        if not self._override:
            self._image=File(self._filename +".h5","r+")          

    def record_images(self,image,itter) :
        """_summary_ saves the images in h5 file format

        Args:
            image (numpy array): Image captured by camera
            itter (int): the key to the image
        """            
        self._image.create_dataset(str(itter),data=image)
    def record_images_multi(self,image,itter) :
        """_summary_ saves the images in h5 file format

        Args:
            image (numpy array): Image captured by camera
            itter (int): the key to the image
        """ 
        self._image.create_dataset(str(itter),data=image)

        

   

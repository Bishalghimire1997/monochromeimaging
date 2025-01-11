from h5py import File
from mpi4py import MPI
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
    def pop_first(path:str,index:str,lock):         
         with File(path, 'r',swmr=True) as h5_file:
                 image = np.array(h5_file.pop(index))
         return image 
    @staticmethod
    def read_image_multi(path:str,index:str):
          with File(path, 'r',swmr=True) as h5_file:
                image = np.array(h5_file[index])
                h5_file.close()
          return image
    @staticmethod
    def read_image_multi_parallel(path: str, index: str, comm: MPI.Comm):
        """Reads an image dataset in parallel, assuming a shared dataset with rows split.
        
        Args:
            path (str): Path to the HDF5 file.
            index (str): Dataset index/key to read.
            comm (MPI.Comm): MPI communicator.

        Returns:
            np.ndarray: The portion of the dataset read by the current rank.
        """
        rank = comm.Get_rank()
        size = comm.Get_size()

        with File(path, 'r', driver='mpio', comm=comm) as h5_file:
            dataset = h5_file[index]
            height, width = dataset.shape[0], dataset.shape[1]
            chunk_size = height // size
            start = rank * chunk_size
            end = start + chunk_size if rank != size - 1 else height

            # Read rows assigned to the current rank
            image_chunk = np.array(dataset[start:end, :])
        return image_chunk
    @staticmethod
    def open_images( image):
        """displys the numpy array as image
        Args:
            image (np.Arrayterator): numpy array
        """
        cv2.imshow("image",image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
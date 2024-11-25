from data_visualization_packege.visualize import Visualize
from h5_file_format_package.h5_format_read import ReadH5
import numpy as np
from image_processing_package.processing_routines import Processing
def image_vis():
    """initial test case"""
    obj2 = ReadH5()
    blue1 = obj2.read_files("image.h5","102")
    green = obj2.read_files("image.h5","103")
    red = obj2.read_files("image.h5","104")
    image = Processing.image_reconstruction(blue1,green,red)
    vis = Visualize()
    vis.plot_3d_interactive(image)

def ratio ():
    from matplotlib import pyplot as plt 
    obj2 = ReadH5()
    blue = obj2.read_files("image.h5","102")
    green = obj2.read_files("image.h5","103")
    red = obj2.read_files("image.h5","104")
    b_g = elementwise_divide(blue,red)
    plt.plot(b_g.flatten())
    plt.show()

def elementwise_multiply(arr1, arr2):
    """
    Performs element-wise multiplication of two arrays.

    Parameters:
    arr1 (numpy.ndarray): The first input array.
    arr2 (numpy.ndarray): The second input array.

    Returns:
    numpy.ndarray: The element-wise multiplication of arr1 and arr2.
    """
    return arr1 * arr2

def elementwise_divide(arr1, arr2):
    """
    Performs element-wise division of two arrays, handling division by zero.

    Parameters:
    arr1 (numpy.ndarray): The first input array (numerator).
    arr2 (numpy.ndarray): The second input array (denominator).

    Returns:
    numpy.ndarray: The element-wise division of arr1 by arr2. Division by zero
                   is handled by setting those results to np.nan.
    """
    # Use np.where to handle division by zero
    result = np.where(arr2 != 0, arr1 / arr2, 1)
    return result
image_vis()


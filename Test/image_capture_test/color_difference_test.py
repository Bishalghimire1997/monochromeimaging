
from processing_using_raft.evaluation import Evaluation
from h5_file_format_package.h5_format import H5FormatRead
import numpy as np
import cv2
from matplotlib import pyplot as plt

def error_heatmap(image1: np.ndarray, image2: np.ndarray, show: bool = True, colormap='hot',color_diff_map = False) -> np.ndarray:
    """
    Compute a pixel-wise error heatmap between two images.

    Args:
        image1 (np.ndarray): First image (H,W) or (H,W,C)
        image2 (np.ndarray): Second image, same shape as image1
        show (bool): Whether to display the heatmap
        colormap (str): Matplotlib colormap to use

    Returns:
        np.ndarray: Normalized error heatmap (values 0-1)
    """
    # Convert to float to avoid overflow
    cd=Evaluation()
    img1 = image1.astype(np.float32)
    img2 = image2.astype(np.float32)

    # Compute squared error
    if img1.ndim == 3:  # Color image
        error = np.mean((img1 - img2) ** 2, axis=2)
    else:  # Grayscale
        error = (img1 - img2) ** 2
 
    print("Max Error = ",np.max(error))
    if color_diff_map == True:
         val = cd.compute_del_e([img1],[img2])
         error = val

    # Normalize to 0-1
    heatmap = error #/ np.max(error) if np.max(error) > 0 else error

    # Display
    if show:
        plt.imshow(np.sqrt(heatmap), cmap=colormap)
        plt.colorbar(label='Root Squared Error')
        plt.title("Error Heatmap")
        plt.show()

        plt.figure()
        plt.hist(np.sqrt(heatmap.flatten()), bins=255)
        plt.title("Median Error: %f DN" % np.median(np.sqrt(heatmap.flatten())))
        plt.show()

    return heatmap
def run():
    path = "image.h5"
    cd=Evaluation()
    b = H5FormatRead().read_files(path,"30")
    g = H5FormatRead().read_files(path,"31")
    r = H5FormatRead().read_files(path,"2")
    print("###################",b.shape)
    reb = cv2.resize(b.copy(),(900,900))
    reg = cv2.resize(g.copy(),(900,900),interpolation=cv2.INTER_LINEAR)
    cv2.imshow("b",reb)
    cv2.imshow("g",reg)
    cv2.waitKey(0) 
    cv2.destroyAllWindows()
    ref = []
    targ = []
    for i in range(10):
        ref.append(H5FormatRead().read_files(path,str(15+i)))
        targ.append(H5FormatRead().read_files(path,str(16+i)))

        
    val = cd.compute_del_e_new(np.array(ref),np.array(targ))
    print("This is the final delta E =   ",val, "MSE = ",np.mean((b.astype(np.float32) - g.astype(np.float32)) ** 2))
    error_heatmap(b,g)

run()

from matplotlib import pyplot as plt
import numpy as np
class Visualize():
    def __init__(self):
        pass
    def plot_channels(self,image):
        """Generates plots between different channels pixel values

        Args:
            image (numpy array): Color image
        """        
        r = image[:,:,0]
        g = image[:,:,1]
        b = image[:,:,2]
        r=r.flatten()
        g=g.flatten()
        b=b.flatten()
        # Create a figure and axes
        fig, axs = plt.subplots(1, 3, figsize=(15, 5))  # 1 row, 3 columns

        # Scatter plot for R vs G
        axs[0].scatter(r, g, s=1, alpha=0.5)  # s controls marker size, alpha controls transparency
        axs[0].set_xlabel("Red")
        axs[0].set_ylabel("Green")
        axs[0].set_title("Red vs Green")

        # Scatter plot for R vs B
        axs[1].scatter(r, b, s=1, alpha=0.5)
        axs[1].set_xlabel("Red")
        axs[1].set_ylabel("Blue")
        axs[1].set_title("Red vs Blue")

        # Scatter plot for G vs B
        axs[2].scatter(g, b, s=1, alpha=0.5)
        axs[2].set_xlabel("Green")
        axs[2].set_ylabel("Blue")
        axs[2].set_title("Green vs Blue")

        # Adjust layout to prevent overlapping
        plt.tight_layout()
        plt.show()
    def plot_3d_interactive (self,image):
        r = image[:,:,0].flatten()
        g = image[:,:,1].flatten()
        b = image[:,:,2].flatten()

        # Create a figure and 3D axis
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')

        # Create a scatter plot
        scatter = ax.scatter(r, g, b, c=np.stack([r, g, b], axis=1)/255.0, s=1, alpha=0.5)

        # Set axis labels
        ax.set_xlabel("Red")
        ax.set_ylabel("Green")
        ax.set_zlabel("Blue")
        ax.set_title("Interactive 3D Scatter Plot: Red vs Green vs Blue")

        # Show the plot interactively
        plt.show()

    # Call the function with your image
    # plot_3d_interactive(image)



import cv2
from image_processing_package.tracking import Track
from image_processing_package.detect_changed_object import DetectChanges
from image_processing_package.processing_routines import Processing
from h5_file_format_package.h5_format_read import ReadH5

class TrackerrImpl():
    def __init__(self):
        self.trackers_list = ['MIL','KCF','CSRT']
        self.trackers_object_list=[]
        for i in self.trackers_list:
            self.trackers_object_list.append(Track(i))
    def track(self):   
        read_imaegs = ReadH5()
        var=60
        frame = read_imaegs.read_files("image.h5",str(var))
        roi,_ = DetectChanges.select_and_crop_roi(frame) 
        x,y,w,h=roi

        frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)        
        for tr in self.trackers_object_list:
            
            tr.start_tracking(frame,roi)

    
        for i in range(50): 
            bounding_box = []
            success_list=[]

            frame=  read_imaegs.read_files("image.h5",str(i+var))
            frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)   

           
            print(bounding_box)
            suc=False
            for i in success_list:
                suc= suc+i
            if (suc):
                x, y, w,h  = [int(v) for v in self.select_best_roi(self.trackers_list,success_list,bounding_box)]
            image=frame.copy()
            for bbox, algorithm in zip(bounding_box, self.trackers_list):
               image= self.draw_bounding_box(image,bbox,algorithm)       
            Processing.open_images(image,"frame")    
            frame=  read_imaegs.read_files("image.h5",str(i+var))
            roi = x,y,w,h
        cv2.destroyAllWindows()
        
    def select_best_roi(self,trackers_list, success_list, roi_list):
        priority_order = {'CSRT': 0, 'MIL': 1, 'KCF': 2}
        sorted_trackers = sorted(range(len(trackers_list)), key=lambda i: priority_order[trackers_list[i]])
        for idx in sorted_trackers:
            if success_list[idx]:  # If tracker succeeded
                return roi_list[idx]        
        return []
    
    def draw_bounding_box(self,image, bbox, algorithm):
        """
        Draws a bounding box with a specific color for each tracking algorithm and labels it.
        
        Args:
            image (ndarray): The image on which to draw.
            bbox (tuple): The bounding box coordinates as (x, y, width, height).
            algorithm (str): The name of the tracking algorithm.
        """
        colors = {'BOOSTING': (255, 0, 0),  # Red
    'MIL': (0, 255, 0),       # Green
    'KCF': (0, 0, 255),       # Blue
    'TLD': (255, 255, 0),     # Cyan
    'CSRT': (255, 0, 255),    # Magenta
    'MEDIANFLOW': (0, 255, 255),  # Yellow
    'MOSSE': (128, 128, 128) } # Gray
        # Set color based on the algorithm
        color = colors.get(algorithm, (255, 255, 255))  # Default to white if not in colors
        
        # Unpack bbox coordinates
        x, y, width, height = bbox
        
        # Draw rectangle
        start_point = (int(x), int(y))
        end_point = (int(x + width), int(y + height))
        cv2.rectangle(image, start_point, end_point, color, 2)
        
        # Draw text label
        label = f"{algorithm}"
        cv2.putText(image, label, (int(x), int(y) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        return image

obj= TrackerrImpl()
obj.track()



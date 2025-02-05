import cv2
class Track:
    def __init__(self, tracker_type):
        self.tracker_type = tracker_type
        self.tracker = self.create_tracker()

    def create_tracker(self):
        if self.tracker_type == 'BOOSTING':
            return cv2.legacy.TrackerBoosting_create()
        elif self.tracker_type == 'MIL':
            return cv2.TrackerMIL_create()
        elif self.tracker_type == 'KCF':
            return cv2.TrackerKCF_create()
        elif self.tracker_type == 'TLD':
            return cv2.legacy.TrackerTLD_create()
        elif self.tracker_type == 'MEDIANFLOW':
            return cv2.legacy.TrackerMedianFlow_create()
        elif self.tracker_type == 'GOTURN':
            return cv2.TrackerGOTURN_create()
        elif self.tracker_type == 'MOSSE':
            return cv2.legacy.TrackerMOSSE_create()
        elif self.tracker_type == 'CSRT':
            return cv2.TrackerCSRT_create()
        else:
            raise ValueError("Invalid tracker type")

    def start_tracking(self, frame, bounding_box):
        self.tracker.init(frame, bounding_box)

    def __update_tracking(self, frame):
        success, bbox = self.tracker.update(frame)
        return success, bbox
    def update_roi(self,frame:list):
        roi=[]
        for i in frame:
            roi.append(self.__update_tracking(i)[1])
        return roi




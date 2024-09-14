from cv2 import VideoCapture, 
import json
from pupil_apriltags import Detector
import time
import math
# import pyb
import numpy as np
# xStopPin = pyb.Pin("P0", pyb.Pin.OUT_PP)
# yStopPin = pyb.Pin("P1", pyb.Pin.OUT_PP)
# blue = pyb.LED(3)

# Conversion from pixel to cm 
cm2px = 30
tolerance = 30 # 30 px, 1cm
# 300 X 
at_detector = Detector(
    families="tag36h11",
    nthreads=1,
    quad_decimate=1,
    quad_sigma=0,
    refine_edges=1,
    decode_sharpening=0.25,
    debug=0
)
gridByRow = [
    [18, 12, 6, 0],
    [19, 13, 7, 1],
    [20, 14, 8, 2],
    [21, 15, 9, 3],
    [22, 16, 10, 4],
    [23, 17, 11, 5]
]

xStop = [0, 1,2,3,4,5]

gridByColumn = [
    [23, 22, 21, 20, 19, 18],
    [17, 16, 15, 14, 13, 12],
    [11, 10, 9, 8, 7, 6],
    [5,4,3,2,1,0]
    ]

yStop = [18,12,6,0]


fx = 0
cx = 0
fy = 0
cy = 0
k1 = 0
k2 = 0
p1 = 0
p2 = 0
k3 = 0
xMax = 640
yMax = 480
xMin = 0
yMin = 0
centerX = int(xMin + (xMax - xMin)/2)
centerY = int(yMin + (yMax - yMin)/2)

# Load the calibration parameters
# These would normally be obtained from a calibration process
camera_matrix = np.array([[fx, 0, cx], [0, fy, cy], [0, 0, 1]])
dist_coeffs = np.array([k1, k2, p1, p2, k3])

class CameraStream:
    def __init__(self, camera_index=0):
        # Initialize the camera capture object
        self.cap = cv2.VideoCapture(camera_index)
        self.aprilTags = {}
        self.xStop = []
        self.yStop = []
        self.camera_matrix = camera_matrix
        self.dist_coeffs = dist_coeffs
        if not self.cap.isOpened():
            print(f"Error: Unable to open camera {camera_index}")
            raise Exception("Camera not accessible")

    def start_stream(self):
        print("Starting camera stream...")
        # Continuously read frames from the camera and display them
        # while True:
        self.apriltagDetect()
        # ret, frame = self.cap.read()  # Capture frame-by-frame
        # print(frame)
        # if not ret:
        #     print("Error: Unable to read from camera")
        #     break

        #cv2.imshow('Camera Stream', frame)  # Display the resulting frame

        # # Break the loop if 'q' is pressed
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break

    def stop_stream(self):
        # Release the camera and close the windows
        self.cap.release()
        cv2.destroyAllWindows()
        print("Camera stream stopped")

    def apriltagDetect(self):
        while True:


            
            # Capture frame-by-frame
            ret, frame = self.cap.read()

            # Draw the corner boxes & center box            
            cv2.line(frame, (xMin + 30, yMin + 30), (xMin + 30,yMin), (0, 255, 255), 2)
            cv2.line(frame, (xMin + 30, yMin), (xMin,yMin), (0, 255, 255), 2)
            cv2.line(frame, (xMin, yMin), (xMin,yMin+30), (0, 255, 255), 2)
            cv2.line(frame, (xMin, yMin+30), (xMin+30,yMin+30), (0, 255, 255), 2)
            
            cv2.line(frame, (xMax, yMin), (xMax,yMin+30), (0, 255, 255), 2)
            cv2.line(frame, (xMax, yMin+30), (xMax-30,yMin+30), (0, 255, 255), 2)
            cv2.line(frame, (xMax-30, yMin+30), (xMax-30,yMin), (0, 255, 255), 2)
            cv2.line(frame, (xMax-30, yMin), (xMax,yMin), (0, 255, 255), 2)


            cv2.line(frame, (xMax - 30, yMax - 30), (xMax - 30,yMax), (0, 255, 255), 2)
            cv2.line(frame, (xMax - 30, yMax), (xMax,yMax), (0, 255, 255), 2)
            cv2.line(frame, (xMax, yMax), (xMax,yMax-30), (0, 255, 255), 2)
            cv2.line(frame, (xMax, yMax-30), (xMax-30,yMax-30), (0, 255, 255), 2)
            
            cv2.line(frame, (xMin, yMax), (xMin,yMax-30), (0, 255, 255), 2)
            cv2.line(frame, (xMin, yMax-30), (xMin+30,yMax-30), (0, 255, 255), 2)
            cv2.line(frame, (xMin+30, yMax-30), (xMin+30,yMax), (0, 255, 255), 2)
            cv2.line(frame, (xMin+30, yMax), (xMin,yMax), (0, 255, 255), 2)


            cv2.line(frame, (xMin, yMax), (xMin,yMax-30), (0, 255, 255), 2)
            cv2.line(frame, (xMin, yMax-30), (xMin+30,yMax-30), (0, 255, 255), 2)
            cv2.line(frame, (xMin+30, yMax-30), (xMin+30,yMax), (0, 255, 255), 2)
            cv2.line(frame, (xMin+30, yMax), (xMin,yMax), (0, 255, 255), 2)

            cv2.line(frame, (centerX-15, centerY-15), (centerX-15,centerY+15), (0, 255, 0), 2)
            cv2.line(frame, (centerX-15, centerY+15), (centerX+15,centerY+15), (0, 255, 0), 2)
            cv2.line(frame, (centerX+15, centerY+15), (centerX+15,centerY-15), (0, 255, 0), 2)
            cv2.line(frame, (centerX+15, centerY-15), (centerX-15,centerY-15), (0, 255, 0), 2)


            
            if not ret:
                break

            # Convert the frame to grayscale (AprilTags detection works best on grayscale images)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # print(type(gray))
            # cv2.imshow("GrayScale", gray)

            # Detect AprilTags in the image
            # results, t_vec, r_vec = at_detector.detect(gray, True)
            results = at_detector.detect(gray)
            # Loop over the AprilTag detection results
            for r in results:

                # Extract the bounding box (the four corners of the tag) for the AprilTag
                (ptA, ptB, ptC, ptD) = r.corners
                ptA = (int(ptA[0]), int(ptA[1]))
                ptB = (int(ptB[0]), int(ptB[1]))
                ptC = (int(ptC[0]), int(ptC[1]))
                ptD = (int(ptD[0]), int(ptD[1]))

                # Draw the bounding box of the AprilTag detection
                cv2.line(frame, ptA, ptB, (0, 255, 0), 2)
                cv2.line(frame, ptB, ptC, (0, 255, 0), 2)
                cv2.line(frame, ptC, ptD, (0, 255, 0), 2)
                cv2.line(frame, ptD, ptA, (0, 255, 0), 2)

                # Draw the center of the tag
                (cX, cY) = (int(r.center[0]), int(r.center[1]))
                cv2.circle(frame, (cX, cY), 5, (0, 0, 255), -1)

                # Print the tag family and ID
                tagID = r.tag_id
                xStopID = self.findStop(tagID, gridByRow, xStop)
                if xStopID not in self.xStop:
                    self.xStop.append(xStopID)
                yStopID = self.findStop(tagID, gridByColumn, yStop)
                if yStopID not in self.yStop:
                    self.yStop.append(yStopID)
                cv2.putText(frame, f"Tag ID: {tagID}", (ptA[0], ptA[1] - 15),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                aprilTag = {
                    'tagID': tagID,
                    'x': cX,
                    'y': cY,
                    'time': time.time()
                }
                # print(centerX)
                # print(centerY)
                # print(cX)
                # print(centerX -15)
                # print(centerX - 15 < cX)
                # print((centerX - 15 < cX and cX < centerX + 15))
                if tagID in self.xStop:
                    # xStopPin.high()
                    # pyb.LED.on(blue)
                    print("X stop")
                if tagID in self.yStop:
                    print("Y stop")
                    # yStopPin.high()
                    # pyb.LED.off(blue)
                # if((centerX - 15 < cX and cX < centerX + 15) and (centerY - 15 < cY and cY < centerY + 15)):
                #     print("All Stop !")
                #     print(cX)
                #     print(cY)
                # else:
                #     if(centerX - 15 < cX and cX < centerX + 15):
                #         print("Stop X!")
                #         print(cX)
                #     if(centerY - 15 < cY and cY < centerY + 15):
                #         print("Stop Y!")
                #         print(cY)
                # if(tagID == 73):
                #     stopPin.high()
                #     pyb.LED.on(blue)
                # if(tagID == 72):
                #     stopPin.low()
                #     pyb.LED.off(blue)
                #pself.aprilTags[aprilTag['time']] = aprilTag
                break
            # Display the resulting frame
            cv2.imshow("AprilTag Detection", frame)
            # Exit the loop when 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    #Function to add the Stop to the Stop list. 
    def findStop(self, tagID, gridList, stopList):
        for i, sublist in enumerate(gridList):
            if tagID in sublist:
                print(f"Found {tagID} in stop is {stopList[i]}")
                # Use the index `i` to get a value from another list
                result = stopList[i]
                return result
        return None  # Return None if the target is not found in any sublist


# Example usage:
if __name__ == "__camera__":
    stream = CameraStream(camera_index=0)  # 0 is the default camera index
    try:
        stream.start_stream()
    finally:
        stream.stop_stream()

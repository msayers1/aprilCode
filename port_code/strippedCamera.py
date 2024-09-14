from cv2 import VideoCapture, cvtColor, COLOR_BGR2GRAY
import json
from pupil_apriltags import Detector
import time
import math
import RPi.GPIO as GPIO
import numpy as np

# Sample Instantion and use. 
#
#
# # Create an instance of the CameraStream class
# camera_stream = CameraStream(camera_index=0)  # Use 0 for the default camera
#
# try:
#     # Start the camera stream
#     camera_stream.start_stream()
#     #print(camera_stream.aprilTags)
# except Exception as e:
#     print(f"An error occurred: {e}")
# finally:
#     # Stop the camera stream and release resources
#     camera_stream.stop_stream()

# Y stop
# GPIO 16
# X Stop 
# GPIO 26
GPIO.setmode(GPIO.BCM)  # Use BCM pin numbering
xStopPin = 26                # Define the pin number you want to use (change as needed)
GPIO.setup(xStopPin, GPIO.OUT)
yStopPin = 16                # Define the pin number you want to use (change as needed)
GPIO.setup(yStopPin, GPIO.OUT)


# April Tag Detector
at_detector = Detector(
    families="tag36h11",
    nthreads=1,
    quad_decimate=1,
    quad_sigma=0,
    refine_edges=1,
    decode_sharpening=0.25,
    debug=0
)
#April Tags
gridByRow = [
    [18, 12, 6, 0],
    [19, 13, 7, 1],
    [20, 14, 8, 2],
    [21, 15, 9, 3],
    [22, 16, 10, 4],
    [23, 17, 11, 5]
]

# X Stops
xStop = [0, 1,2,3,4,5]

# April Tags
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

class CameraStream:
    def __init__(self, camera_index=0):
        # Initialize the camera capture object
        self.cap = VideoCapture(camera_index)
        self.aprilTags = {}
        self.xStop = []
        self.yStop = []
        self.TagInFrame = False
        if not self.cap.isOpened():
            print(f"Error: Unable to open camera {camera_index}")
            raise Exception("Camera not accessible")

    def start_stream(self):
        print("Starting camera stream...")
        self.apriltagDetect()

    def stop_stream(self):
        self.cap.release()
        print("Camera stream stopped")

    def apriltagDetect(self):
        while True:
            print(f"Tag in Frame:{self.TagInFrame}")
            # Capture frame-by-frame
            ret, frame = self.cap.read()
            if not ret:
                break
            # Convert the frame to grayscale (AprilTags detection works best on grayscale images)
            gray = cvtColor(frame, COLOR_BGR2GRAY)
            results = at_detector.detect(gray)
            if len(results) == 0:
                self.TagInFrame = False
            # Loop over the AprilTag detection results
            for r in results:
                tagID = r.tag_id
                self.TagInFrame = True
                xStopID = self.findStop(tagID, gridByRow, xStop)
                if xStopID not in self.xStop:
                    self.xStop.append(xStopID)
                yStopID = self.findStop(tagID, gridByColumn, yStop)
                if yStopID not in self.yStop:
                    self.yStop.append(yStopID)
                if tagID in self.xStop:
                    print("X stop")
                    GPIO.output(xStopPin, GPIO.HIGH)
                    print(f"Pin {xStopPin} is now HIGH.")
                if tagID in self.yStop:
                    print("Y stop")
                    GPIO.output(yStopPin, GPIO.HIGH)
                    print(f"Pin {xStopPin} is now HIGH.")
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
        print('Starting stream')
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Stop the camera stream and release resources
        stream.stop_stream()
        print('Stopping stream')

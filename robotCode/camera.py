import cv2
import json
from pupil_apriltags import Detector
import time
import pyb
import numpy as np
stopPin = pyb.Pin("P0", pyb.Pin.OUT_PP)
blue = pyb.LED(3)


at_detector = Detector(
    families="tag36h11",
    nthreads=1,
    quad_decimate=1,
    quad_sigma=0,
    refine_edges=1,
    decode_sharpening=0.25,
    debug=0
)

fx = 0
cx = 0
fy = 0
cy = 0
k1 = 0
k2 = 0
p1 = 0
p2 = 0
k3 = 0


# Load the calibration parameters
# These would normally be obtained from a calibration process
camera_matrix = np.array([[fx, 0, cx], [0, fy, cy], [0, 0, 1]])
dist_coeffs = np.array([k1, k2, p1, p2, k3])

class CameraStream:
    def __init__(self, camera_index=0):
        # Initialize the camera capture object
        self.cap = cv2.VideoCapture(camera_index)
        self.aprilTags = {}
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

            # Break the loop if 'q' is pressed
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
                # Use solvePnP to estimate pose
                tag_size = 0.05  # Tag size in meters
                obj_points = np.array([
                    [-tag_size / 2, -tag_size / 2, 0],
                    [ tag_size / 2, -tag_size / 2, 0],
                    [ tag_size / 2,  tag_size / 2, 0],
                    [-tag_size / 2,  tag_size / 2, 0]
                ], dtype=np.float32)

                # Corners of the tag in the image
                img_points = np.array(r.corners, dtype=np.float32)

                # Estimate pose using solvePnP
                ret, rvec, tvec = cv2.solvePnP(obj_points, img_points, self.camera_matrix, self.dist_coeffs)

                if ret:
                    print(f"Rotation Vector (rvec): {rvec.ravel()}")
                    print(f"Translation Vector (tvec): {tvec.ravel()}")

                    # tvec contains the translation vector (x, y, z)
                    # The distance from the camera to the tag is the magnitude of the translation vector
                    distance = np.linalg.norm(tvec)
                    print(f"Estimated distance to the AprilTag: {distance:.2f} meters")

                    # Translation vector directly gives you the position of the tag in the camera's coordinate system
                    x = tvec[0]  # X-coordinate (horizontal position relative to camera)
                    y = tvec[1]  # Y-coordinate (vertical position relative to camera)
                    z = tvec[2]  # Z-coordinate (depth from the camera)

                    print(f"Position of the tag relative to the camera: X = {x}, Y = {y}, Z = {z}")

                # Convert rvec to a rotation matrix
                rotation_matrix, _ = cv2.Rodrigues(rvec)

                # Print the rotation matrix
                print("Rotation matrix:")
                print(rotation_matrix)

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
                cv2.putText(frame, f"Tag ID: {tagID}", (ptA[0], ptA[1] - 15),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                aprilTag = {
                    'tagID': tagID,
                    'x': cX,
                    'y': cY,
                    'time': time.time()
                }
                if(tagID == 73):
                    stopPin.high()
                    pyb.LED.on(blue)
                if(tagID == 72):
                    stopPin.low()
                    pyb.LED.off(blue)
                self.aprilTags[aprilTag['time']] = aprilTag
            # Display the resulting frame
            cv2.imshow("AprilTag Detection", frame)

            # Exit the loop when 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break




# Example usage:
if __name__ == "__camera__":
    stream = CameraStream(camera_index=0)  # 0 is the default camera index
    try:
        stream.start_stream()
    finally:
        stream.stop_stream()

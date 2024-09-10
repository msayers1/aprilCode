import cv2
import json
from pupil_apriltags import Detector
import time
import numpy as np


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

# For stereo vision, you would also need the stereo camera parameters


at_detector = Detector(
    families="tag36h11",
    nthreads=1,
    quad_decimate=1,
    quad_sigma=0,
    refine_edges=1,
    decode_sharpening=0.25,
    debug=0
)
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

    def calibrate(self):
        # Define the chessboard dimensions
        chessboard_size = (9, 6)  # Number of inner corners in row and column
        square_size = 0.025  # Size of each square in meters (adjust based on your chessboard)

        # Prepare object points (0,0,0), (1,0,0), (2,0,0), ..., (8,5,0)
        objp = np.zeros((chessboard_size[0] * chessboard_size[1], 3), np.float32)
        objp[:, :2] = np.mgrid[0:chessboard_size[0], 0:chessboard_size[1]].T.reshape(-1, 2) * square_size

        # Prepare arrays to store object points and image points
        objpoints = []
        imgpoints = []

        # Load the image
        image_path = 'chessboard_image.jpg'  # Path to your chessboard image
        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Find the chessboard corners
        ret, corners = cv2.findChessboardCorners(gray, chessboard_size, None)
        if ret:
            objpoints.append(objp)
            imgpoints.append(corners)
            
            # Draw and display the corners
            img = cv2.drawChessboardCorners(img, chessboard_size, corners, ret)
            cv2.imshow('Chessboard', img)
            cv2.waitKey(500)
            cv2.destroyAllWindows()
        else:
            print("Chessboard corners not found!")

        # Calibrate the camera
        ret, camera_matrix, dist_coeffs, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

        # Print camera matrix and distortion coefficients
        print("Camera matrix:\n", camera_matrix)
        print("Distortion coefficients:\n", dist_coeffs)

    def convert2d_to_3d(self, image_points):
        # Define fixed 2D image points use below as sample input. 
        # image_points = np.array([
        #     [x1, y1],
        #     [x2, y2],
        #     # Add more points as needed
        # ], dtype='float32')

        # Define corresponding 3D world points
        object_points = np.array([
            [0, 0, 0],
            [1, 0, 0],
            [1, 1, 0],
            [0, 1, 0],
            # Add more points as needed
        ], dtype='float32')

        # Load the camera matrix and distortion coefficients from calibration
        #camera_matrix = np.array([[fx, 0, cx], [0, fy, cy], [0, 0, 1]], dtype='float32')
        #dist_coeffs = np.array([k1, k2, p1, p2, k3], dtype='float32')

        # Estimate the pose of the object
        success, rotation_vector, translation_vector = cv2.solvePnP(object_points, image_points, camera_matrix, dist_coeffs)

        # Create a 3D grid
        grid_size = 10  # Size of the grid
        grid_points = []
        for x in range(grid_size):
            for y in range(grid_size):
                grid_points.append([x * 0.1, y * 0.1, 0])  # Adjust step size based on your needs
        grid_points = np.array(grid_points, dtype='float32')

        # Project the 3D grid points to 2D image plane
        image_points_reprojected, _ = cv2.projectPoints(grid_points, rotation_vector, translation_vector, camera_matrix, dist_coeffs)

        # Print the projected 2D points
        print("Projected 2D points:\n", image_points_reprojected)


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

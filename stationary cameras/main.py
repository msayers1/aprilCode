from camera import CameraStream  # Import the CameraStream class from camera.py
#import findCamera

def main():
    #findCamera.find_cameras(max_cameras=10)
    # Create an instance of the CameraStream class
    camera_stream = CameraStream(camera_index=2)  # Use 0 for the default camera
   

    try:
        # Start the camera stream
        camera_stream.start_stream()
        print(camera_stream.aprilTags)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Stop the camera stream and release resources
        camera_stream.stop_stream()

if __name__ == "__main__":
    main()

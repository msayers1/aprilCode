import cv2

def find_cameras(max_cameras=10):
    available_cameras = []
    print("running")
    for i in range(max_cameras):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            print(f"Camera {i} is available.")
            available_cameras.append(i)
            cap.release()
        else:
            print(f"Camera {i} is not available.")
    
    return available_cameras

def test_camera(index):
    cap = cv2.VideoCapture(index)
    if not cap.isOpened():
        print(f"Cannot open camera {index}")
        return
    
    print(f"Testing camera {index}")
    while True:
        ret, frame = cap.read()
        if not ret:
            print(f"Failed to grab frame from camera {index}")
            break
        
        cv2.imshow(f'Camera {index}', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__findCamera__":
    # Find available cameras
    cameras = find_cameras(max_cameras=10)
    
    # Test each available camera
    for cam in cameras:
        test_camera(cam)

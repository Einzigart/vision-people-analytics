import cv2

def find_available_cameras(max_cameras_to_check=10):
    """
    Checks for available camera IDs up to a specified maximum.

    Args:
        max_cameras_to_check (int): The maximum number of camera indices to check.

    Returns:
        list: A list of available camera IDs (indices).
    """
    available_cameras = []
    print(f"Checking for available webcams (up to index {max_cameras_to_check - 1}) using cv2.CAP_DSHOW...")
    for i in range(max_cameras_to_check):
        print(f"Attempting to open camera index: {i} with cv2.CAP_DSHOW...")
        cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
        
        if cap is None:
            print(f"cv2.VideoCapture({i}, cv2.CAP_DSHOW) returned None.")
            continue

        print(f"Checking if camera index {i} is opened...")
        is_opened = cap.isOpened()
        
        if is_opened:
            print(f"Webcam found and opened successfully at index: {i}")
            available_cameras.append(i)
            print(f"Releasing camera index: {i}...")
            cap.release()
            print(f"Camera index: {i} released.")
        else:
            print(f"Failed to open webcam at index: {i}")
            # It's good practice to release even if not opened, in case it was partially initialized.
            print(f"Attempting to release camera index: {i} (even if not opened)...")
            cap.release()
            print(f"Camera index: {i} released (after failed open).")
            
    if not available_cameras:
        print("No webcams found.")
    else:
        print(f"Available webcam IDs: {available_cameras}")
    return available_cameras

if __name__ == "__main__":
    find_available_cameras()

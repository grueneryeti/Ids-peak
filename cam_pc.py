import cv2
import threading
import time

frame_lock = threading.Lock()
current_frame = None

def camera_loop():
    global current_frame
    cap = cv2.VideoCapture(0)  # Standard-Webcam
    if not cap.isOpened():
        print("Webcam konnte nicht geöffnet werden.")
        return

    while True:
        ret, frame = cap.read()
        if ret:
            with frame_lock:
                current_frame = frame.copy()
        time.sleep(0.02)  # ca. 50 FPS

def get_frame():
    with frame_lock:
        if current_frame is not None:
            return current_frame.copy()
        else:
            return None
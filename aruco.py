import cv2
import time

ARUCO_ENABLED = True
processed_frame = None

def aruco_loop(get_frame_func):
    global processed_frame
    dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)

    while True:
        if not ARUCO_ENABLED:
            processed_frame = None
            time.sleep(0.05)
            continue

        frame = get_frame_func()
        if frame is None:
            time.sleep(0.02)
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, _ = cv2.aruco.detectMarkers(gray, dictionary)
        if ids is not None:
            cv2.aruco.drawDetectedMarkers(frame, corners, ids)

        processed_frame = frame.copy()
        time.sleep(0.02)
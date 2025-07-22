import cv2
import numpy as np

CALIBRATION_MODE = False

def run_calibration(frame):
    print("Kalibrierung gestartet...")
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    pattern_size = (7, 6)
    found, corners = cv2.findChessboardCorners(gray, pattern_size)

    if found:
        print("Board erkannt, Kalibrierung erfolgreich!")
        return True
    else:
        print("Board nicht erkannt.")
        return False
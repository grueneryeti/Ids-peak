import threading
import time
import sys

import cam_pc
import aruco
import calibration
from gui import CameraGUI

def main():
    calibration.CALIBRATION_MODE = False
    aruco.ARUCO_ENABLED = True

    cam_thread = threading.Thread(target=cam_pc.camera_loop, daemon=True)
    cam_thread.start()

    aruco_thread = threading.Thread(target=aruco.aruco_loop, args=(cam_pc.get_frame,), daemon=True)
    aruco_thread.start()

    gui = CameraGUI()
    gui.run()

    print("GUI geschlossen, Programm wird beendet.")
    sys.exit()

if __name__ == "__main__":
    main()
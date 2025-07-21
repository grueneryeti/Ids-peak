import tkinter as tk
from PIL import Image, ImageTk
import cv2

import cam_pc
import aruco
import calibration

class CameraGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Webcam GUI")

        self.label = tk.Label(self.root)
        self.label.pack()

        self.calibrated = False

    def update(self):
        frame = None
        if calibration.CALIBRATION_MODE and not self.calibrated:
            frame = cam_pc.get_frame()
            if frame is not None:
                self.calibrated = calibration.run_calibration(frame)
                if self.calibrated:
                    print("Kalibrierung fertig - Programm wird beendet.")
                    self.root.quit()
        else:
            if aruco.ARUCO_ENABLED:
                frame = aruco.processed_frame
                if frame is None:
                    frame = cam_pc.get_frame()
            else:
                frame = cam_pc.get_frame()

        if frame is not None:
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(img)
            imgtk = ImageTk.PhotoImage(image=img)
            self.label.imgtk = imgtk
            self.label.config(image=imgtk)

        self.root.after(30, self.update)

    def run(self):
        self.update()
        self.root.mainloop()
# camera.py
import cv2
import threading
import time
import numpy as np
import ids_peak
import ids_peak.ids_peak as ids_peak
import ids_peak_ipl.ids_peak_ipl as ids_ipl
import ids_peak.ids_peak_ipl_extension as ids_ipl_extension

frame_lock = threading.Lock()
current_frame = None

def camera_loop():
    global current_frame

    # IDS Peak initialisieren
    ids_peak.Library.Initialize()
    device_manager = ids_peak.DeviceManager.Instance()
    device_manager.Update()
    device_descriptors = device_manager.Devices()
    if not device_descriptors:
        print("Keine IDS Kamera gefunden.")
        return

    device = device_descriptors[0].OpenDevice(ids_peak.DeviceAccessType_Control)
    remote_device_nodemap = device.RemoteDevice().NodeMaps()[0]

    # Kamera konfigurieren
    remote_device_nodemap.FindNode("TriggerSelector").SetCurrentEntry("ExposureStart")
    remote_device_nodemap.FindNode("TriggerSource").SetCurrentEntry("Software")
    remote_device_nodemap.FindNode("TriggerMode").SetCurrentEntry("On")
    remote_device_nodemap.FindNode("ExposureTime").SetValue(20000)
    remote_device_nodemap.FindNode("ReverseX").SetValue(False)
    remote_device_nodemap.FindNode("ReverseY").SetValue(False)

    # Datenstrom vorbereiten
    datastream = device.DataStreams()[0].OpenDataStream()
    payload_size = remote_device_nodemap.FindNode("PayloadSize").Value()
    for _ in range(datastream.NumBuffersAnnouncedMinRequired()):
        buffer = datastream.AllocAndAnnounceBuffer(payload_size)
        datastream.QueueBuffer(buffer)

    datastream.StartAcquisition()
    remote_device_nodemap.FindNode("AcquisitionStart").Execute()
    remote_device_nodemap.FindNode("AcquisitionStart").WaitUntilDone()

    print("[camera] Kamera-Thread gestartet.")

    try:
        while True:
            remote_device_nodemap.FindNode("TriggerSoftware").Execute()
            buffer = datastream.WaitForFinishedBuffer(1000)
            raw_image = ids_ipl_extension.BufferToImage(buffer)
            color_image = raw_image.ConvertTo(ids_ipl.PixelFormatName_RGB8)
            datastream.QueueBuffer(buffer)

            frame = color_image.get_numpy_3D()
            bgr_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

            with frame_lock:
                current_frame = bgr_frame.copy()

            time.sleep(0.02)  # ca. 50 FPS

    except Exception as e:
        print("[camera] Fehler:", e)
    finally:
        print("[camera] Beende Kamera...")
        device.Close()
        ids_peak.Library.Close()

def get_frame():
    with frame_lock:
        return current_frame.copy() if current_frame is not None else None
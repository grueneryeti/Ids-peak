import threading
import time
import numpy as np
from ids_peak import ids_peak, ids_peak_ipl_extension

frame_lock = threading.Lock()
current_frame = None

def camera_loop():
    global current_frame

    ids_peak.Library.Initialize()
    system_manager = ids_peak.DeviceManager.Instance()
    system_manager.Update()

    if system_manager.Devices().empty():
        print("Keine IDS Kamera gefunden.")
        return

    device = system_manager.Devices()[0].OpenDevice(ids_peak.DeviceAccessType_Control)

    data_stream = device.DataStreams()[0].OpenDataStream()
    nodemap = device.RemoteDevice().NodeMaps()[0]

    payload_size = int(nodemap.FindNode("PayloadSize").Value())
    buffer_count = data_stream.NumBuffersAnnouncedMinRequired()
    buffers = []
    for _ in range(buffer_count):
        buffer = data_stream.AllocAndAnnounceBuffer(payload_size)
        data_stream.QueueBuffer(buffer)
        buffers.append(buffer)

    data_stream.StartAcquisition()
    nodemap.FindNode("AcquisitionStart").Execute()
    nodemap.FindNode("AcquisitionStart").WaitUntilDone()

    try:
        while True:
            buffer = data_stream.WaitForFinishedBuffer(5000)
            if buffer:
                image = ids_peak_ipl_extension.BufferToImage(buffer)
                np_img = image.get_numpy_2d()

                with frame_lock:
                    current_frame = np_img.copy()

                data_stream.QueueBuffer(buffer)
            else:
                print("Kein Bild empfangen.")
            time.sleep(0.01)
    except KeyboardInterrupt:
        pass
    finally:
        data_stream.StopAcquisition()
        nodemap.FindNode("AcquisitionStop").Execute()
        nodemap.FindNode("AcquisitionStop").WaitUntilDone()
        for buffer in buffers:
            data_stream.RevokeBuffer(buffer)
        device.Close()
        ids_peak.Library.Close()

def get_frame():
    with frame_lock:
        if current_frame is not None:
            return current_frame.copy()
        else:
            return None
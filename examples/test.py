import ids_peak.ids_peak as ids_peak

ids_peak.Library.Initialize()
device_manager = ids_peak.DeviceManager.Instance()
device_manager.Update()
device_descriptors = device_manager.Devices()

print("Found Devices: " + str(len(device_descriptors)))
for device_descriptor in device_descriptors:
    print(device_descriptor.DisplayName())

device = device_descriptors[0].OpenDevice(ids_peak.DeviceAccessType_Control)
print("Opened Device: " + device.DisplayName())
remote_device_nodemap = device.RemoteDevice().NodeMaps()[0]

remote_device_nodemap.FindNode("TriggerSelector").SetCurrentEntry("ExposureStart")
remote_device_nodemap.FindNode("TriggerSource").SetCurrentEntry("Software")
remote_device_nodemap.FindNode("TriggerMode").SetCurrentEntry("On")

datastream = device.DataStreams()[0].OpenDataStream()
payload_size = remote_device_nodemap.FindNode("PayloadSize").Value()
for i in range(datastream.NumBuffersAnnouncedMinRequired()):
    buffer = datastream.AllocAndAnnounceBuffer(payload_size)
    datastream.QueueBuffer(buffer)
    
datastream.StartAcquisition()
remote_device_nodemap.FindNode("AcquisitionStart").Execute()
remote_device_nodemap.FindNode("AcquisitionStart").WaitUntilDone()

remote_device_nodemap.FindNode("ExposureTime").SetValue(20000) # in microseconds

remote_device_nodemap.FindNode("ReverseX").SetValue(False)
remote_device_nodemap.FindNode("ReverseY").SetValue(False)

# trigger image
remote_device_nodemap.FindNode("TriggerSoftware").Execute()
buffer = datastream.WaitForFinishedBuffer(1000)

# convert to RGB
import ids_peak_ipl.ids_peak_ipl as ids_ipl
import ids_peak.ids_peak_ipl_extension as ids_ipl_extension
raw_image = ids_ipl_extension.BufferToImage(buffer)
# for Peak version 2.0.1 and lower, use this function instead of the previous line:
#raw_image = ids_ipl.Image_CreateFromSizeAndBuffer(buffer.PixelFormat(), buffer.BasePtr(), buffer.Size(), buffer.Width(), buffer.Height())
color_image = raw_image.ConvertTo(ids_ipl.PixelFormatName_RGB8)
datastream.QueueBuffer(buffer)

import numpy as np
picture = color_image.get_numpy_3D()

# display the image
from matplotlib import pyplot as plt
plt.figure(figsize = (15,15))
plt.imshow(picture)

picture.shape
picture[100,0:10,:]

picture[0:100,0:100,:] = [255,0,0]

# display the image
from matplotlib import pyplot as plt
plt.figure(figsize = (15,15))
plt.imshow(picture)

picture_roi = picture[:,150:1350,:]

plt.figure(figsize = (15,15))
plt.imshow(picture_roi)

fig,ax=plt.subplots(nrows=1,ncols=3,figsize=(15,5))
for i in range(3):
    component = np.zeros(picture_roi.shape,dtype="uint8")
    component[:,:,i] = picture_roi[:,:,i]
    ax[i].imshow(component)

import cv2
gray_image = cv2.cvtColor(picture_roi, cv2.COLOR_RGB2GRAY)
plt.imshow(gray_image, cmap='gray')

plt.xlim([0, 256])
hist = cv2.calcHist([gray_image], [0], None, [256], [0, 256])
plt.plot(hist, color="Black")

plt.xlim([0, 256])
colors = ["Red", "Green", "Blue"]
for i in range(3):
    hist = cv2.calcHist([picture_roi], [i], None, [256], [0, 256])
    plt.plot(hist, color=colors[i])
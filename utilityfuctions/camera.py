# camera.py

# This module contains the Camera class, which is a wrapper for the Raspberry Pi camera
# It is based on the picamera library.

import time

import cv2
import numpy as np
from utiliyfunctions.utils import Filter1D, Timer

class Camera():

    def __init__(self, size=10, frameRate=40, horizontalflip=False, verticalflip=False):
        from picamera import PiCamera, PiCameraCircularIO
        self.active = False
        try:
            if type(size) is not int:
                raise TypeError("Size must be an integer")
            elif 1 <= size and size <= 51:
                self.size = size
                self.horizontal_resolution = size * 64
                self.vertical_resolution = size * 48
            else:
                raise ValueError("Size must be in range 1 to 51")
        except TypeError or ValueError:
            raise
        self.picam = PiCamera()
        self.picam.resolution = (self.horizontal_resolution, self.vertical_resolution)
        self.picam.framerate = frameRate
        self.picam.horizontalflip = horizontalflip
        self.picam.verticalflip = verticalflip
        time.sleep(1)
        self.stream = PiCameraCircularIO(self.picam, seconds=1)
        self.frameRateTimer = Timer()
        self.frameRateFilter = Filter1D(maxSize=21)
        self.start()

    def close(self):
        self.stop()
        self.picam.close()

    def doWhiteBalance(self, whiteBalanceFileName='awb_gains.txt', mode='auto'):
		""" Does white balance calibration for PiCamera """
        ##  Set AWB mode for calibration
        self.picam.awb_mode = mode
        print('Calibrating white balance gains...')
        time.sleep(1)
        ##  Read AWB gains
        redgains = 0
        bluegains = 0
        nbReadings = 100
        for i in range(nbReadings):
            gains = self.picam.awb_gains
            redgains += gains[0]
            bluegains += gains[1]
            time.sleep(.01)
        gains = redgains / nbReadings, bluegains / nbReadings
        ##  Set AWB mode to off (manual)
        self.picam.awb_mode = 'off'
        ##  Set AWB gains to remain constant
        self.picam.awb_gains = gains

        ##  Write AWB gains to file
        redgains = float(gains[0])
        bluegains = float(gains[1])
        f = open(whiteBalanceFileName, 'w')
        f.flush()
        f.write(str(redgains) + ', ' + str(bluegains))
        f.close()
        print('AWB gains set to:', redgains, bluegains)
        print('AWB gains written to ' + whiteBalanceFileName)

    def readWhiteBalance(self, whiteBalanceFileName='awb_gains.txt'):
        """Reads white balance gains and sets them during game play"""
        ##  Read AWB gains from file
        f = open(whiteBalanceFileName, 'r')
        line = f.readline()
        f.close()
        redgains, bluegains = [float(g) for g in line.split(', ')]
        ##  Set AWB mode to off (manual)
        self.picam.awb_mode = 'off'
        ##  Set AWB gains to remain constant
        self.picam.awb_gains = redgains, bluegains
        print('AWB gains set to:', redgains, bluegains)
		
	def addFrameRateText(self, img, pos=(0, 25), color_BGR_tuple=(0,255,0), samples=21):
        """ Adds frame rate text to image """
        # Calculate framerate and reset timer
        self.frameRateFilter.addDataPoint(1 / self.frameRateTimer.getElapsed())
        self.frameRateTimer.reset()
        # Get averaged framerate as a string
        frString = '{}fps'.format(str(int(round(self.frameRateFilter.getMean(),
                                                0))))
        # Add text to image
        cv2.putText(img, frString, pos, cv2.FONT_HERSHEY_DUPLEX, 1, color_BGR_tuple)

    def getOpenCVImage(self):
        """Converts Camera frame to OpenCv Image array using numpy"""
        img = np.empty((self.vertical_resolution * self.horizontal_resolution * 3), dtype=np.uint8)
        self.picam.capture(img, 'bgr', use_video_port=True)
        return img.reshape((self.vertical_resolution, self.horizontal_resolution, 3))

    def start(self):
        if not self.active:
            self.active = True
            self.picam.start_recording(self.stream, format='h264',
                                       resize=(self.horizontal_resolution, self.vertical_resolution))

    def startPreview(self):
        self.picam.start_preview()

    def stop(self):
        self.active = False
        self.picam.stop_recording()
        self.stopPreview()

    def stopPreview(self):
        self.picam.stop_preview()

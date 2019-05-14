# utility.py


import glob
import time

import numpy as np

# Define possible gestures as constants
ROCK = 0
PAPER = 1
SCISSORS = 2

# Define text labels corresponding to gestures
gestureTxt = {ROCK: 'rock', PAPER: 'paper', SCISSORS: 'scissors'}

# Define paths to raw image folders
imgPathsRaw = {ROCK: './img/rock/', PAPER: './img/paper/',
               SCISSORS: './img/scissors/'}

def cameraSetup():
    from utilityfunctions.camera import Camera
    """Returns a camera object with pre-defined settings."""

    # Settings
    size = 8
    frameRate = 40
    whitebalanceFilename = 'awb_gains.txt'

    # Create Camera object
    print("Initializing camera")
    cameraobject = Camera(size=size, frameRate=frameRate)

    # Check if white balance file exists
    if len(glob.glob(whitebalanceFilename)) != 0:
        # File exists, set camera white balance using gains from file
        print("Reading white balance gains from {}".format(whitebalanceFilename))
        cameraobject.readWhiteBalance(whitebalanceFilename)
    else:
        # File does not exist. Prompt user to perform white balance.
        print("WARNING: No white balance file found. ")
        if input("Perform white balance (Y/n)?\n") != "n":
            print("Performing white balance.")
            print("Place a sheet of white paper in front of camera.")
            input("Press any key when ready.\n")
            cameraobject.doWhiteBalance(whitebalanceFilename)

    return cameraobject

class Filter1D:

    def __init__(self, maxSize=3):
        if maxSize % 2 == 1 and maxSize >= 3:
            self._maxSize = maxSize
        else:
            raise ValueError("maxSize must be an odd integer >= 3")
        self._data = np.ndarray(0)

    def addDataPoint(self, dataPoint):
        ##  Append new data point(s) to end of array
        self._data = np.insert(self._data, self._data.size, dataPoint)
        ##  Trim begining of array if longer than maxSize
        if self._data.size > self._maxSize:
            self._data = self._data[self._data.size - self._maxSize:]

    def getData(self):
        return self._data

    def getLast(self):
        return self._data[-1]

    def getMean(self, windowSize=0):
        if self._data.size == 0:
            raise RuntimeError("Filter1D data is empty. Call Filter1D.addDataPoint() to add data prior calling Filter1D.getMean().")
        if type(windowSize) is int:
            if windowSize <= 0 or windowSize > self._maxSize:
                windowSize = self._maxSize
            return np.mean(self._data[-windowSize:])
        else:
            raise TypeError("windowSize must be an integer")

    def getMedian(self, windowSize=0):
        if self._data.size == 0:
            raise RuntimeError("Filter1D data is empty. Call Filter1D.addDataPoint() to add data prior calling Filter1D.getMedian().")
        if type(windowSize) is not int:
            raise TypeError("windowSize must be an integer")
        if windowSize <= 0 or windowSize > self._maxSize:
            windowSize = self._maxSize
        if windowSize % 2 == 1 and windowSize <= self._maxSize:
            return np.median(self._data[-windowSize:])
        else:
            raise ValueError("windowSize must be an odd integer <= maxSize")

class Timer:
	"""Timer functions defined to clock the image captures and game play """
    def __init__(self):
        self.paused = False
        self.pauseInitTime = None
        self.pauseElapsed = 0
        self.initTime = time.time()

    def pause(self):
        self.pauseInitTime = time.time()
        self.paused = True

    def reset(self):
        self.paused = False
        self.pauseInitTime = None
        self.pauseElapsed = 0
        self.initTime = time.time()

	def getElapsed(self):
		if self.paused:
			return self.pauseInitTime - self.initTime - self.pauseElapsed
		else:
			return time.time() - self.initTime - self.pauseElapsed
    
	def resume(self):
        if self.paused:
            self.pauseElapsed += time.time() - self.pauseInitTime
            self.paused = False
        else:
            print("Warning: Timer.resume() called without prior call to Timer.pause()")

    def sleepToElapsed(self, delay, reset = True):
        if self.getElapsed() < delay:
            time.sleep(delay - self.getElapsed())
        if reset:
            self.reset()
			
	def isWithin(self, delay):
        if self.getElapsed() < delay:
            return True
        else:
            return False

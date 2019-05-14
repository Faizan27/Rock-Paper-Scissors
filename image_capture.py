# capture.py

# Script used to capture image and save it in img folder which is then used to train the model

import time

import cv2
import numpy as np

from utilityfunctions import utils
from utilityfunctions import imgproc as imp

def saveImage(image, gesture):

    # Define image path and filename
    folder = utils.imgPathsRaw[gesture]
    name = utils.gestureTxt[gesture] + '-' + time.strftime('%Y%m%d-%H%M%S')
    extension = '.png'

    print("Saving " + name + extension + " - Accept ([y]/n)?")

    # Write gesture name to image and show for a few seconds
    imgTxt = image.copy()
    font = cv2.FONT_HERSHEY_COMPLEX
    cv2.putText(imgTxt, utils.gestureTxt[gesture], (10,25), font, 1, (0, 0, 255))
    cv2.imshow('Camera', imgTxt)
    key = cv2.waitKey(2000)
    if key not in [110, 120]:
        # Key is not x or n. Save image
        cv2.imwrite(folder + name + extension, image)
        print("Saved ({}x{})".format(image.shape[1], image.shape[0]))
    else:
        print("Save cancelled")

try:
    # Create camera object with pre-defined settings
    cameraobject = utils.cameraSetup()

    # Initialize variable to stop while loop execution
    stop = False

    # Initialize opencv GUI window (resizeable)
    cv2.namedWindow('Camera', cv2.WINDOW_AUTOSIZE)

    # Print instructions
    print("\nImage capture mode")
    print("Press the following keys to capture:")
    print("Rock gesture: r")
    print("Paper gesture: p")
    print("Scisors gesture: s or c")
    print("Press ESC or q to quit capture mode\n")

    # Main loop
    while not stop:
        # Capture image from camera
        image = cameraobject.getOpenCVImage()

        # Crop image
        image = imp.crop(image)

        # Add framerate to copy of image
        rotatedImage = imp.fastRotate(image)
        txtPos = (5, rotatedImage.shape[0] - 10)
        cameraobject.addFrameRateText(rotatedImage, txtPos, bgr=(0,0,255))

        # Display image
        cv2.imshow('Camera', rotatedImage)

        # Wait for key press
        key = cv2.waitKey(1)
        if key in [27, 113]:
            # Escape or "Q" key pressed; Stop.
            stop = True
        else:
            gesture = None
            if key == 114:
                # "R" key pressed (Rock)
                gesture = utils.ROCK
            elif key == 112:
                # "P" key pressed (Paper)
                gesture = utils.PAPER
            elif key in [115, 99]:
                # "S" or "C" key pressed (Scisors)
                gesture = utils.SCISSORS
            if gesture is not None:
                saveImage(image, gesture)

finally:
    cv2.destroyAllWindows()
    cameraobject.close()

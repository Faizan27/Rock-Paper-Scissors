# imageprocessing.py
# This file contains image processing functions used in this project.

import os
from glob import glob
import time

import numpy as np

from skimage.io import imread
from skimage import color
from skimage import feature
from skimage import filters

from utilityfunctions import utils

import cv2

def crop(img):
    """Crops runtime image to region of interest"""
    return img[75:275, 125:425]

def hueDistance(img, hueValue):
    # Convert image to hsv_image colorspace
    hsv_image = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)

    hue_channel = hsv_image[:,:,0].astype(int)

    # Calculate hue distance
    distance = np.abs(hsv_image[:,:,0] - hueValue)
    if hueValue < 90:
        hueOffset = 180
    else:
        hueOffset = -180

    distance = np.minimum(np.abs(hue_channel - hueValue),
                      np.abs(hue_channel - (hueValue + hueOffset)))

    return distance
	
def generateGrayFeatures(imageshape=(200,300, 3), backimage=0, debug=False, rs=42):
    """Generates Gray Scale image features to train the Vector machine"""

    imsize = imageshape[0] * imageshape[1]

    t0 = time.time()

    gestures = [utils.ROCK, utils.PAPER, utils.SCISSORS]

    # Create a list of image files for each gesture
    files = []
    for i, gesture in enumerate(gestures):
        path = os.path.join(utils.imgPathsRaw[gesture], '*.png')
        files.append(glob(path))
        files[i].sort(key=str.lower)

    backImages = sum([len(i) for i in files])

    # Create empty numpy arays for features and labels
    features = np.empty((backImages, imsize), dtype=np.float32)
    labels = np.empty((backImages), dtype=np.int)

    # Generate grayscale images
    counter = 0
    for i, gesture in enumerate(gestures):

        if backimage > 0:
            np.random.seed = rs
            files[i] = np.random.permutation(files[i])
            if len(files[i]) > backimage:
                files[i] = files[i][:int(backimage / 3)]

        for imageFile in files[i]:

            if debug:
                print('Processing image {}'.format(imageFile))

            # Load image as a numpy array
            img = imread(imageFile)

            if img.shape == imageshape:

                # Generate and store image features in features array
                features[counter] = getGray(img, threshold=17)

                # Store image label in labels array
                labels[counter] = gesture

                counter += 1

            else:
                print('Image {} has invalid shape: {}, {} expected, skipping image.'.format( \
                    imageFile, img.shape, imageshape))

    print('Completed processing {} images'.format(counter))

    return features[:counter], labels[:counter]


def getGray(img, hueValue=63, threshold=0):
    img = removeBackground(img, hueValue, threshold)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY).astype(np.float32) / 255
    return img.ravel()


def removeBackground(img, hueValue, threshold=0):
    distance = hueDistance(img, hueValue)

    image_copy = img.copy()

    if threshold == 0:
        image_copy[distance < filters.threshold_mean(distance)] = 0
    else:
        image_copy[distance < threshold] = 0

    return image_copy

def fastRotate(img):
    return np.transpose(img, axes=(1, 0, 2))[:,::-1,:].copy()
# playgui.py
# The main driver file

import pickle
import random
import sys
import time

import pygame as pgame
import pygame.locals

import numpy as np
import cv2

from utilityfunctions import utils
from utilityfunctions import imgproc as imp
from utilityfunctions.gui import RPSGUI

def saveImage(img, gesture, verbose=False):

    # Define image path and filename
    folder = utils.imgPathsRaw[gesture]
    name = utils.gestureTxt[gesture] + '-' + time.strftime('%Y%m%d-%H%M%S')
    extension = '.png'

    if verbose:
        print('Saving {}'.format(folder + name + extension))

    # Save image
    cv2.imwrite(folder + name + extension, img)

if __name__ == '__main__':
    try:
        # Initialize game mode variables
        privacy = False
        loop = False

        # Read command line arguments
        argv = sys.argv
        argv.pop(0)

        if len(sys.argv) > 0:
            for arg in argv:
                if arg == 'privacy':
                    privacy = True
                elif arg == 'loop':
                    loop = True
                else:
                    print('{} is not a recognized argument'.format(arg))

        # Load classifier from pickle file
        filename = 'clf.pkl'
        with open(filename, 'rb') as f:
            clf = pickle.load(f)

        # Create camera object with pre-defined settings
        cameraobject = utils.cameraSetup()

        # Initialize last gesture value
        lastGesture = -1

        # Define score at which game ends
        endScore = 5

        # Initialize GUI
        gui = RPSGUI(privacy=privacy, loop=loop)

        # Load static images for computer gestures
        coImgs = {}
        img = cv2.imread('img/gui/rock.png', cv2.IMREAD_COLOR)
        coImgs[utils.ROCK] = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.imread('img/gui/paper.png', cv2.IMREAD_COLOR)
        coImgs[utils.PAPER] = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.imread('img/gui/scissors.png',
                         cv2.IMREAD_COLOR)
        coImgs[utils.SCISSORS] = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Load green image
        greenImg = cv2.imread('img/gui/green.png', cv2.IMREAD_COLOR)
        greenImg = cv2.cvtColor(greenImg, cv2.COLOR_BGR2RGB)

        while True:

            # Get image from camera
            img = imp.crop(cameraobject.getOpenCVImage())

            # Convert image to RGB (from BGR)
            imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            # Set player image to imgRGB
            gui.setPlImg(imgRGB)

            # Get grayscale image
            gray = imp.getGray(imgRGB, threshold=17)

            # Count non-background pixels
            nonZero = np.count_nonzero(gray)

            # Define waiting time
            waitTime = 0

            # Parameters for saving new images
            gesture = None
            verbose = False

            # Check if player hand is present
            if nonZero > 9000:

                # Predict gesture
                predictedgesture = clf.predict([gray])[0]

                if predictedgesture == lastGesture:
                    successive += 1
                else:
                    successive = 0

                if successive == 2:
                    print('Player: {}'.format(utils.gestureTxt[predictedgesture]))
                    waitTime = 3000
                    gesture = predictedgesture

                    # Computer gesture
                    computerGesture = random.randint(0,2)
                    print('Computer: {}'.format(utils.gestureTxt[computerGesture]))

                    # Set computer image to computer gesture
                    gui.setCoImg(coImgs[computerGesture])

                    diff = computerGesture - predictedgesture
                    if diff in [-2, 1]:
                        print('Computer wins!')
                        gui.setWinner('computer')
                    elif diff in [-1, 2]:
                        print('Player wins!')
                        gui.setWinner('player')
                    else:
                        print('Tie')
                        gui.setWinner('tie')
                    print('Score: player {}, computer {}\n'.format(gui.plScore,
                                                                 gui.coScore))

                lastGesture = predictedgesture

            else:

                lastGesture = -1

                # Set computer image to green
                gui.setCoImg(greenImg)
                gui.setWinner()

            # Draw GUI
            gui.draw()

            # Flip pygame display
            pgame.display.flip()

            # Wait
            pgame.time.wait(waitTime)

            if gesture is not None:
                # Save new image
                saveImage(img, gesture, verbose)

            # Check pygame events
            for event in pgame.event.get():
                if event.type == pgame.locals.QUIT:
                    gui.quit()

            # Check if scores reach endScore (end of game)
            if gui.plScore == endScore or gui.coScore == endScore:
                if gui.coScore > gui.plScore:
                    print('Game over, computer wins...\n')
                else:
                    print('Game over, player wins!!!\n')
                gui.gameOver()


    finally:
        f.close()
        cameraobject.close()

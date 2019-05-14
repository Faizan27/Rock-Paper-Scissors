# Gamegui.py

# This file defines the RPSGUI class and associated methods to manage the game
# graphical user intrerface (GUI).

import sys
import numpy as np
import cv2
import pygame as pgame
import pygame.freetype

class RPSGUI():

    def __init__(self, privacy=False, loop=False):
        pgame.init()
        self.privacy = privacy
        self.loop = loop
        self.gameWidth = 640
        self.gameHeight = 480
        self.surf = pgame.display.set_mode((self.gameWidth, self.gameHeight))
        pgame.display.set_caption('Rock-Paper-Scissors')
        self.plScore = 0
        self.coScore = 0
        self.plImg = pgame.Surface((200, 300))
        self.coImg = pgame.Surface((200, 300))
        self.plImgPos = (380, 160)
        self.coImgPos = (60, 160)
        self.plZone = pgame.Surface((250, 330))
        self.coZone = pgame.Surface((250, 330))
        self.plZonePos = (355, 145)
        self.coZonePos = (35, 145)
        self.winner = None

        # colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.RED = (255, 0, 0)
        self.GREEN = (0, 255, 0)
        self.BLUE = (0, 0, 255)

        self.showPrivacyNote()

    def blitTextAlignCenter(self, surf, text, pos):
        textWidth = text[1].width
        surf.blit(text[0], (pos[0] - textWidth / 2, pos[1]))

    def gameOver(self, delay=3500):
        gameOverZone = pgame.Surface((400, 200))
        gameOverZone.fill(self.WHITE)
		vertices = [(3, 3), (396, 3), (396, 196), (3, 196), (3, 3)]
        pgame.draw.polygon(gameOverZone, self.BLACK, vertices, 1)
		font = pgame.freetype.SysFont(None, 40)
        gameOverText = font.render('GAME OVER', self.BLACK)
        self.blitTextAlignCenter(gameOverZone, gameOverText, (200, 45))

        if self.plScore > self.coScore:
            winner = 'PLAYER'
            color = self.GREEN
        else:
            winner = 'COMPUTER'
            color = self.RED

        winnerText = font.render('{} WINS!'.format(winner), color)
        self.blitTextAlignCenter(gameOverZone, winnerText, (200, 110))

        pos = (self.gameWidth / 2 - 200, 175)
        self.surf.blit(gameOverZone, pos)

        pgame.display.flip()

        pgame.time.wait(delay)

        if self.loop:
            self.reset()
        else:
            self.quit()

    def quit(self, delay=0):
        pgame.time.wait(delay)
        pgame.quit()
        sys.exit()

    def reset(self):
        self.plScore = 0
        self.coScore = 0
        self.showPrivacyNote()

    def setCoImg(self, img):
        self.coImg = pgame.surfarray.make_surface(img[:,::-1,:])

    def setPlImg(self, img):
        self.plImg = pgame.surfarray.make_surface(img[::-1,:,:])

    def setWinner(self, winner=None):
        self.winner = winner
        if winner == 'player':
            self.plScore += 1
        elif winner == 'computer':
            self.coScore += 1
			
	def draw(self):
			self.surf.fill(self.WHITE)

			playerZone = [(325, 3), (634, 3), (634, 476), (325, 476), (325, 3)]
			pgame.draw.polygon(self.surf, self.BLACK, playerZone, 1)
			computerZone = [(5, 3), (315, 3), (315, 476), (5, 476), (5, 3)]
			pgame.draw.polygon(self.surf, self.BLACK, computerZone, 1)

			font = pgame.freetype.SysFont(None, 30)
			text = font.render('PLAYER', self.BLACK)
			self.blitTextAlignCenter(self.surf, text, (480,15))
			text = font.render('COMPUTER', self.BLACK)
			self.blitTextAlignCenter(self.surf, text, (160,15))

			if self.winner == 'player':
				self.plZone.fill(self.GREEN)
				self.coZone.fill(self.RED)
			elif self.winner == 'computer':
				self.plZone.fill(self.RED)
				self.coZone.fill(self.GREEN)
			elif self.winner == 'tie':
				self.plZone.fill(self.BLUE)
				self.coZone.fill(self.BLUE)
			else:
				self.plZone.fill(self.WHITE)
				self.coZone.fill(self.WHITE)

			self.surf.blit(self.plZone, self.plZonePos)
			self.surf.blit(self.coZone, self.coZonePos)

			self.surf.blit(self.plImg, self.plImgPos)
			self.surf.blit(self.coImg, self.coImgPos)

			font = pgame.freetype.SysFont(None, 100)
			text = font.render(str(self.plScore), self.BLACK)
			self.blitTextAlignCenter(self.surf, text, (480, 60))
			text = font.render(str(self.coScore), self.BLACK)
			self.blitTextAlignCenter(self.surf, text, (160, 60))
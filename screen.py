from math import pi
from typing import Tuple
import pygame, sys
from pygame.locals import *
from pygame import Rect

from document import Document

FPS = 30 #frames per second setting
white = (255, 255, 255)
black = (  0,   0,   0)
green = (0, 255, 0)
blue = (0, 0, 180)
red   = (255,   0,   0)

class Screen:
    """
    Creates pygame screen and draws objects from document
    """
    # good pygame tutorial https://riptutorial.com/pygame

    def __init__(self, doc : Document) -> None:
        pygame.init()

        self.doc = doc

        self.fpsClock = pygame.time.Clock()

        background_colour = (200,200,255) # For the background color of your window
        (width, height) = (500, 500) # Dimension of the window

        self.screen = pygame.display.set_mode((width, height), flags=pygame.RESIZABLE) # Making of the screen
        pygame.display.set_caption('Interactive agents') # Name for the window
        self.screen.fill(background_colour) #This syntax fills the background colour

    def Update(self) -> None:
        self.screen.fill(white)

        self.DrawDoc()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.update()
        self.fpsClock.tick(FPS)


    def DrawDoc(self):
        (screenX, screenY) = self.GetScreenSize()
        (cellsX, cellsY) = self.doc.size
        cellSize = int(min(screenX / cellsX, screenY / cellsY))
        boardRect = Rect(0,0, cellSize * cellsX, cellSize * cellsY)

        self.DrawRect(boardRect, (200,200,255))

        self.DrawCellLines(boardRect)

        self.DrawAgent(1, 2, boardRect)

        self.DrawTable(2,2, 3,2, boardRect)

        self.DrawChair(4, 2, boardRect)
        

    def DrawCellLines(self, boardRect : Rect):
        (cellsX, cellsY) = self.doc.size
        assert int(boardRect.width / cellsX) == int(boardRect.height / cellsY)

        cellSize = int(min(boardRect.width / cellsX, boardRect.height / cellsY))
        lineWidth = 1
        
        for x in range(0, cellsX+1):
            pygame.draw.line(self.screen, black, (boardRect.x + x * cellSize, boardRect.y), (boardRect.x + x * cellSize, boardRect.y + cellsY * cellSize), lineWidth)
        for y in range(0, cellsY+1):
            pygame.draw.line(self.screen, black, (boardRect.x, boardRect.y + y * cellSize), (boardRect.x + cellsX * cellSize, boardRect.y + y * cellSize), lineWidth)

        
    
    def DrawAgent(self, X : int, Y : int, boardRect : Rect) -> None:
        (cellsX, cellsY) = self.doc.size
        assert int(boardRect.width / cellsX) == int(boardRect.height / cellsY)
        cellSize = int(min(boardRect.width / cellsX, boardRect.height / cellsY))
        Y = cellsY - Y -1   # Y flip

        agentRect = Rect(boardRect.x + X * cellSize, boardRect.y + Y * cellSize, cellSize, cellSize)
        self.DrawAgentInRect(agentRect)

    def DrawTable(self, X1 : int, Y1 : int, X2 : int, Y2 : int, boardRect : Rect) -> None:
        (cellsX, cellsY) = self.doc.size
        assert int(boardRect.width / cellsX) == int(boardRect.height / cellsY)
        cellSize = int(min(boardRect.width / cellsX, boardRect.height / cellsY))
        Xmin = min(X1, X2)
        Ymin = max(Y1, Y2)
        Ymin = cellsY - Ymin -1   # Y flip
        if(X1 != X2):
            tableRect = Rect(boardRect.x + Xmin * cellSize, boardRect.y + Ymin * cellSize, cellSize * 2 , cellSize)
        else:
            tableRect = Rect(boardRect.x + Xmin * cellSize, boardRect.y + Ymin * cellSize, cellSize, cellSize * 2)

        self.DrawTableInRect(tableRect)

    def DrawChair(self, X : int, Y : int, boardRect : Rect) -> None:
        (cellsX, cellsY) = self.doc.size
        assert int(boardRect.width / cellsX) == int(boardRect.height / cellsY)
        cellSize = int(min(boardRect.width / cellsX, boardRect.height / cellsY))
        Y = cellsY - Y -1   # Y flip

        chairRect = Rect(boardRect.x + X * cellSize, boardRect.y + Y * cellSize, cellSize, cellSize)
        self.DrawChairInRect(chairRect)

    def GetScreenSize(self) -> Tuple[int, int]:
        return self.screen.get_size()
        
    def DrawRect(self, rect : Rect, color) -> None:
        pygame.draw.rect(self.screen, color, rect)

    def DrawAgentInRect(self, rect : Rect) -> None:
        off = int(rect.width / 10)
        topCenterX = (rect.left + rect.right) / 2
        points = (
            (rect.left + off, rect.bottom - off),
            (rect.right - off, rect.bottom - off),
            (topCenterX, rect.top + off)
        )
        agentColor = (255, 0, 0)
        pygame.draw.polygon(self.screen, agentColor, points)

    def DrawTableInRect(self, rect : Rect) -> None:
        deflate = -0.1
        rect = rect.inflate(deflate * rect.width, deflate * rect.height)
        tableColor = (180, 20, 20)
        pygame.draw.ellipse(self.screen, tableColor, rect)

    def DrawChairInRect(self, rect : Rect) -> None:
        deflate = -0.4
        rect = rect.inflate(deflate * rect.width, deflate * rect.height)
        chairColor = (100, 0, 0)
        pygame.draw.ellipse(self.screen, chairColor, rect)


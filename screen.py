from typing import Tuple
import pygame, sys
from pygame import color
from pygame.locals import *
from pygame import Rect

from document import Document
from simObj import Agent
from action import Action

FPS = 60  # frames per second setting
white = (255, 255, 255)
black = (  0,   0,   0)
green = (  0, 255,   0)
blue  = (  0,   0, 180)
red   = (255,   0,   0)


class Screen:
    """
    Creates pygame screen and draws objects from document
    """
    # good pygame tutorial https://riptutorial.com/pygame

    def __init__(self) -> None:
        pygame.init()

        self.fpsClock = pygame.time.Clock()

        background_colour = (200,200,255) # For the background color of your window
        (width, height) = (500, 500) # Dimension of the window

        self.screen = pygame.display.set_mode((width, height), flags=pygame.RESIZABLE) # Making of the screen
        pygame.display.set_caption('Interactive agents') # Name for the window
        self.screen.fill(background_colour) #This syntax fills the background colour

    def update(self, doc : Document) -> None:
        self.screen.fill(white)

        self.drawDoc(doc)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.update()
        self.fpsClock.tick(FPS)

    def drawDoc(self, doc: Document):
        (screenX, screenY) = self.getScreenSize()
        (cellsX, cellsY) = doc.size
        cellSize = int(min(screenX / cellsX, screenY / cellsY))
        boardRect = Rect(0, 0, cellSize * cellsX, cellSize * cellsY)

        self.drawRect(boardRect, (200, 200, 255))

        self.drawCellLines(boardRect, doc)

        for table in doc.tables:
            self.drawTable(table.x1, table.y1, table.x2, table.y2, boardRect, doc)

        for agent in doc.agents:
            self.drawAgent(agent, boardRect, doc)
            print("agent x: ", agent.x, " y: ", agent.y)
        
        for chair in doc.chairs:
            self.drawChair(chair.x, chair.y, boardRect, doc)

    def drawCellLines(self, boardRect: Rect, doc: Document):
        (cellsX, cellsY) = doc.size
        assert int(boardRect.width / cellsX) == int(boardRect.height / cellsY)

        cellSize = int(min(boardRect.width / cellsX, boardRect.height / cellsY))
        lineWidth = 1
        
        for x in range(0, cellsX+1):
            pygame.draw.line(self.screen, black, (boardRect.x + x * cellSize, boardRect.y),
                             (boardRect.x + x * cellSize, boardRect.y + cellsY * cellSize), lineWidth)
        for y in range(0, cellsY+1):
            pygame.draw.line(self.screen, black, (boardRect.x, boardRect.y + y * cellSize),
                             (boardRect.x + cellsX * cellSize, boardRect.y + y * cellSize), lineWidth)
    

    def drawAgent(self, agent: Agent, boardRect : Rect, doc : Document) -> None:
        (cellsX, cellsY) = doc.size
        assert int(boardRect.width / cellsX) == int(boardRect.height / cellsY)
        cellSize = int(min(boardRect.width / cellsX, boardRect.height / cellsY))
        X = agent.x
        Y = agent.y
        Y = cellsY - Y -1   # Y flip

        agentRect = Rect(boardRect.x + X * cellSize, boardRect.y + Y * cellSize, cellSize, cellSize)
        self.drawAgentInRect(agentRect)

        # last_action = agent.last_action
        if(agent.grab):
            sX = agentRect.centerx
            sY = agentRect.centery
            if(agent.grab == Action.north):
                grabLineEnd = [sX,sY - cellSize]
            elif(agent.grab == Action.east):
                grabLineEnd = [sX + cellSize, sY]
            elif(agent.grab == Action.south):
                grabLineEnd = [sX,sY + cellSize]
            elif(agent.grab == Action.west):
                grabLineEnd = [sX - cellSize, sY]
            
            self.drawAgentGrab([sX,sY], grabLineEnd);


    def drawTable(self, X1: int, Y1: int, X2: int, Y2: int, boardRect: Rect, doc: Document) -> None:
        (cellsX, cellsY) = doc.size
        assert int(boardRect.width / cellsX) == int(boardRect.height / cellsY)
        cellSize = int(min(boardRect.width / cellsX, boardRect.height / cellsY))
        Xmin = min(X1, X2)
        Ymin = max(Y1, Y2)
        Ymin = cellsY - Ymin - 1   # Y flip
        if X1 != X2:
            tableRect = Rect(boardRect.x + Xmin * cellSize, boardRect.y + Ymin * cellSize, cellSize * 2 , cellSize)
        else:
            tableRect = Rect(boardRect.x + Xmin * cellSize, boardRect.y + Ymin * cellSize, cellSize, cellSize * 2)

        self.drawTableInRect(tableRect)

    def drawChair(self, X: int, Y: int, boardRect: Rect, doc: Document) -> None:
        (cellsX, cellsY) = doc.size
        assert int(boardRect.width / cellsX) == int(boardRect.height / cellsY)
        cellSize = int(min(boardRect.width / cellsX, boardRect.height / cellsY))
        Y = cellsY - Y -1   # Y flip

        chairRect = Rect(boardRect.x + X * cellSize, boardRect.y + Y * cellSize, cellSize, cellSize)
        self.drawChairInRect(chairRect)

    def getScreenSize(self) -> Tuple[int, int]:
        return self.screen.get_size()
        
    def drawRect(self, rect : Rect, color) -> None:
        pygame.draw.rect(self.screen, color, rect)

    def drawAgentInRect(self, rect : Rect) -> None:
        off = int(rect.width / 10)
        topCenterX = (rect.left + rect.right) / 2
        points = (
            (rect.left + off, rect.bottom - off),
            (rect.right - off, rect.bottom - off),
            (topCenterX, rect.top + off)
        )
        agentColor = (255, 0, 0)
        pygame.draw.polygon(self.screen, agentColor, points)

    def drawAgentGrab(self, start, end) -> None:
        agentColor = (255, 150, 0)
        pygame.draw.line(self.screen, agentColor, start, end, 3);

    def drawTableInRect(self, rect : Rect) -> None:
        deflate = -0.1
        rect = rect.inflate(deflate * rect.width, deflate * rect.height)
        tableColor = (180, 20, 20)
        pygame.draw.ellipse(self.screen, tableColor, rect)

    def drawChairInRect(self, rect : Rect) -> None:
        deflate = -0.4
        rect = rect.inflate(deflate * rect.width, deflate * rect.height)
        chairColor = (100, 0, 0)
        pygame.draw.ellipse(self.screen, chairColor, rect)

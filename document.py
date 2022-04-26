from random import randrange
import numpy as np
from action import Action
from simObj import Agent, Chair, Table

class Document:
    """
    Represents simulation state, collection of objects 
    """
    def __init__(self, sizeX: int, sizeY: int) -> None:
        self.size = np.array([sizeX, sizeY])
        self.agents = list()
        self.tables = list()
        self.chairs = list()
        self.grid = [[None for x in range(self.size[1])] for y in range(self.size[0])] 

    # returns true if action was valid and was performed, false otherwise 
    def ApplyActionToAgent(self, agent: Agent, action : Action) -> bool:
        inGridAgent = self.grid[agent.x][agent.y]
        assert(inGridAgent == agent)

        ##############################################
        # TEMP
        Xmove = randrange(-1,2,1)
        Ymove = randrange(-1,2,1)
        XNew = agent.x + Xmove
        YNew = agent.y + Ymove

        if(XNew < 0): XNew = 0
        if(XNew >= self.size[0]): XNew = self.size[0]-1
        if(YNew < 0): YNew = 0
        if(YNew >= self.size[1]): YNew = self.size[1]-1
        self.grid[agent.x][agent.y] = None
        self.grid[XNew][YNew] = agent
        agent.x = XNew
        agent.y = YNew
        return True
        # TEMP
        ##############################################

    def AddAgent(self, x: int, y: int) -> bool:
        if(self.grid[x][y] != None):
            return False

        agent = Agent(x, y)
        self.grid[x][y] = agent
        self.agents.append(agent)
        return True

    def AddTable(self, x1: int, y1: int, x2: int, y2: int) -> bool:
        if(self.grid[x1][y1] != None):
            return False
        if(self.grid[x2][y2] != None):
            return False
        if(abs(x1-x2) + abs(y1-y2) != 1):
            return False

        
        table = Table(x1, y1, x2, y2)
        self.grid[x1][y1] = table
        self.grid[x2][y2] = table
        self.tables.append(table)
        return True

    def AddChair(self, x: int, y: int) -> bool:
        if(self.grid[x][y] != None):
            return False

        chair = Chair(x, y)
        self.grid[x][y] = chair
        self.chairs.append(chair)
        return True
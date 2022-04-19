from random import randrange
import numpy as np
from simObj import Agent

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
    def ApplyActionToAgent(self, agent: Agent, action) -> bool:
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

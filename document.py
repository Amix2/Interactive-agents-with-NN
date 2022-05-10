from random import randrange
from typing import Union

import numpy as np
from action import Action
from simObj import Agent, Chair, Table, ISimObj
from cellCodes import CellCodes


class Document:
    """
    Represents simulation state, collection of objects 
    """
    def __init__(self, sizeX: int, sizeY: int) -> None:
        self.size = np.array([sizeX, sizeY])
        self.agents : list[Agent] = list() 
        self.tables : list[Table] = list()
        self.chairs : list[Chair] = list()
        self.grid: list[list[Union[None, ISimObj]]] = [[None for x in range(self.size[1])] for y in range(self.size[0])]

    # returns true if action was valid and was performed, false otherwise
    def applyActionToAgent(self, agent: Agent, action: Union[Action, None]) -> bool:
        inGridAgent = self.grid[agent.x][agent.y]
        assert(inGridAgent == agent)
        self.validate()
        newPosition = np.array([agent.x, agent.y])

        # current position of grabbed object
        if agent.grab:
            targetPosition = newPosition + Action.directionToVector(agent.grab)
        else:
            targetPosition = np.array([None, None])

        if action is None:
            # random movement
            Xmove = randrange(-1, 2, 1)
            Ymove = randrange(-1, 2, 1)
            newPosition += [Xmove, Ymove]
        else:
            # carry out action
            if action.type == Action.release:
                agent.grab = None
                return True;

            elif action.type == Action.move:
                # move to a different square
                newPosition += Action.directionToVector(action.direction)

            elif action.type == Action.grab:
                # grab furniture
                if agent.grab:
                    # ignore grab actions while holding an object
                    return False

                targetPosition = newPosition + Action.directionToVector(action.direction)

                # check if there's furniture there
                grabTarget = self.GetCell(targetPosition[0], targetPosition[1])
                if self.GetCellCode(targetPosition[0], targetPosition[1]) in [CellCodes.Chair, CellCodes.Table_max, CellCodes.Table_min]:
                    # TODO: consider legal table-carrying configurations (can you only carry by holding short ends?)
                    agent.grab = action.direction

            elif action.type == Action.wait:
                return True

        # check against walking off-scene
        if newPosition[0] < 0:
            newPosition[0] = 0
        if newPosition[0] >= self.size[0]:
            newPosition[0] = self.size[0]-1
        if newPosition[1] < 0:
            newPosition[1] = 0
        if newPosition[1] >= self.size[1]:
            newPosition[1] = self.size[1]-1

        # check against walking onto occupied cells - can only push the grabbed object or move onto empty cells
        if not np.array_equal(newPosition, targetPosition) and \
                self.GetCellCode(newPosition[0], newPosition[1]) != CellCodes.Empty:
            return False

        # TODO: check against moving furniture off-scene or onto occupied cells
        # TODO: check if a table can be moved
        #  (agents can check for intentions to move other side or submit their own intention for next agents in line?)
        if agent.grab and action.type == Action.move:
            pass

        # TODO: move tables
        if agent.grab and action.type == Action.move:
            target = self.grid[targetPosition[0]][targetPosition[1]]
            targetCode = self.GetCellCode(targetPosition[0], targetPosition[1])
            targetNewPosition = targetPosition + Action.directionToVector(action.direction)
            if targetCode == CellCodes.Chair:
                target.x = targetNewPosition[0]
                target.y = targetNewPosition[1]
                self.grid[targetPosition[0]][targetPosition[1]] = None
                self.grid[targetNewPosition[0]][targetNewPosition[1]] = target

        if self.grid[agent.x][agent.y] == agent:
            # replace cell with empty if no furniture was just placed there
            self.grid[agent.x][agent.y] = None
        self.grid[newPosition[0]][newPosition[1]] = agent

        agent.x = newPosition[0]
        agent.y = newPosition[1]

        # agent.SetLastAction(action) # run only if true
        return True

    # returns object in given x,y or None is x,y is outside of the grid
    def GetCell(self, x: int, y: int) -> Union[ISimObj, None]:
        if x < 0 or y < 0 or x >= self.size[0] or y >= self.size[1]:
            return None
        return self.grid[x][y]


    # returns cell code for given x,y from CellCodes list
    def GetCellCode(self, x: int, y: int) -> int:
        if x < 0 or y < 0 or x >= self.size[0] or y >= self.size[1]:
            return CellCodes.Inaccessible
        cellObj = self.grid[x][y]
        if cellObj is None:
            return CellCodes.Empty
        return cellObj.GetCode(x, y)

    def AddAgent(self, x: int, y: int) -> bool:
        if self.grid[x][y] is not None:
            return False

        agent = Agent(x, y)
        self.grid[x][y] = agent
        self.agents.append(agent)
        return True

    def AddTable(self, x1: int, y1: int, x2: int, y2: int) -> bool:
        if self.grid[x1][y1] is not None:
            return False
        if self.grid[x2][y2] is not None:
            return False
        if (abs(x1-x2) + abs(y1-y2)) != 1:
            return False

        table = Table(x1, y1, x2, y2)
        self.grid[x1][y1] = table
        self.grid[x2][y2] = table
        self.tables.append(table)
        return True

    def AddChair(self, x: int, y: int) -> bool:
        if self.grid[x][y] is not None:
            return False

        chair = Chair(x, y)
        self.grid[x][y] = chair
        self.chairs.append(chair)
        return True

    # Validates document making sure all of the objects are in different cells and all cells have correct objects in them
    def validate(self) -> None:
        for agent in self.agents:
            cell = self.GetCell(agent.x, agent.y)
            assert(cell == agent)

        for table in self.tables:
            cell = self.GetCell(table.x1, table.y1)
            assert(cell == table)
            cell = self.GetCell(table.x2, table.y2)
            assert(cell == table)

        for chair in self.chairs:
            cell = self.GetCell(chair.x, chair.y)
            assert(cell == chair)

        for x in range(0, self.size[0]):
            for y in range(0, self.size[1]):
                cell = self.GetCell(x, y)
                assert(cell is None or cell in self.agents or cell in self.tables or cell in self.chairs)

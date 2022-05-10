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

    def moveActionGrabbedAgent(self, agent: Agent, direction: str) -> bool:
        assert(agent.grab is not None)

        agentPos = np.array([agent.x, agent.y])
        targetPosition = agentPos + Action.directionToVector(direction)
        targetCode = self.GetCellCode(targetPosition[0], targetPosition[1])

        grabbedPos = agentPos + Action.directionToVector(agent.grab)
        grabbedCode = self.GetCellCode(grabbedPos[0], grabbedPos[1])
        grabbedObj = self.GetCell(grabbedPos[0], grabbedPos[1])

        # target cell must be empty
        # TODO stronger check, what if many agents want to move to the same cell in the same step
        if targetCode != CellCodes.Empty and self.GetCell(targetPosition[0], targetPosition[1]) != grabbedObj:  
            return False


        assert(CellCodes.IsGrabbable(grabbedCode))

        objMoveSuccessful = False;
        # try to move grabbed object
        if grabbedCode == CellCodes.Chair:
            grabbedNewPos = grabbedPos + Action.directionToVector(direction)
            newPosCode = self.GetCellCode(grabbedNewPos[0], grabbedNewPos[1])
            newPosCell = self.GetCell(grabbedNewPos[0], grabbedNewPos[1])
            # moved chair will colide with st other that agent 
            if newPosCode != CellCodes.Empty and newPosCell != agent:
                objMoveSuccessful = False
            else:
                # move object
                objMoveSuccessful = True
                grabbedObj.x = grabbedNewPos[0]
                grabbedObj.y = grabbedNewPos[1]
                self.grid[grabbedPos[0]][grabbedPos[1]] = None
                self.grid[grabbedNewPos[0]][grabbedNewPos[1]] = grabbedObj

            # TODO: check if a table can be moved
        elif grabbedCode in [CellCodes.Table_min, CellCodes.Table_max]:
            if Table.required_agents != 1:
                assert(False)
                objMoveSuccessful = False    ## TODO

            grabbedTable : Table = grabbedObj
            grabbedPos1 = np.array([grabbedTable.x1, grabbedTable.y1])
            grabbedPos2 = np.array([grabbedTable.x2, grabbedTable.y2])
            grabbedNewPos1 = grabbedPos1 + Action.directionToVector(direction)
            grabbedNewPos2 = grabbedPos2 + Action.directionToVector(direction)

            newPos1Code = self.GetCellCode(grabbedNewPos1[0], grabbedNewPos1[1])
            newPos2Code = self.GetCellCode(grabbedNewPos2[0], grabbedNewPos2[1])
            newPos1Cell = self.GetCell(grabbedNewPos1[0], grabbedNewPos1[1])
            newPos2Cell = self.GetCell(grabbedNewPos2[0], grabbedNewPos2[1])

            # new positions must be empty or occupied by the same table or agent
            if (newPos1Code != CellCodes.Empty and newPos1Cell not in [grabbedTable, agent]) \
                or (newPos2Code != CellCodes.Empty and newPos2Cell not in [grabbedTable, agent]):
                objMoveSuccessful = False
            else:
                # move object
                objMoveSuccessful = True
                grabbedTable.x1 = grabbedNewPos1[0]
                grabbedTable.y1 = grabbedNewPos1[1]
                grabbedTable.x2 = grabbedNewPos2[0]
                grabbedTable.y2 = grabbedNewPos2[1]
                self.grid[grabbedPos1[0]][grabbedPos1[1]] = None
                self.grid[grabbedPos2[0]][grabbedPos2[1]] = None
                self.grid[grabbedNewPos1[0]][grabbedNewPos1[1]] = grabbedTable
                self.grid[grabbedNewPos2[0]][grabbedNewPos2[1]] = grabbedTable

        if objMoveSuccessful:
            if self.GetCell(agent.x, agent.y) != grabbedObj:    # issue when going opposite direction to grab direction
                self.grid[agent.x][agent.y] = None
            agent.x = targetPosition[0]
            agent.y = targetPosition[1]
            self.grid[agent.x][agent.y] = agent

            self.validate()
            return True
        else:
            return False

    def moveActionSoloAgent(self, agent: Agent, direction: str) -> bool:
        assert(agent.grab is None)

        agentPos = np.array([agent.x, agent.y])

        targetPosition = agentPos + Action.directionToVector(direction)
        
        targetCode = self.GetCellCode(targetPosition[0], targetPosition[1])

        # target cell must be empty
        if targetCode != CellCodes.Empty:   # TODO stronger check, what if many agents want to move to the same cell in the same step
            return False

        self.grid[agent.x][agent.y] = None
        agent.x = targetPosition[0]
        agent.y = targetPosition[1]
        self.grid[agent.x][agent.y] = agent

        return True

    def grabActionAgent(self, agent: Agent, direction: str) -> bool:
        if(agent.grab is not None):
            return False
        agentPos = np.array([agent.x, agent.y])

        targetPosition = agentPos + Action.directionToVector(direction)

        # check if there's furniture there
        target = self.GetCell(targetPosition[0], targetPosition[1])
        targetCode = self.GetCellCode(targetPosition[0], targetPosition[1])
        if not CellCodes.IsGrabbable(targetCode):
            return False

        # TODO: consider legal table-carrying configurations (can you only carry by holding short ends?)
        agent.grab = direction
        return True

    # returns true if action was valid and was performed, false otherwise
    def applyActionToAgent(self, agent: Agent, action: Action) -> bool:
        # initial safaty checks
        if action is None:
            return False
        inGridAgent = self.grid[agent.x][agent.y]
        assert(inGridAgent == agent)
        self.validate()



        actionRet = False;
        # carry out action
        if action.type == Action.release:
            actionRet = agent.grab is not None  # action is good only if agent grabbed object before
            agent.grab = None

        elif action.type == Action.move:
            # move to a different square
            if agent.grab:
                actionRet = self.moveActionGrabbedAgent(agent, action.direction)
            else:
                actionRet = self.moveActionSoloAgent(agent, action.direction)

        elif action.type == Action.grab:
            actionRet = self.grabActionAgent(agent, action.direction)

        self.validate()
        return actionRet

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
            if agent.grab is not None:
                grabbedDir = Action.directionToVector(agent.grab)
                grabbedPos = [agent.x + grabbedDir[0], agent.y + grabbedDir[1]]
                grabbedCode = self.GetCellCode(grabbedPos[0], grabbedPos[1])
                assert(CellCodes.IsGrabbable(grabbedCode))

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



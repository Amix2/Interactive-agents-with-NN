from random import randrange
from typing import Union

import numpy as np
from numpy.core.multiarray import empty
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

    def applyActionList(self, actionList: list):
        def sortFunc(agentAction):
            agent: Agent = agentAction[0]
            action: Action = agentAction[1]
            IDS = {
                Action.wait: 1,
                Action.release: 2,
                Action.move: 3,
                Action.grab: 4
                }
            actType = action.type
            return IDS[actType]
        actionList.sort(key=sortFunc)


        while len(actionList) > 0:
            validatedActionList = self.getValidatedActionGroup(actionList)
            self.validate()
            lastMoveAgentAction = None
            for agentAction in reversed(validatedActionList):
                agent: Agent = agentAction[0]
                action: Action = agentAction[1]
                if action.type == Action.move:
                    lastMoveAgentAction = agentAction
                    break

            for agentAction in validatedActionList:
                agent: Agent = agentAction[0]
                action: Action = agentAction[1]
                lastMoveAct = lastMoveAgentAction == agentAction
                applied = self.performActionToAgent(agent, action, True, lastMoveAct)
                if not applied:
                    iiiwe=0
                    actionGroupGood = self.validateActionGroup(validatedActionList)

                    applied = self.performActionToAgent(agent, action, True, lastMoveAct)
            self.fixGrid()
            self.validate()


    # pops first element of given list and returns minimal list of good actions all of which have to be performed
    def getValidatedActionGroup(self, actionList: list) -> list:
        actionGroup = self.getActionGroup(actionList)
        actionGroupGood = self.validateActionGroup(actionGroup)
        if actionGroupGood:
            return actionGroup
        return []

    # gets action group containing 1st action and all connected actions, removes those from the given list
    def getActionGroup(self, actionList: list) -> list:
        agentAction = actionList.pop(0);
        outList = [agentAction]
        agent: Agent = agentAction[0]
        action: Action = agentAction[1]
        if agent.grab is not None:
            grabbedObj = agent.grabbedObj
            for otherGrabber in grabbedObj.grabbed_by:
                it = 0
                while it < len(actionList):
                    agentAction = actionList[it]
                    if agentAction[0] == otherGrabber:
                        outList.append(agentAction)
                        actionList.pop(it)
                    else:
                        it = it + 1



        return outList
    
    # returns true if all of the actions are valid and can be performed as single move
    def validateActionGroup(self, actionGroup: list) -> bool:
        # ruch na pozycje okukowaną przez agenta w tej liście, który chce sie przesunąc 
        # all of the actions are valid on their own
        for agentAction in actionGroup:
            actionGood = self.validateAction(agentAction[0], agentAction[1])
            if not actionGood:
                return False

        # actions can be release or move all in the same direction
        moveDir = None
        moveActCount = 0
        for agentAction in actionGroup:
            agent: Agent = agentAction[0]
            action: Action = agentAction[1]
            if agent.grab is not None:
                if action.type == Action.move:
                    if moveDir is None or moveDir == action.direction:
                        moveDir = action.direction
                        moveActCount = moveActCount+1
                    else:
                        return False
                elif action.type == Action.release:
                    pass
                else:
                    return False
            else:
                if len(actionGroup) != 1:
                    teer = 0;
                    for agentAction in actionGroup:
                        actionGood = self.validateAction(agentAction[0], agentAction[1])
                        if not actionGood:
                            fdasdasdassda=0
                #assert(len(actionGroup) == 1)
        if agent.grab is not None:
            if agent.grabbedCode == CellCodes.Table_min or agent.grabbedCode == CellCodes.Table_max:
                if moveActCount < 2 and moveActCount > 0:
                    return False
        return True;


    def validateAction(self, agent: Agent, action: Action) -> bool:
        actionValid = self.performActionToAgent(agent, action, False,False)
        return actionValid

    def moveActionGrabbedAgent(self, agent: Agent, direction: str, applyToSelf: bool, applyToOthers: bool) -> bool:
        assert(agent.grab is not None)

        agentPos = np.array([agent.x, agent.y])
        targetPosition = agentPos + Action.directionToVector(direction)
        targetCode = self.GetCellCode(targetPosition[0], targetPosition[1])

        grabbedPos = agentPos + Action.directionToVector(agent.grab)
        grabbedCode = self.GetCellCode(grabbedPos[0], grabbedPos[1])
        grabbedObj = self.GetCell(grabbedPos[0], grabbedPos[1])
        if grabbedObj != agent.grabbedObj:
            grabbedCode = CellCodes.Empty
            grabbedObj = None

        if targetCode == CellCodes.Inaccessible:
            return False

        # target cell must be empty
        # TODO stronger check, what if many agents want to move to the same cell in the same step
        if targetCode != CellCodes.Empty and self.GetCell(targetPosition[0], targetPosition[1]) != grabbedObj:  
            return False

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
                if applyToOthers:
                    grabbedObj.x = grabbedNewPos[0]
                    grabbedObj.y = grabbedNewPos[1]
                    self.grid[grabbedPos[0]][grabbedPos[1]] = None
                    self.grid[grabbedNewPos[0]][grabbedNewPos[1]] = grabbedObj

            # TODO: check if a table can be moved
        elif grabbedCode in [CellCodes.Table_min, CellCodes.Table_max]:

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
                if applyToOthers:
                    grabbedTable.x1 = grabbedNewPos1[0]
                    grabbedTable.y1 = grabbedNewPos1[1]
                    grabbedTable.x2 = grabbedNewPos2[0]
                    grabbedTable.y2 = grabbedNewPos2[1]
                    self.grid[grabbedPos1[0]][grabbedPos1[1]] = None
                    self.grid[grabbedPos2[0]][grabbedPos2[1]] = None
                    self.grid[grabbedNewPos1[0]][grabbedNewPos1[1]] = grabbedTable
                    self.grid[grabbedNewPos2[0]][grabbedNewPos2[1]] = grabbedTable
        else:
            objMoveSuccessful = True

        if objMoveSuccessful and applyToSelf:
            if self.GetCell(agent.x, agent.y) != grabbedObj:    # issue when going opposite direction to grab direction
                self.grid[agent.x][agent.y] = None
            agent.x = targetPosition[0]
            agent.y = targetPosition[1]
            self.grid[agent.x][agent.y] = agent

        return objMoveSuccessful


    def moveActionSoloAgent(self, agent: Agent, direction: str, applyToSelf: bool, applyToOthers: bool) -> bool:
        assert(agent.grab is None)

        agentPos = np.array([agent.x, agent.y])

        targetPosition = agentPos + Action.directionToVector(direction)
        
        targetCode = self.GetCellCode(targetPosition[0], targetPosition[1])

        # target cell must be empty
        if targetCode != CellCodes.Empty:   # TODO stronger check, what if many agents want to move to the same cell in the same step
            return False
        if applyToSelf:
            self.grid[agent.x][agent.y] = None
            agent.x = targetPosition[0]
            agent.y = targetPosition[1]
            self.grid[agent.x][agent.y] = agent

        return True


    def grabActionAgent(self, agent: Agent, direction: str, applyToSelf: bool, applyToOthers: bool) -> bool:
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
        if applyToSelf:
            agent.grab = direction
            agent.grabbedCode = targetCode
            agent.grabbedObj = target

            target.grabbed_by.append(agent) # treated as a self move cos it doesnt affect other obj position 
        return True


    # returns true if action was valid and env state is changed if apply==True
    def performActionToAgent(self, agent: Agent, action: Action, applyToSelf: bool, applyToOthers: bool) -> bool:
        # initial safaty checks
        if action is None:
            return False
        inGridAgent = self.grid[agent.x][agent.y]
        assert(inGridAgent == agent)

        actionRet = False;
        # carry out action
        if action.type == Action.release:
            actionRet = agent.grab is not None  # action is good only if agent grabbed object before
            if agent.grab is not None:

                target = agent.grabbedObj

                if applyToSelf:
                    target.grabbed_by.remove(agent)

                    agent.grab = None
                    agent.grabbedCode = None
                    agent.grabbedObj = None


        elif action.type == Action.move:
            # move to a different square
            if agent.grab:
                actionRet = self.moveActionGrabbedAgent(agent, action.direction, applyToSelf, applyToOthers)
            else:
                actionRet = self.moveActionSoloAgent(agent, action.direction, applyToSelf, applyToOthers)

        elif action.type == Action.grab:
            actionRet = self.grabActionAgent(agent, action.direction, applyToSelf, applyToOthers)

        elif action.type == Action.wait:
            actionRet = True

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

    def fixGrid(self) -> None:
        self.grid = [[None for x in range(self.size[1])] for y in range(self.size[0])]
        for agent in self.agents:
            self.grid[agent.x][agent.y] = agent

        for table in self.tables:
            self.grid[table.x1][table.y1] = table
            self.grid[table.x2][table.y2] = table

        for chair in self.chairs:
            self.grid[chair.x][chair.y] = chair



    # Validates document making sure all of the objects are in different cells and all cells have correct objects in them
    def validate(self) -> None:
        for agent in self.agents:
            cell = self.GetCell(agent.x, agent.y)
            assert(cell == agent)
            if agent.grab is not None:
                grabbedDir = Action.directionToVector(agent.grab)
                grabbedPos = [agent.x + grabbedDir[0], agent.y + grabbedDir[1]]
                grabbedCode = self.GetCellCode(grabbedPos[0], grabbedPos[1])
                grabbedObj = self.GetCell(grabbedPos[0], grabbedPos[1])
                assert(CellCodes.IsGrabbable(grabbedCode))
                assert(grabbedObj is not None)
                assert(agent in grabbedObj.grabbed_by)
                assert(agent.grabbedCode == grabbedCode)
                assert(agent.grabbedObj == grabbedObj)

        for table in self.tables:
            cell = self.GetCell(table.x1, table.y1)
            assert(cell == table)
            cell = self.GetCell(table.x2, table.y2)
            assert(cell == table)
            for grabbedBy in table.grabbed_by:
                assert(grabbedBy.grab)
                grabbedDir = Action.directionToVector(grabbedBy.grab)
                grabbedPos = [grabbedBy.x + grabbedDir[0], grabbedBy.y + grabbedDir[1]]
                grabbedObj = self.GetCell(grabbedPos[0], grabbedPos[1])
                assert(grabbedObj == table)
                assert(grabbedBy.grabbedObj == table)

        for chair in self.chairs:
            cell = self.GetCell(chair.x, chair.y)
            assert(cell == chair)
            for grabbedBy in chair.grabbed_by:
                assert(grabbedBy.grab)
                grabbedDir = Action.directionToVector(grabbedBy.grab)
                grabbedPos = [grabbedBy.x + grabbedDir[0], grabbedBy.y + grabbedDir[1]]
                grabbedObj = self.GetCell(grabbedPos[0], grabbedPos[1])
                assert(grabbedObj == chair)
                assert(grabbedBy.grabbedObj == chair)


        for x in range(0, self.size[0]):
            for y in range(0, self.size[1]):
                cell = self.GetCell(x, y)
                assert(cell is None or cell in self.agents or cell in self.tables or cell in self.chairs)



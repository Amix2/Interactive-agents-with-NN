import random
from random import randrange
from typing import Union

import numpy as np
from numpy.core.multiarray import empty
from action import Action
from simObj import ISimObj
from agent import Agent
from chair import Chair
from table import Table
from cellCodes import CellCodes
from actionGroup import ActionGroup
from performedAction import PerformedAction


class Document:
    """
    Represents simulation state, collection of objects 
    """

    def __init__(self, sizeX: int, sizeY: int) -> None:
        self.size = np.array([sizeX, sizeY])
        self.agents: list[Agent] = list()
        self.tables: list[Table] = list()
        self.chairs: list[Chair] = list()
        self.grid: list[list[Union[None, ISimObj]]] = [[None for x in range(self.size[1])] for y in range(self.size[0])]
        self.step = 0

    def applyActionList(self, perfActionList: list[PerformedAction]):
        def sortFunc(perfAction: PerformedAction):
            action: Action = perfAction.action
            IDS = {
                Action.wait: 1,
                Action.release: 2,
                Action.move: 3,
                Action.grab: 4
            }
            actType = action.type
            return IDS[actType]

        perfActionList.sort(key=sortFunc)
        perfActListTemp = perfActionList.copy()
        self.step += 1
        while len(perfActListTemp) > 0:
            self.validate()

            perfActListCopy = perfActionList.copy()  # used to know what actions was performed in this loop iteration
            # its valid action group which can be applied to object
            # application can return false if action was useless, but they are all valid
            validActionGroup: ActionGroup = self.getValidatedActionGroup(perfActListTemp)
            actionSuccessful = self.performActionGroup(validActionGroup)
            usedAgents = list(set(perfActListCopy) - set(perfActListTemp))

            for agentAction in usedAgents:
                def find(perfAct: list[PerformedAction], item: PerformedAction) -> int:
                    for i, action in enumerate(perfAct):
                        if action.agent.x == item.agent.x and action.agent.y == item.agent.y:
                            return i
                    return -1

                perfActionList[find(perfActionList, agentAction)].success = actionSuccessful
                agent: Agent = agentAction.agent
                action: Action = agentAction.action

            self.fixGrid()
            self.validate()

    # pops first element of given list and returns minimal list of good actions all of which have to be performed
    def getValidatedActionGroup(self, actionList: list) -> ActionGroup:
        # contains 1 action and all objects (including tables/chairs)
        actionGroup: ActionGroup = self.getActionGroup(actionList)
        if actionGroup.action is None:
            return ActionGroup.empty()
        actionGroupGood = self.validateActionGroup(actionGroup)
        if actionGroupGood:
            return actionGroup
        return ActionGroup.empty()

    # gets action group containing 1st action and all connected actions, removes those from the given list
    def getActionGroup(self, actionList: list[PerformedAction]) -> ActionGroup:
        agentAction = actionList.pop(0)
        agent: Agent = agentAction.agent
        action: Action = agentAction.action
        if action.type != Action.move:
            # stationary action
            return ActionGroup(action, [agent])

        if agent.grab is None:
            # agent can do it on their own
            return ActionGroup(action, [agent])

        # we have to collect all the agents who grabbed the same object
        agentActionList = [agentAction]
        objectList = []
        agent: Agent = agentAction.agent
        action: Action = agentAction.action
        if agent.grab is not None:
            grabbedObj = agent.grabbedObj
            for otherGrabber in grabbedObj.grabbed_by:
                it = 0
                while it < len(actionList):
                    agentAction = actionList[it]
                    if agentAction.agent == otherGrabber:
                        agentActionList.append(agentAction)
                        actionList.pop(it)
                    else:
                        it = it + 1
            objectList.append(grabbedObj)
        # now we have all the move actions which want to move the same grabbed object - their direction must be the same
        modelAction = agentActionList[0].action
        direction = modelAction.direction

        for performedAct in agentActionList:
            thisDir = performedAct.action.direction
            if thisDir != direction:
                return ActionGroup.empty()
            objectList.append(performedAct.agent)

        # now we are sure that all agents want to do the same action on the same object
        return ActionGroup(modelAction, objectList)

    # returns true if all the actions are valid and can be performed as single move
    def validateActionGroup(self, actionGroup: ActionGroup) -> bool:
        action = actionGroup.action
        for obj in actionGroup.objects:
            if not obj.canPerformActionType(action):
                return False

        moveVec = Action.directionToVector(action.direction)
        if action.type == Action.move:
            # check for collisions with other objects in grid
            for obj in actionGroup.objects:
                pos = obj.getPositions()
                for x, y in pos:
                    newX = x + moveVec[0]
                    newY = y + moveVec[1]

                    # going outside the map
                    if self.getCellCode(newX, newY) == CellCodes.Inaccessible:
                        return False

                    collisionObj = self.getCell(newX, newY)
                    # collision with object which is not part of this action group
                    if collisionObj is not None and collisionObj not in actionGroup.objects:
                        return False

        # test if every agent holding chair or table is in this actionGroup
        for obj in actionGroup.objects:
            if isinstance(obj, Table) or isinstance(obj, Chair):
                for grabbedObj in obj.grabbed_by:
                    if grabbedObj not in actionGroup.objects:
                        return False
            if isinstance(obj, Table):
                if len(obj.grabbed_by) < 2:
                    return False
        return True

    def performActionGroup(self, actionGroup: ActionGroup) -> bool:
        """Perform action without changing grid"""
        action = actionGroup.action
        actionSuccessful = False
        for obj in actionGroup.objects:
            if isinstance(obj, Agent):
                actionSuccessful = self.performActionOnAgent(action, obj)
            elif isinstance(obj, Table):
                actionSuccessful = self.performActionOnTable(action, obj)
            elif isinstance(obj, Chair):
                actionSuccessful = self.performActionOnChair(action, obj)
            else:
                raise NotImplementedError
        return actionSuccessful

    def performActionOnAgent(self, action: Action, agent: Agent) -> bool:
        def waitAction(action: Action, agent: Agent) -> bool:
            return True

        def releaseAction(action: Action, agent: Agent) -> bool:
            wasHolding = agent.grab is not None
            if agent.grab is not None:
                target = agent.grabbedObj
                assert (target is not None)
                assert (agent in target.grabbed_by)

                target.grabbed_by.remove(agent)
                agent.grab = None
                agent.grabbedCode = None
                agent.grabbedObj = None
            return wasHolding

        def grabAction(action: Action, agent: Agent) -> bool:
            if agent.grab is not None:
                return False

            agentPos = np.array([agent.x, agent.y])
            targetPosition = agentPos + Action.directionToVector(action.direction)

            # check if there's furniture there
            target = self.getCell(targetPosition[0], targetPosition[1])
            targetCode = self.getCellCode(targetPosition[0], targetPosition[1])
            if not CellCodes.IsGrabbable(targetCode):
                return False

            agent.grab = action.direction
            agent.grabbedCode = targetCode
            agent.grabbedObj = target
            target.grabbed_by.append(agent)
            return True

        def moveAction(action: Action, agent: Agent) -> bool:
            pos = np.array([agent.x, agent.y])
            target = pos + Action.directionToVector(action.direction)
            agent.x = target[0]
            agent.y = target[1]
            return True

        if action.type == Action.wait:
            return waitAction(action, agent)
        elif action.type == Action.release:
            return releaseAction(action, agent)
        elif action.type == Action.grab:
            return grabAction(action, agent)
        elif action.type == Action.move:
            return moveAction(action, agent)

        raise NotImplementedError

    def performActionOnTable(self, action: Action, table: Table) -> bool:
        assert (action.type == Action.move)
        if action.type == Action.move:
            pos1 = np.array([table.x1, table.y1])
            pos2 = np.array([table.x2, table.y2])
            target1 = pos1 + Action.directionToVector(action.direction)
            target2 = pos2 + Action.directionToVector(action.direction)
            table.x1 = target1[0]
            table.y1 = target1[1]
            table.x2 = target2[0]
            table.y2 = target2[1]
            return True
        return False

    def performActionOnChair(self, action: Action, chair: Chair) -> bool:
        assert(action.type == Action.move)
        if action.type == Action.move:
            pos = np.array([chair.x, chair.y])
            target = pos + Action.directionToVector(action.direction)
            chair.x = target[0]
            chair.y = target[1]
            return True
        return False

    # returns object in given x,y or None is x,y is outside of the grid
    def getCell(self, x: int, y: int) -> Union[ISimObj, None]:
        if x < 0 or y < 0 or x >= self.size[0] or y >= self.size[1]:
            return None
        return self.grid[x][y]

    # returns cell code for given x,y from CellCodes list
    def getCellCode(self, x: int, y: int) -> int:
        if x < 0 or y < 0 or x >= self.size[0] or y >= self.size[1]:
            return CellCodes.Inaccessible
        cellObj = self.grid[x][y]
        if cellObj is None:
            return CellCodes.Empty
        return cellObj.getCode(x, y)

    def addAgent(self, x: int, y: int) -> bool:
        if self.grid[x][y] is not None:
            return False

        agent = Agent(x, y)
        self.grid[x][y] = agent
        self.agents.append(agent)
        return True

    def addTable(self, x1: int, y1: int, x2: int, y2: int) -> bool:
        if self.grid[x1][y1] is not None:
            return False
        if self.grid[x2][y2] is not None:
            return False
        if (abs(x1 - x2) + abs(y1 - y2)) != 1:
            return False

        table = Table(x1, y1, x2, y2)
        self.grid[x1][y1] = table
        self.grid[x2][y2] = table
        self.tables.append(table)
        return True

    def addChair(self, x: int, y: int) -> bool:
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
            cell = self.getCell(agent.x, agent.y)
            assert (cell == agent)
            if agent.grab is not None:
                grabbedDir = Action.directionToVector(agent.grab)
                grabbedPos = [agent.x + grabbedDir[0], agent.y + grabbedDir[1]]
                grabbedCode = self.getCellCode(grabbedPos[0], grabbedPos[1])
                grabbedObj = self.getCell(grabbedPos[0], grabbedPos[1])
                assert (CellCodes.IsGrabbable(grabbedCode))
                assert (grabbedObj is not None)
                assert (agent in grabbedObj.grabbed_by)
                assert (agent.grabbedCode == grabbedCode)
                assert (agent.grabbedObj == grabbedObj)

        for table in self.tables:
            cell = self.getCell(table.x1, table.y1)
            assert (cell == table)
            cell = self.getCell(table.x2, table.y2)
            assert (cell == table)

            for grabbedBy in table.grabbed_by:
                assert (grabbedBy.grab)
                grabbedDir = Action.directionToVector(grabbedBy.grab)
                grabbedPos = [grabbedBy.x + grabbedDir[0], grabbedBy.y + grabbedDir[1]]
                grabbedObj = self.getCell(grabbedPos[0], grabbedPos[1])
                assert (grabbedObj == table)
                assert (grabbedBy.grabbedObj == table)

        for chair in self.chairs:
            cell = self.getCell(chair.x, chair.y)
            assert (cell == chair)

            for grabbedBy in chair.grabbed_by:
                assert (grabbedBy.grab)
                grabbedDir = Action.directionToVector(grabbedBy.grab)
                grabbedPos = [grabbedBy.x + grabbedDir[0], grabbedBy.y + grabbedDir[1]]

                grabbedObj = self.getCell(grabbedPos[0], grabbedPos[1])
                assert (grabbedObj == chair)
                assert (grabbedBy.grabbedObj == chair)

        for x in range(0, self.size[0]):
            for y in range(0, self.size[1]):
                cell = self.getCell(x, y)
                assert (cell is None or cell in self.agents or cell in self.tables or cell in self.chairs)

    @staticmethod
    def getRandom(sizeX: int, sizeY: int, n_tables: int, n_chairs: int, n_agents: int) -> 'Document':
        doc = Document(sizeX, sizeY)

        placed_tables = 0
        while placed_tables < n_tables:
            table_dir = random.choice(["V", "H"])

            if table_dir == "V":
                x1 = random.randint(0, sizeX-1)
                y1 = random.randint(0, sizeY-2)
                x2 = x1
                y2 = y1+1

            else:  # table_dir == "H"
                x1 = random.randint(0, sizeX - 2)
                y1 = random.randint(0, sizeY - 1)
                x2 = x1 + 1
                y2 = y1

            if doc.addTable(x1, y1, x2, y2):
                placed_tables += 1

        placed_chairs = 0
        while placed_chairs < n_chairs:
            x = random.randint(0, sizeX-1)
            y = random.randint(0, sizeY-1)

            if doc.addChair(x, y):
                placed_chairs += 1

        placed_agents = 0
        while placed_agents < n_agents:
            x = random.randint(0, sizeX - 1)
            y = random.randint(0, sizeY - 1)

            if doc.addAgent(x, y):
                placed_agents += 1

        return doc


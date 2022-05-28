import math
import random
from typing import Union

from action import Action
from agentView import AgentView
from cellCodes import CellCodes
from simObj import ISimObj


class Agent(ISimObj):
    def __init__(self, x: int, y: int, actionMemorySize: int = 5) -> None:
        super().__init__()
        self.x = x
        self.y = y
        self.grab: str = None
        self.grabbedCode: str = None
        self.grabbedObj: ISimObj = None

        self.grab: Union[str, None] = None
        self._actionMemorySize = actionMemorySize
        self.actionMemory: list[Union[tuple[Action, bool], None]] = [None]*self._actionMemorySize

    def getCode(self, x: int, y: int) -> int:
        assert(x == self.x and y == self.y)
        if self.grab:
            if self.grab == Action.north:
                return CellCodes.Agent_grabbedN
            if self.grab == Action.south:
                return CellCodes.Agent_grabbedS
            if self.grab == Action.east:
                return CellCodes.Agent_grabbedE
            if self.grab == Action.west:
                return CellCodes.Agent_grabbedW
        return CellCodes.Agent_standing

    def getPositions(self) -> list[tuple[int, int]]:
        """Returns list of all the occupied positions"""
        return [(self.x, self.y)]

    def canPerformActionType(self, action: Action) -> bool:
        """Returns true if object is capable of performing given action in their correct state ignoring surroundings """
        if action.type == Action.wait:
            return True
        elif action.type == Action.release:
            return self.grab is not None
        elif action.type == Action.grab:
            return self.grab is None
        elif action.type == Action.move:
            return True
        raise NotImplementedError

    def selectActions(self, agentView: AgentView) -> list[Action]:
        # TODO implement
        actions = Action.getAll()
        return actions

    def addToMemory(self, action: Action, succeeded: bool) -> None:
        self.actionMemory.pop(0)
        self.actionMemory.append((action, succeeded))

    def getLastAction(self):
        return self.actionMemory[self._actionMemorySize-1]

    def bid(self, action: Action, agentView: AgentView) -> float:
        # TODO implement
        return random.random()

    def L(self, actionList: list[tuple], reward: float) -> None:
        # TODO: implement the learning function for action selecting
        action: Action
        succeeded: bool
        if self.getLastAction() is None:
            return
        action, succeeded = self.getLastAction()
        pass

    def Q(self, actionList: list[tuple], reward: float) -> None:
        # TODO: implement
        action: Action
        succeeded: bool
        if self.getLastAction() is None:
            return
        action, succeeded = self.getLastAction()
        pass

    def distanceTo(self, agent) -> float:
        return math.sqrt((self.x-agent.x) * (self.x-agent.x) + (self.y-agent.y) * (self.y-agent.y))

from action import Action
from cellCodes import CellCodes
from simObj import ISimObj
from agent import Agent


class Chair(ISimObj):
    def __init__(self, x: int, y: int) -> None:
        super().__init__()
        self.x = x
        self.y = y
        self.grabbed_by: list[Agent] = []

    def getCode(self, x: int, y: int) -> int:
        assert(x == self.x and y == self.y)
        return CellCodes.Chair

    def getPositions(self) -> list[tuple[int, int]]:
        """Returns list of all the occupied positions"""
        return [(self.x, self.y)]

    def canPerformActionType(self, action: Action) -> bool:
        """Returns true if object is capable of performing given action in their correct state ignoring surroundings """
        if action.type == Action.wait:
            return False
        elif action.type == Action.release:
            return False
        elif action.type == Action.grab:
            return False
        elif action.type == Action.move:
            return len(self.grabbed_by) > 0
        raise NotImplementedError

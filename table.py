from action import Action
from cellCodes import CellCodes
from simObj import ISimObj
from agent import Agent


class Table(ISimObj):
    def __init__(self, x1: int, y1: int, x2: int, y2: int) -> None:
        assert ((abs(x1 - x2) == 1 and y1 == y2)
                or (abs(y1 - y2) == 1 and x1 == x2))
        super().__init__()
        # x1 and y1 represent the lower or left side of the table
        self.x1 = min(x1, x2)
        self.y1 = min(y1, y2)
        self.x2 = max(x1, x2)
        self.y2 = max(y1, y2)
        self.grabbed_by: list[Agent] = []

    def getCode(self, x: int, y: int) -> int:
        assert((x == self.x1 and y == self.y1) or (x == self.x2 and y == self.y2))
        if x == self.x1 and y == self.y1:
            return CellCodes.Table_min
        return CellCodes.Table_max

    def getPositions(self) -> list[tuple[int, int]]:
        """Returns list of all the occupied positions"""
        return [(self.x1, self.y1), (self.x2, self.y2)]

    def canPerformActionType(self, action: Action) -> bool:
        """Returns true if object is capable of performing given action in their correct state ignoring surroundings """
        if action.type == Action.wait:
            return False
        elif action.type == Action.release:
            return False
        elif action.type == Action.grab:
            return False
        elif action.type == Action.move:
            return len(self.grabbed_by) > 1
        raise NotImplementedError

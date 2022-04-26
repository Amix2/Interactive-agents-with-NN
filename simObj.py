from action import Action
from cellCodes import CellCodes

class ISimObj:

    def __init__(self) -> None:
        self.last_action = None

    def SetLastAction(self, action: Action) -> None:
        self.last_action = action;

    def GetCode(self, x: int, y: int) -> int:
        raise NotImplementedError

class Agent(ISimObj):

    def __init__(self, x: int, y: int) -> None:
        super().__init__()
        self.x = x
        self.y = y

    def GetCode(self, x: int, y: int) -> int:
        assert(x == self.x and y == self.y)
        if(self.last_action != None and self.last_action.type == "G"):
            if(self.last_action.direction == "N"):
                return CellCodes.Agent_grabbedN
            elif(self.last_action.direction == "S"):
                return CellCodes.Agent_grabbedS
            elif(self.last_action.direction == "E"):
                return CellCodes.Agent_grabbedE
            elif(self.last_action.direction == "W"):
                return CellCodes.Agent_grabbedW
        return CellCodes.Agent_standing


class Table(ISimObj):

    def __init__(self, x1: int, y1: int, x2: int, y2: int) -> None:
        assert(abs(x1-x2) + abs(y1-y2) == 1)
        super().__init__()
        # x1 and y1 represent smaller point 
        self.x1 = min(x1, x2);
        self.y1 = min(y1, y2)
        self.x2 = max(x1, x2);
        self.y2 = max(y1, y2);

    def GetCode(self, x: int, y: int) -> int:
        assert((x == self.x1 and y == self.y1) or (x == self.x2 and y == self.y2))
        if(x == self.x1 and y == self.y1):
            return CellCodes.Table_min
        return CellCodes.Table_max


class Chair(ISimObj):

    def __init__(self, x: int, y: int) -> None:
        super().__init__()
        self.x = x
        self.y = y

    def GetCode(self, x: int, y: int) -> int:
        assert(x == self.x and y == self.y)
        return CellCodes.Chair
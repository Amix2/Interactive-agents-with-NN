from action import Action
from cellCodes import CellCodes


class ISimObj:
    # is keeping the last action necessary?
    # def __init__(self) -> None:
    #     self.last_action = None
    #
    # def SetLastAction(self, action: Action) -> None:
    #     self.last_action = action

    def GetCode(self, x: int, y: int) -> int:
        raise NotImplementedError


class Agent(ISimObj):
    def __init__(self, x: int, y: int) -> None:
        super().__init__()
        self.x = x
        self.y = y
        self.grab: str= None

    def GetCode(self, x: int, y: int) -> int:
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


class Table(ISimObj):

    # TODO change it after proper validation 
    required_agents = 1 # how many agents are required to move table

    def __init__(self, x1: int, y1: int, x2: int, y2: int) -> None:
        assert((abs(x1-x2) == 1 and y1 == y2)
               or (abs(y1-y2) == 1 and x1 == x2))
        super().__init__()
        # x1 and y1 represent the lower or left side of the table
        self.x1 = min(x1, x2)
        self.y1 = min(y1, y2)
        self.x2 = max(x1, x2)
        self.y2 = max(y1, y2)
        self.grabbed_by : list[Agent] = []

    def GetCode(self, x: int, y: int) -> int:
        assert((x == self.x1 and y == self.y1) or (x == self.x2 and y == self.y2))
        if x == self.x1 and y == self.y1:
            return CellCodes.Table_min
        return CellCodes.Table_max


class Chair(ISimObj):

    def __init__(self, x: int, y: int) -> None:
        super().__init__()
        self.x = x
        self.y = y
        self.grabbed_by : list[Agent] = []


    def GetCode(self, x: int, y: int) -> int:
        assert(x == self.x and y == self.y)
        return CellCodes.Chair


class ISimObj:
    pass

class Agent(ISimObj):
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

class Table(ISimObj):
    def __init__(self, x1: int, y1: int, x2: int, y2: int) -> None:
        self.x1 = x1;
        self.y1 = y1
        self.x2 = x2;
        self.y2 = y2;
        pass


class Chair(ISimObj):
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y
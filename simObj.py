
class ISimObj:
    pass


class Agent(ISimObj):
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y


class Table(ISimObj):
    def __init__(self) -> None:
        pass


class Chair(ISimObj):
    def __init__(self) -> None:
        pass

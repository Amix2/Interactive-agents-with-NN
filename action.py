from typing import Union
import random

class Action:
    grab = "G"
    move = "M"
    release = "R"
    wait = "W"

    _valid_types = [grab, move, release, wait]
    _directed_types = [grab, move]

    north = "N"
    west  = "W"
    east  = "E"
    south = "S"

    _valid_directions = [north, west, east, south]

    def __init__(self, type: str, direction: Union[str, None] = None):
        if type not in Action._valid_types:
            raise ValueError("not a valid action type.")

        if direction is not None and direction not in Action._valid_directions:
            raise ValueError("not a valid direction.")

        if direction is None and type in Action._directed_types:
            raise ValueError("this action type requires a direction.")

        self.type = type
        self.direction = direction

    @staticmethod
    def directionToVector(direction: str):
        if direction == Action.north:
            return [0, 1]
        if direction == Action.south:
            return [0, -1]
        if direction == Action.east:
            return [1, 0]
        if direction == Action.west:
            return [-1, 0]

    @staticmethod
    def makeRandom():
        while True:
            try:
                aType = random.choice(Action._valid_types)        
                aDir = random.choice(Action._valid_directions + [None])
                action = Action(aType, aDir)
            except ValueError:
                return Action(Action.wait)
            else:
                return action

    @staticmethod
    def getAll() -> list:
        return [
            Action(Action.grab, Action.north),
            Action(Action.grab, Action.east),
            Action(Action.grab, Action.south),
            Action(Action.grab, Action.west),
            Action(Action.move, Action.north),
            Action(Action.move, Action.east),
            Action(Action.move, Action.south),
            Action(Action.move, Action.west),
            Action(Action.wait),
            Action(Action.release),
            ]
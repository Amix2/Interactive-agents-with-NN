from typing import Union


class Action:
    grab = "G"
    move = "M"
    release = "R"
    wait = "W"

    _valid_types = [grab, move, release, wait]
    _directed_types = [grab, move]

    north = "N"
    west = "W"
    east = "E"
    south = "S"

    _valid_directions = [north, west, east, south]

    def __init__(self, type: str, direction: Union[str, None]):
        if type not in Action._valid_types:
            raise ValueError("not a valid action type.")

        if direction is not None and direction not in Action._valid_directions:
            raise ValueError("not a valid direction.")

        if direction is None and type in Action._directed_types:
            raise ValueError("this action type requires a direction.")

        self.type = type
        self.direction = direction

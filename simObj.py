from action import Action


class ISimObj:
    def getCode(self, x: int, y: int) -> int:
        raise NotImplementedError

    def getPositions(self) -> list[tuple[int, int]]:
        """Returns list of all the occupied positions"""
        raise NotImplementedError

    def canPerformActionType(self, action: Action) -> bool:
        """Returns true if object is capable of performing given action in their correct state ignoring surroundings """
        raise NotImplementedError



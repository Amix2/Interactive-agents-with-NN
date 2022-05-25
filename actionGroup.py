from action import Action
from simObj import ISimObj


class ActionGroup:
    """
    Single action which applies to every object in a group, its the only proper way to perform actions in document
    """
    def __init__(self, action: Action, objects: list[ISimObj]):
        self.action = action
        self.objects: list[ISimObj] = objects

    @staticmethod
    def empty():
        return ActionGroup(None, [])  # empty action group

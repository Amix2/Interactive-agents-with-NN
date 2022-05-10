class CellCodes:
    """
    Storage for codes for every cells used throughout a program
    """
    Inaccessible = 0
    Empty = 1
    Agent_standing = 2
    Agent_grabbedN = 3
    Agent_grabbedS = 4
    Agent_grabbedE = 5
    Agent_grabbedW = 6
    Chair = 7
    Table_min = 8
    Table_max = 9

    @staticmethod
    def IsGrabbable(code: int) -> bool:
        return code in [CellCodes.Chair, CellCodes.Table_min, CellCodes.Table_max]
# following 3 lines are a workaround for avoiding circular deps with typing-related imports
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from document import Document


class AgentView:
    """
    Uses Document::GetCellCode() to collect cells around given position 
    """
    def __init__(self, doc: Document, x: int, y: int, size: int = 9) -> None:
        self.size = size
        self.data = []
        d = int(size / 2)
        for iy in range(-d, d+1):
            for ix in range(-d, d+1):
                self.data.append(doc.getCellCode(x + ix, y + iy))

    def GetData(self, x: int, y: int) -> int:
        return self.data[x + y * self.size]

    def ToPrettyString(self) -> str:
        out = "=====\n"
        for y in range(0, self.size):
            out += "[ "
            for x in range(0, self.size):
                out += str(self.GetData(x, y))
            out += " ]\n"
        out += "=====\n"
        return out

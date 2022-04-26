from document import Document

class AgentView:
    """
    Uses Document::GetCellCode() to collect cells around given position 
    """
    def __init__(self, doc: Document, x: int, y: int, size: int = 9) -> None:
        self.size = size
        self.data = []
        d = int(size / 2)
        for iy in range(-d,d+1):
            for ix in range(-d,d+1):
                self.data.append(doc.GetCellCode(x+ix, y+iy))
    

    def GetData(self, x:int, y:int) -> int:
        return self.data[x + y * self.size]


    def ToPrettyString(self) -> str:
        out = "=====\n"
        for y in range(0,self.size):
            out += "[ "
            for x in range(0,self.size):
                out += str(self.GetData(x,y))
            out += " ]\n"
        out += "=====\n"
        return out

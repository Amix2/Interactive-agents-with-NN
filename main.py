from document import Document
from model import Model
from screen import Screen
import time


def main():
    timeStepInterval = 0.2  # [s]

    doc = Document(5,5)
    screen = Screen()
    model = Model()
    doc.AddAgent(4,4)
    doc.AddChair(2, 2)
    doc.AddTable(3, 3, 3, 4)
    #doc.AddTable(4,3, 4, 2)

    nextSimStepTime = time.time()
    while True:  # the main game loop
        nowTime = time.time()
        if nextSimStepTime <= nowTime:
            nextSimStepTime = nowTime + timeStepInterval
            model.step(doc)
        screen.update(doc)


if __name__ == "__main__":
    main()

from document import Document
from model import Model
from screen import Screen
import time


def main():
    timeStepInterval = 0.2  # [s]

    doc = Document(15, 10)
    screen = Screen()
    model = Model()
    doc.AddAgent(5, 5)
    doc.AddChair(2, 2)
    doc.AddTable(3, 3, 3, 4)

    nextSimStepTime = time.time()
    while True:  # the main game loop
        nowTime = time.time()
        if nextSimStepTime <= nowTime:
            nextSimStepTime = nowTime + timeStepInterval
            model.step(doc)
            screen.update(doc)


if __name__ == "__main__":
    main()

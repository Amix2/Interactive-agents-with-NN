from document import Document
from model import Model
from screen import Screen
import time

def main():
    timeStepInterval = 0.5 # [s]

    doc = Document(15, 10)
    screen = Screen()
    model = Model()
    doc.AddAgent(5,5)
    nextSimStepTime = 0
    while True: # the main game loop
        nowTime = time.time()
        if(nextSimStepTime < nowTime):
            nextSimStepTime = nowTime + timeStepInterval
            model.Step(doc)
        screen.Update(doc)

if __name__ == "__main__":
    main()
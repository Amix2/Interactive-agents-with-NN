from document import Document
from model import Model
from screen import Screen
import time
import pygame, sys


def main():
    timeStepInterval = 0.2  # [s]

    screen = Screen()
    model = Model()

    # doc = Document(5,5)
    # doc.addAgent(1, 2)
    # doc.addAgent(2, 1)
    # doc.addAgent(4, 0)
    # doc.addAgent(4, 2)
    # doc.addChair(2, 2)
    # doc.addChair(4, 1)
    # doc.addChair(1, 4)
    # doc.addTable(3, 3, 3, 4)
    # doc.addTable(0, 1, 1, 1)

    doc = Document.getRandom(5, 5, 2, 3, 2)

    Screen.FPS = 1/timeStepInterval
                    

    nextSimStepTime = time.time()
    while True:  # the main game loop

        #handle events 
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f: # fast mode 
                    timeStepInterval *= -1
                    if timeStepInterval <= 0:
                        Screen.FPS = 200
                    else:
                        Screen.FPS = 1/timeStepInterval
                        
            elif event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        nowTime = time.time()
        if nextSimStepTime <= nowTime:
            nextSimStepTime = nowTime + timeStepInterval
            model.step(doc)

        screen.update(doc)


if __name__ == "__main__":
    main()

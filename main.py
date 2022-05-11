from document import Document
from model import Model
from screen import Screen
import time
import pygame, sys


def main():
    timeStepInterval = 0.2  # [s]

    doc = Document(5, 5)
    screen = Screen()
    model = Model()
    doc.AddAgent(1, 1)
    #doc.AddAgent(2, 1)
    doc.AddChair(2, 2)
    doc.AddChair(4, 1)
    doc.AddChair(1, 4)
    doc.AddTable(3, 3, 3, 4)
    doc.AddTable(0, 0, 1, 0)
                    

    nextSimStepTime = time.time()
    while True:  # the main game loop

        #handle events 
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f: # fast mode 
                    timeStepInterval *= -1
                    if timeStepInterval <= 0:
                        Screen.FPS = 100
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

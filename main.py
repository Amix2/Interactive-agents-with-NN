from math import pi
from pygame.locals import *
from document import Document

from screen import Screen
def main():
    doc = Document()
    screen = Screen(doc)

    while True: # the main game loop
        screen.Update()

if __name__ == "__main__":
    main()
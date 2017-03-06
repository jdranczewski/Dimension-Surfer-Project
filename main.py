# Import the pygame library.
import pygame

def main():
    # Initialize the pygame environment.
    pygame.init()

    # Set the width and height of the screen.
    size = (500, 500)
    screen = pygame.display.set_mode(size)

    # Set the title of the window.
    pygame.display.set_caption("My Game")

    # This variable stores whether the user pressed the close button on the window.
    done = False

    # An object used to manage how fast the screen updates.
    clock = pygame.time.Clock()

    # Main program loop, runs until the close button is pressed.
    while not done:
        # Event processing - we iterate on the events given to us by pygame:
        for event in pygame.event.get():
            # If the event type is QUIT, the user wants to close the window.
            # So we set done to True.
            if event.type == pygame.QUIT:
                done = True
        # Game logic:

        # Do the drawing:
        screen.fill((255, 255, 255))

        # Update the screen:
        pygame.display.flip()

        # Show the frame rate in the title for performance checking.
        pygame.display.set_caption(str(clock.get_fps()))
        # Set the desired frame rate to 60fps (frames per second.
        clock.tick(60)

    # Close the window when the main loop finishes.
    pygame.quit()

if __name__ == "__main__":
    main()

# Import the pygame library.
import pygame
import math


class ThreeDMesh():
    def __init__(self, id, baseColour, maxColour):
        self.id = id
        self.data = self.importData()
        self.z = 250
        self.baseColour = baseColour
        self.maxColour = maxColour
        self.currentColour = baseColour

    # This method will import polygon data from a text file.
    def importData(self):
        # Create an empty list for the data.
        data = [[[]]]
        # Create indexes that will help iterate over polygons and the third dimension.
        polygonIndex = 0
        zIndex = 0
        # Open file specified by the id.
        with open('level_data/' + self.id + ".txt", 'r') as f:
            # Parse every line in the file.
            for line in f:
                if line == "#\n":
                    # If line contains a '#' it means that the data about a particular
                    # cross section has just finished. Create a new sublist
                    # for the next cross section.
                    data[zIndex].pop()
                    data.append([[]])
                    # We move to the next cross section, so we increase the zIndex.
                    zIndex += 1
                    # We have not added any polygons to this cross section yet,
                    # so we reset the polygonIndex to 0.
                    polygonIndex = 0
                elif line == "\n":
                    # If the line is emty, that means that we reached the end of
                    # a single polygon's description. We create a sublist to hold
                    # the next polygon...
                    data[zIndex].append([])
                    # ...and change the polygonIndex to indicate that we moved to
                    # the next polygon.
                    polygonIndex += 1
                else:
                    # If the line is neither empty nor it has a '#' in it,
                    # we assume that it contains coordinates of a point.
                    # We add this point to a polygon indicated by polygonIndex
                    # in the crossSection indicated by the zIndex.
                    data[zIndex][polygonIndex].append([float(x) for x in line.split(" ")])
            # The pop() functions throughout the code are to get rid of unpopulated
            # lists that occur naturally due to the construction of the data format.
            data.pop()
        # Close the file...
        f.closed
        # ...and return the processed data array.
        return data

    # This method will draw a cross-section specified by self.z
    def draw(self, screen):
        # This is a set of polygons in the cross-section that
        # we will be drawing:
        drawing = self.data[math.floor(self.z)]
        # We iterate on the elements of the drawing list,
        # which are lists of vertices...
        for polygon in drawing:
            # ...and pass them to the drawing function.
            pygame.draw.polygon(screen, self.currentColour, polygon)

    # This method will update the self.y attribute based on
    # the mouse y coordinate.
    def update(self, mouse_y):
        # Calculate the difference between the mouse position
        # and the current z position.
        diff = mouse_y - self.z
        # If the difference is bigger than 50,
        # limit the transition speed.
        if abs(diff) > 50:
            # abs(diff)/diff is used to copy the sign of diff.
            diff = 50 * abs(diff) / diff
        # Add a fraction of the difference to self.z.
        self.z += diff * 0.1
        # Set the currentColour based on self.z.
        self.currentColour = (calculateColour(self.baseColour[0], self.maxColour[0], self.z), calculateColour(self.baseColour[1], self.maxColour[1], self.z), calculateColour(self.baseColour[2], self.maxColour[2], self.z))

    # Other methods will go here...

# The simplified Player class for testing purposes.
class Player():
    def __init__(self, x, y, width, height):
        # Set the attributes to the values given.
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        # Create the vertices list
        self.vertices = []

    # Update the position every refresh based on mouse position.
    def update(self, mouse_x, mouse_y):
        # Set the coordinates to the mouse coordinates.
        self.x = mouse_x
        self.y = mouse_y
        # Calculate the coordinates of the rectangle's vertices.
        self.vertices = [[self.x, self.y], [self.x + self.width, self.y], [self.x + self.width, self.y + self.height], [self.x, self.y + self.height]]

    # Draw the Player.
    def draw(self, screen):
        # Use pygame's built in draw rectangle function.
        pygame.draw.rect(screen, (0, 0, 0), [self.x, self.y, self.width, self.height])

# Calculate the colour component based on the z position.
def calculateColour(min, max, z):
    return min + z/500 * (max-min)

# Project a given polygon onto an axis.
def project(polygon, normal):
    # Create a list of projected vertices.
    projected = []
    # We treat each vertex coordinates as a position vector
    # and iterate on them.
    for vect in polygon:
        # Calculate the dot product of the position vector and the axis vector.
        dp = vect[0] * normal[0] + vect[1] * normal[1]
        # Calculate the projection of the position vector on the axis.
        projected_v = [normal[0] * dp, normal[1] * dp]
        # Calculate the projection's length - this is what we actually need.
        projected_l = math.sqrt(projected_v[0] ** 2 + projected_v[1] ** 2)
        # Get the direction of the projection relative to the axis direction.
        sign_p = projected_v[0] * normal[0] + projected_v[1] * normal[1]
        # Apply the direction to the projected length.
        projected_l = projected_l * (sign_p / abs(sign_p))
        # Append the calculated projection to the list of projected vertices.
        projected.append(projected_l)
    # After all vertices are processed, return the boundaries of the projection.
    return [min(projected), max(projected)]

# Check whether there is overlap.
def checkOverlap(obstacle, player, normal):
    # Project the player and the obstacle onto the axis given by the normal vector.
    obstacle_p = project(obstacle, normal)
    player_p = project(player, normal)
    # Test for overlap.
    if (obstacle_p[1] < player_p[0]) or (obstacle_p[0] > player_p[1]):
        # If the above condition is true, it means that the projections do not overlap.
        return False
    else:
        # Else, it means that there is overlap.
        return True

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

    # A simple ThreeDMesh for testing purposes.
    mesh = ThreeDMesh("1", (0,0,255), (0,255,0))
    player = Player(0,0,20,20)

    # Main program loop, runs until the close button is pressed.
    while not done:
        # Event processing - we iterate on the events given to us by pygame:
        for event in pygame.event.get():
            # If the event type is QUIT, the user wants to close the window.
            # So we set done to True.
            if event.type == pygame.QUIT:
                done = True
        # Get the mouse coordinates.
        pos = pygame.mouse.get_pos()
        mouse_x = pos[0]
        mouse_y = pos[1]

        # Game logic:
        # Update the mesh.
        # mesh.update(mouse_y)
        player.update(mouse_x,mouse_y)

        # Do the drawing:
        screen.fill((255, 255, 255))
        mesh.draw(screen)
        player.draw(screen)

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
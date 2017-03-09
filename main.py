# Import the pygame library.
import pygame
import math
# Import the Separating Axis Theorem library
import sat


class ThreeDMesh():
    def __init__(self, id, baseColour, maxColour):
        self.id = id
        self.data = self.importData()
        self.z = 0
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
    def __init__(self, x, y, width, height, baseColour, maxColour):
        # Set the attributes to the values given.
        self.x = x
        self.y = y
        self.xSpeed = 0
        self.ySpeed = 0
        self.xAcceleration = 2
        self.yAcceleration = 0.2
        self.width = width
        self.height = height
        self.baseColour = baseColour
        self.maxColour = maxColour
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
    def draw(self, screen, levelZ):
        # Calculate the colour to be used while drawing.
        colour = (calculateColour(self.baseColour[0], self.maxColour[0], levelZ),
                  calculateColour(self.baseColour[1], self.maxColour[1], levelZ),
                  calculateColour(self.baseColour[2], self.maxColour[2], levelZ))
        # Use pygame's built in draw rectangle function.
        pygame.draw.rect(screen, colour, [self.x, self.y, self.width, self.height])

    # Displace the player after collision.
    def collisionDisplace(self, projectionVector):
        # Change the player's x and y coordinates according to the projection vector.
        self.x += projectionVector[0]
        self.y += projectionVector[1]

    # Reset the Player's position.
    def reset(self):
        # Set the x and y coordinates to zero.
        self.x = 0
        self.y = 0

# The class for the lava surfaces.
class Lava(ThreeDMesh):
    # A method for detecting collisions.
    def collide(self, player):
        # Take the current cross-section from the data array.
        cSection = self.data[math.floor(self.z)]
        # Iterate over the polygons in the current cross-section.
        for obstacle in cSection:
            # Check the x and y axes.
            if not sat.checkOverlap(obstacle, player.vertices, [1,0]):
                # If there is no overlap we can jump to the next
                # polygon in the data set thanks to the SAT principles.
                continue
            if not sat.checkOverlap(obstacle, player.vertices, [0,1]):
                continue
            # Iterate over the polygon's edges.
            # We assume that there is overlap unless proven otherwise.
            collided = 1
            for i in range(len(obstacle)):
                # Get the normal to this edge...
                normal = sat.getNormal(obstacle[i], obstacle[(i+1) % len(obstacle)])
                # ...and check for overlap, if the axis is not the x or y axis.
                if (normal[0]*normal[1] != 0) and not sat.checkOverlap(obstacle, player.vertices, normal):
                    # Stop checking the edges and rise the flag that
                    # there is no overlap.
                    collided = 0
                    break
            # If we got past all the overlap checks and there was overlap
            # on all the axes, it means that there is a collision, so we
            # reset the level.
            if collided:
                player.reset()
                # If there is a collision we do not need to check
                # the rest of the polygons.
                break

# The class for the level surfaces.
class Level(ThreeDMesh):
    # A method for detecting collisions.
    def collide(self, player):
        # Take the current cross-section from the data array.
        cSection = self.data[math.floor(self.z)]
        # Iterate over the polygons in the current cross-section.
        for obstacle in cSection:
            # Create lists for holding projection vector lengths
            # and the vectors.
            projectionVectorsLenghts = []
            projectionVectors = []
            # Check the x and y axes.
            vectors = sat.calculateProjectionVectors(obstacle, player.vertices, [1, 0])
            # If the calculateProjectionVectors function did not return false,
            # it means that it successfully found projection vectors...
            if vectors:
                # ...which we can add to our lists.
                projectionVectorsLenghts.append(vectors[0])
                projectionVectors.append(vectors[1])
                projectionVectorsLenghts.append(vectors[2])
                projectionVectors.append(vectors[3])
            else:
                continue

            vectors = sat.calculateProjectionVectors(obstacle, player.vertices, [0, 1])
            if vectors:
                projectionVectorsLenghts.append(vectors[0])
                projectionVectors.append(vectors[1])
                projectionVectorsLenghts.append(vectors[2])
                projectionVectors.append(vectors[3])
            else:
                continue

            # Iterate over the polygon's edges.
            # We assume that there is overlap unless proven otherwise.
            collided = 1
            for i in range(len(obstacle)):
                # Get the normal to this edge...
                normal = sat.getNormal(obstacle[i], obstacle[(i + 1) % len(obstacle)])
                # ...and check for overlap, if the axis is not the x or y axis.
                if (normal[0] * normal[1] != 0):
                    vectors = sat.calculateProjectionVectors(obstacle, player.vertices, normal)
                    if vectors:
                        projectionVectorsLenghts.append(vectors[0])
                        projectionVectors.append(vectors[1])
                        projectionVectorsLenghts.append(vectors[2])
                        projectionVectors.append(vectors[3])
                    else:
                        # Stop checking the edges and rise the flag that
                        # there is no overlap.
                        collided = 0
                        break
            # If we got past all the overlap checks and there was overlap
            # on all the axes, it means that there is a collision.
            if collided:
                # Find the index of the shortest vector...
                minimumIndex = projectionVectorsLenghts.index(min(projectionVectorsLenghts))
                # ...and pass it to the player.
                player.collisionDisplace(projectionVectors[minimumIndex])
                # If there is a collision we do not need to check
                # the rest of the polygons.
                break

# Calculate the colour component based on the z position.
def calculateColour(min, max, z):
    return math.floor(min + z/500 * (max-min))

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

    # Creating objects for testing:
    level = Level("1_level", (33,150,243), (13,71,161))
    lava = Lava("1_lava", (255,9,9), (180,0,0))
    player = Player(0, 0, 20, 20, (255,193,0), (255,111,0))

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
        # Update level and lava based on mouse position
        level.update(mouse_y)
        lava.update(mouse_y)
        # Move the player
        player.update(mouse_x, mouse_y)
        # Collide the player with the lava and the level
        lava.collide(player)
        level.collide(player)

        # Do the drawing:
        # Set the backgorund color
        backgroundBaseColour = (225,245,254)
        backgroundMaxColour = (179,229,252)
        screen.fill((
            calculateColour(backgroundBaseColour[0], backgroundMaxColour[0], level.z),
            calculateColour(backgroundBaseColour[1], backgroundMaxColour[1], level.z),
            calculateColour(backgroundBaseColour[2], backgroundMaxColour[2], level.z)))
        # Draw the lava, the level and the player
        lava.draw(screen)
        level.draw(screen)
        player.draw(screen, level.z)

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

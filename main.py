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
        self.yPV = 0
        # Create the vertices list
        self.vertices = []

    # Update the position every refresh based on keyboard input.
    def update(self, xSpeed, ySpeed):
        # Set xSpeed based on left/right keys pressed.
        self.xSpeed = xSpeed * self.xAcceleration
        # Add a constant to the ySpeed to simulate freefall.
        self.ySpeed += self.yAcceleration
        # Set a speed limit.
        if self.ySpeed > 5:
            self.ySpeed = 5
        # Jump if conditions are met.
        if ySpeed == -1 and self.yPV < -0.1:
            self.ySpeed = -5
        # Reset the stored y component of the projection vector.
        self.yPV = 0
        # Add the speeds to the coordinates.
        self.x += self.xSpeed
        self.y += self.ySpeed
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
        # Save the y component of the projection vector for use in update()
        self.yPV = projectionVector[1]
        # Reset the ySpeed after collision
        if projectionVector[1] < 0:
            self.ySpeed *= abs(projectionVector[0]) / math.sqrt(projectionVector[0] ** 2 + projectionVector[1] ** 2)

    # Reset the Player's position.
    def reset(self):
        # Set the x and y coordinates to zero.
        self.x = 0
        self.y = 0
        # Reset the ySpeed.
        self.ySpeed = 0

# The class for the lava surfaces.
class Lava(ThreeDMesh):
    # A method for detecting collisions.
    def collide(self, player, stars):
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
                stars.reset()
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

# The class that handles all things related to stars
class Stars():
    def __init__(self, id, baseColour, maxColour):
        # Set the attributes
        self.id = id
        self.z = 0
        self.score = 0
        # Import the data from a text file
        self.data = self.importData()
        self.baseColour = baseColour
        self.maxColour = maxColour
        self.currentColour = self.baseColour

    # Import the data about the stars
    def importData(self):
        # Create a temporary data list.
        data = []
        # Open the data file.
        with open('level_data/' + self.id + ".txt", 'r') as f:
            # Parse every line in the file.
            for line in f:
                # Create a temporary list for every star and append coordinates
                star = [int(x) for x in line.split(" ")]
                # Append the state of the star. 1 is uncollected.
                star.append(0)
                # Append the star list to the data list.
                data.append(star)
        # Ensure that the file is closed.
        f.closed
        # Return the data array
        return data

    # Draw a single star.
    def drawStar(self, screen, x, y, state):
        # The basic star vertices
        vertices = [[32,10],[20,10],[16,0],[12,10],[0,10],[9,19],[6,30],[16,24],[26,30],[23,19],[32,10]]
        # Add the given x and y coordinates to the star's vertices.
        correctedVertices = [[v[0] + x, v[1] + y] for v in vertices]
        # Draw the star. The state is used as width. If it is 0 (uncollected),
        # the polygon is filled, if it is 1 (collected), a border of width 3 is drawn.
        pygame.draw.polygon(screen, self.currentColour, correctedVertices, state*3)

    # Draw the stars and the star score.
    def draw(self, screen):
        # Iterate on the stars in the data array.
        for star in self.data:
            # Draw the stars.
            self.drawStar(screen, star[0], star[1], star[2])
        # Render the star score.
        for i in range(len(self.data)):
            if i > self.score-1:
                # Draw an empty star.
                self.drawStar(screen, 5+i*40, 5, 1)
            else:
                # Draw a full star.
                self.drawStar(screen, 5+i*40, 5, 0)

    # Update the stars.
    def update(self, mouse_y, player):
        # Use the self.z and colour updating algorithm from the ThreeDMesh class.
        diff = mouse_y - self.z
        if abs(diff) > 50:
            diff = 50 * abs(diff) / diff
        self.z += diff * 0.1
        self.currentColour = (
            calculateColour(self.baseColour[0], self.maxColour[0], self.z),
            calculateColour(self.baseColour[1], self.maxColour[1], self.z),
            calculateColour(self.baseColour[2], self.maxColour[2], self.z))
        # Iterate on the stars to check for collisions.
        for star in self.data:
            # Check for overlap. We get the projections by adding
            # width and height to respective coordinates.
            if not star[2] and not (player.x + player.width < star[0])\
                    and not (player.x > star[0] + 32)\
                    and not (player.y + player.height < star[1])\
                    and not (player.y > star[1] + 32):
                # If there is a collision, set the star to collected...
                star[2] = 1
                # ...and add one to the score.
                self.score += 1

    # Reset the stars' state and the star score.
    def reset(self):
        # Set the score to zero.
        self.score = 0
        # Iterate on the stars...
        for star in self.data:
            # ...setting their state to uncllected.
            star[2] = 0

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
    stars = Stars("1_stars", (255,238,88), (253,216,53))
    player = Player(0, 0, 20, 20, (255,193,0), (255,111,0))
    xSpeed = 0
    ySpeed = 0
    leftPressed = 0
    rightPressed = 0
    s = open("scores.txt", 'r')
    scores = [int(x) for x in s.read().split(" ")]
    s.close()
    # Load the necessary images.
    backgroundImage = pygame.image.load("images/main_background.png").convert()
    lockedImage = pygame.image.load("images/locked.png").convert_alpha()

    state = 0
    firstDraw = 1
    # Main program loop, runs until the close button is pressed.
    while not done:
        if state == -1:
            # Show the winning screen.
            print("win")
        elif state == 0:
            # Show the main screen.
            for event in pygame.event.get():
                # If the event type is QUIT, the user wants to close the window.
                # So we set done to True.
                if event.type == pygame.QUIT:
                    done = True
            # Check if drawing needs to be done.
            if firstDraw:
                # Draw the background.
                screen.blit(backgroundImage, [0, 0])
                # Iterate on the list of scores
                for i in range(len(scores)):
                    # If the level is locked display three empty stars
                    # and a locked badge.
                    if scores[i] < 0:
                        for j in range(3):
                            # We use the drawStar() method od the Stars class.
                            stars.drawStar(screen, 31 + i%4*113 + j*33, 285 + i//4*113, 1)
                        screen.blit(lockedImage, [28 + i%4*113, 217 + i//4*113])
                    # If the level is not locked, display the star score
                    # using a loop almost identical to that used in the draw()
                    # method of the Stars class.
                    else:
                        for j in range(3):
                            if j > scores[i] - 1:
                                stars.drawStar(screen, 31 + i%4*113 + j*33, 285 + i//4*113, 1)
                            else:
                                stars.drawStar(screen, 31 + i%4*113 + j*33, 285 + i//4*113, 0)
                # Refresh the screen
                pygame.display.flip()
                # Indicate that there is no need for further drawing.
                firstDraw = 0

        elif state < 9:
            # Show the level indicated by the state variable.
            # Event processing - we iterate on the events given to us by pygame:
            for event in pygame.event.get():
                # If the event type is QUIT, the user wants to close the window.
                # So we set done to True.
                if event.type == pygame.QUIT:
                    done = True
                # Handle the keydown events.
                elif event.type == pygame.KEYDOWN:
                    # Go left.
                    if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                        leftPressed = 1
                        xSpeed = -1
                    # Go right.
                    elif event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                        rightPressed = 1
                        xSpeed = 1
                        # Jump.
                    elif event.key == pygame.K_w or event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                        ySpeed = -1
                # Handle the keyup events.
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                        leftPressed = 0
                        xSpeed = 0
                        # If right is still pressed, start going right.
                        if rightPressed == 1:
                            xSpeed = 1
                    elif event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                        rightPressed = 0
                        xSpeed = 0
                        # If left is still pressed, start going left.
                        if leftPressed == 1:
                            xSpeed = -1
                    elif event.key == pygame.K_w or event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                        ySpeed = 0
            # Get the mouse coordinates.
            pos = pygame.mouse.get_pos()
            mouse_x = pos[0]
            mouse_y = pos[1]
            # print(mouse_x, mouse_y)

            # Game logic:
            # Update level and lava based on mouse position
            level.update(mouse_y)
            lava.update(mouse_y)
            # Move the player
            player.update(xSpeed, ySpeed)
            # Collide the player with the lava and the level
            lava.collide(player, stars)
            level.collide(player)
            stars.update(mouse_y, player)

            # Do the drawing:
            # Set the backgorund color
            backgroundBaseColour = (225,245,254)
            backgroundMaxColour = (179,229,252)
            screen.fill((
                calculateColour(backgroundBaseColour[0], backgroundMaxColour[0], level.z),
                calculateColour(backgroundBaseColour[1], backgroundMaxColour[1], level.z),
                calculateColour(backgroundBaseColour[2], backgroundMaxColour[2], level.z)))
            # Draw the lava, the level, stars and the player
            lava.draw(screen)
            level.draw(screen)
            stars.draw(screen)
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

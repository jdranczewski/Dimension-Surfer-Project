# The Separating Axis Theorem library by Jakub Dranczewski.
# Developed for the Dimension Surfer game, as part of a
# Computer Science Project.

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
    if (obstacle_p[1] < player_p[0]) or (obstacle_p[0] > player_p[1]) or obstacle_p[1]-obstacle_p[0] < 1:
        # If the above condition is true,
        # it means that the projections do not overlap.
        return False
    else:
        # Else, it means that there is overlap.
        return True

# Check for overlap and calculate projection vectors.
def calculateProjectionVectors(obstacle, player, normal):
    # Project the player and the obstacle onto the axis given by the normal vector.
    obstacle_p = project(obstacle, normal)
    player_p = project(player, normal)
    # Test for overlap.
    if (obstacle_p[1] < player_p[0]) or (obstacle_p[0] > player_p[1]) or obstacle_p[1]-obstacle_p[0] < 1:
        # If the above condition is true,
        # it means that the projections do not overlap.
        return False
    else:
        # Else, it means that there is overlap.
        # Calculate the values of the projection vectors.
        value1 = obstacle_p[0] - player_p[1]
        value2 = obstacle_p[1] - player_p[0]
        # Make them directed along the normal.
        vector1 = [normal[0] * value1, normal[1] * value1]
        vector2 = [normal[0] * value2, normal[1] * value2]
        # Return the necessary data.
        return [abs(value1), vector1, abs(value2), vector2]

# Calculate the normal vector for a given edge.
def getNormal(a, b):
    # Obtain the vector representing the edge...
    edge = [b[0] - a[0], b[1] - a[1]]
    # ...and its length.
    length = math.sqrt(edge[0]^2 + edge[1]^2)
    # Turn the edge vector into a unit vector.
    edge = [edge[0] / length, edge[1] / length]
    # Create a vector perpendicular to the unit edge vector...
    normal = [-edge[1], edge[0]]
    # ...and return it.
    return normal

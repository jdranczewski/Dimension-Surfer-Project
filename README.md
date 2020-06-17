# Dimension Surfer
A game created in [`pygame`](https://www.pygame.org/) (a Python library), as an
A-level Computer Science project.

**Finalist in the [BAFTA Young Game Designers](http://ygd.bafta.org/competition/competition-news/2017/dimension-surfer)
contest.**

The game explores a mechanism in which the player can only play a 2D slice of
a 3D level at any give point, but the slice can be freely chosen. This allows
for getting around obstacles that are impossible to cross in just 2D.

The game implements a custom collision engine based on the Separating Axis
Theorem (which is needed to support the dynamically changing environment).

The movement in the third dimension is achieved by moving one's mouse up and
down within the game's window.

You can read a write-up that describes the game in detail [here](http://dranczewski.j.pl/DimensionSurfer.pdf)
(pdf, 8.2MB).

**The `master` branch preserves the state of the code when the project was
submitted for marking. The `BAFTA` branch is what I submitted to the BAFTA
YGD competition** This includes better levels, some fixes, new backgrounds,
and a face for the character. **I recommend using the `BAFTA` branch for testing the game.

![Screenshot from the game](https://i.imgur.com/OymJnY4.png "Screenshot from the game")

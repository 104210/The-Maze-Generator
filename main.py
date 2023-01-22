from random import randint, uniform, choices

import pygame

# Sorry if the code is bad.

# The game is somewhat simple and is explained below.

# 1. The goal.
# The goal is to simply get to the end of the maze, which is a green square.
# The game is endless and there will always be another maze.
#
# 2. Things in the maze.
#     2.1. Powerups.
#         2.1.1. The yellow powerup.
#             It makes you temporarily faster.
#         2.1.2. The cyan powerup.
#             It makes you temporarily slower. It's more like an obstacle.
#
#             Also, they're inspired by the poison mushrooms from
#             Super Mario Bros.: The Lost Levels.
#
#     2.2. Enemies.
#         Enemies will pick a random direction upon spawning and move in it.
#
#         When an enemy is touched by the player, they will die. However, if
#         the player didn't have a powerup when they touched the enemy, then
#         they will die as well. If the player did have a powerup, then they
#         simply lose it.
#
#         Also, enemies can collect powerups as well and they can even spawn
#         with a powerup equipped.
#
#         There are 2 types of enemies.
#
#         2.2.1. Type 1.
#             These enemies are (usually) dark blue and, when they touch a
#             wall, they will move in the opposite direction.
#         2.2.2. Type 2.
#             These enemies are (usually) purple / violet and, when they
#             touch a wall, they will then move in a random direction.

# The code is divided into 4 main sections.
# Section 1: Defining constants.
# Section 2: Defining classes.
# Section 3: Defining functions.
# Section 4: The gameplay loop (and other stuff).

pygame.init()

###############################################################################
# Section 1: Defining constants.
###############################################################################

# Might be useful to do this, but Idk.
SPRITE = pygame.sprite.Sprite
SPRITECOLLIDEANY = pygame.sprite.spritecollideany

# Sets up constants for the window and other stuff.
SCREEN_WIDTH, SCREEN_HEIGHT = 900, 900
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))  # Creates the window for the game.
pygame.display.set_caption("The Maze Generator")

CLOCK = pygame.time.Clock()

# Sets up constants for the maze.
COLUMNS, ROWS = 12, 12

HORIZONTAL_CELL_WIDTH = SCREEN_WIDTH / COLUMNS
VERTICAL_CELL_WIDTH = SCREEN_HEIGHT / ROWS

AVERAGE_CELL_WIDTH = (HORIZONTAL_CELL_WIDTH * VERTICAL_CELL_WIDTH) ** 0.5

HORIZONTAL_OFFSET = HORIZONTAL_CELL_WIDTH / 2  # Used to properly position things horizontally in a cell.
VERTICAL_OFFSET = VERTICAL_CELL_WIDTH / 2  # Used to properly position things vertically in a cell.

# Sets up constants for the player.
# 1 is added, so that if the rest is 0, then the player will still get some speed.
PLAYER_SPEED_SLOW = 40//((COLUMNS * ROWS) ** 0.5) + 1
PLAYER_SPEED_NORMAL = 50//((COLUMNS * ROWS) ** 0.5) + 1
PLAYER_SPEED_FAST = 68.75//((COLUMNS * ROWS) ** 0.5) + 1

# Sets up constants for the enemies.
ENEMY_SPEED_SLOW = 21.7391//((COLUMNS * ROWS) ** 0.5) + 1
ENEMY_SPEED_NORMAL = 31.25//((COLUMNS * ROWS) ** 0.5) + 1
ENEMY_SPEED_FAST = 45.8984//((COLUMNS * ROWS) ** 0.5) + 1

# The below list will hold the actual music that pygame will use.
MUSIC = []
# You can add your own music by putting a song in the working directory
# and then putting a string of the song name in the list below.
# The string must also include the file extension.
track_names = []
# Btw, all of the default music below comes from a game called VVVVVV.
# I decided to not include the default music.
# Comment out the below lines if you don't want any music.

# track_names.extend([
#     "Predestined Fate Remixed.mp3",
#     "Paced Energy.mp3",
#     "Passion for Exploring.mp3",
#     "Pressure Cooker.mp3",
#     "Pushing Onwards.mp3"
# ])

for name in track_names:
    # Attempt to find and load in music with the names above.
    try:
        MUSIC.append(pygame.mixer.Sound(f"{name}"))
    # If a track can't be found, then the program will skip it.
    # This is done so that the program doesn't need the music in order to run.
    except FileNotFoundError:
        print(f"Couldn't find the track: {name}")

# Deleted, because it's not needed after the above.
del track_names

###############################################################################
# Section 2: Defining classes.
###############################################################################


class Player(SPRITE):
    """Used, of course, to make the player."""

    def __init__(self):
        super().__init__()

        self.image = pygame.Surface((HORIZONTAL_OFFSET, VERTICAL_OFFSET))
        self.image.fill("#ff4040")  # Red.
        self.rect = self.image.get_rect(centerx=HORIZONTAL_OFFSET, centery=VERTICAL_OFFSET)
    
        self.speed = PLAYER_SPEED_NORMAL
        
        # Represents how much further (the number of maze cells)
        # the player can move before their powerup runs out.
        # 0 means that the powerup has run out.
        self.powerup_distance = 0
        # Represents what powerup the player currently has.
        # 0 means that the player doesn't have a powerup (yet).
        self.powerup_type = 0
    
    def player_input(self) -> None:
        """Handle player input as well as maze wall collision detection."""

        keys_pressed = pygame.key.get_pressed()

        if any(keys_pressed):
            # If the player is pressing w,
            if keys_pressed[pygame.K_w]:
                # then move them up.
                self.rect.y -= self.speed

                # However, if they're now in a wall,
                if SPRITECOLLIDEANY(self, maze_walls):
                    # then move them back to where they were.
                    self.rect.y += self.speed
            # If they're not moving up,
            # then check for s being pressed.
            # If s has been pressed,
            elif keys_pressed[pygame.K_s]:
                # then move them down.
                self.rect.y += self.speed

                if SPRITECOLLIDEANY(self, maze_walls):
                    self.rect.y -= self.speed
            
            if keys_pressed[pygame.K_a]:
                self.rect.x -= self.speed

                if SPRITECOLLIDEANY(self, maze_walls):
                    self.rect.x += self.speed
            elif keys_pressed[pygame.K_d]:
                self.rect.x += self.speed

                if SPRITECOLLIDEANY(self, maze_walls):
                    self.rect.x -= self.speed

            if self.powerup_distance > 0:
                self.powerup_distance -= self.speed / AVERAGE_CELL_WIDTH

                # Once the power distance is 0,
                if self.powerup_distance <= 0:
                    # then reset the player to their normal state.
                    self.speed = PLAYER_SPEED_NORMAL
                    self.image.fill("#ff4040")  # Red.

                    self.powerup_type = 0
    
    def enemy_collision(self) -> None:
        """Checks to see if the player is touching a enemy."""

        # Check to see if we have actually collided with a enemy first.
        collided_sprite = SPRITECOLLIDEANY(self, enemies)

        # If collided_sprite isn't None, then do stuff to the sprite.
        if collided_sprite:
            # Once a enemy has been touched, it should die.
            enemies.remove(collided_sprite)

            # If player speed hasn't gotten a powerup,
            if self.powerup_type == 0:
                # then send the player back to the start.
                self.rect.centerx, self.rect.centery = HORIZONTAL_OFFSET, VERTICAL_OFFSET
            else:
                # If the player got a powerup, then make their
                # speed and appearance normal again and let them go on.
                self.speed = PLAYER_SPEED_NORMAL
                self.image.fill("#ff4040")  # Red.

                self.powerup_type = 0

    def powerup_collision(self) -> None:
        """Checks to see if the player is touching a power-up."""

        # Check to see if we have actually collided with a power-up first.
        collided_sprite = SPRITECOLLIDEANY(self, powerups)

        # If collided_sprite isn't None, then do stuff to the sprite.
        if collided_sprite:

            # Check and see what kind of power-up it is.
            match collided_sprite.type:
                # Power-up.
                case 1:
                    self.image.fill("#ffa040")  # Orange.
                    self.speed = PLAYER_SPEED_FAST

                    self.powerup_type = 1
                # Power-down.
                case 2:
                    self.image.fill("#a0a0a0")  # Gray / grey.
                    self.speed = PLAYER_SPEED_SLOW

                    self.powerup_type = 2
                # The end of the maze.
                # Will be used to go on to the next maze.
                case 3:
                    return "End"
            
            # Once a power-up has been "collected", the enemy shouldn't be able to get
            # it again.
            powerups.remove(collided_sprite)
            
            self.powerup_distance = (((COLUMNS*ROWS) ** 0.5) - 1) * 0.8173828125
        

class PowerUp(SPRITE):
    """Used to create stuff that the player can collect."""

    def __init__(self, type: int, **kwargs):
        super().__init__()

        self.image = pygame.Surface((HORIZONTAL_OFFSET, VERTICAL_OFFSET))
        self.rect = self.image.get_rect(**kwargs)

        match type:
            # Power-up.
            case 1:
                self.image.fill("#ffff40")  # Yellow.
            # Power-down.
            case 2:
                self.image.fill("#40ffff")  # Light blue / cyan.
            # The end of the maze.
            case 3:
                self.image.fill("#40ff40")  # Green.

        self.type = type
    
    @staticmethod
    def powerup_generation() -> pygame.sprite.Group:
        """Generate sprites for the power-ups of a maze."""

        powerup_group = pygame.sprite.Group()

        for row in range(1, ROWS + 1):
            for column in range(1, COLUMNS + 1):
                if randint(1, powerup_chance) == 1:
                    # Calculates where the powerup should be placed.
                    WIDTH_times_row = -VERTICAL_OFFSET + VERTICAL_CELL_WIDTH*row
                    WIDTH_times_column = -HORIZONTAL_OFFSET + HORIZONTAL_CELL_WIDTH*column

                    # Bad powerups are slightly more common.
                    # This makes the good powerups feel more special / valuable.
                    selected_powerup_type = choices([1, 2], [42.8571, 57.1428], k=1)[0]

                    powerup = PowerUp(
                        type=selected_powerup_type,
                        centerx=WIDTH_times_column,
                        centery=WIDTH_times_row
                    )
                
                    powerup_group.add(powerup)
        
        # These 2 lines are here so that even if no powerups generate,
        # the end still can generate properly.
        WIDTH_times_row = -VERTICAL_OFFSET + VERTICAL_CELL_WIDTH*row
        WIDTH_times_column = -HORIZONTAL_OFFSET + HORIZONTAL_CELL_WIDTH*column
        
        # Add an end point for the maze, so the player can go on to the next maze / level.
        powerup_group.add(PowerUp(3, centerx=WIDTH_times_column, centery=WIDTH_times_row))

        return powerup_group


class Enemy(SPRITE):
    """Used to create enemies for the maze."""

    def __init__(self, enemy_type: int, enemy_powerup_type: int, direction: int, **kwargs):
        super().__init__()

        self.image = pygame.Surface((HORIZONTAL_OFFSET, VERTICAL_OFFSET))

        self.enemy_type = enemy_type
        self.enemy_powerup_type = enemy_powerup_type

        # Type 1 refers to normal enemies that bounce back and forth in certain directions.
        if enemy_type == 1:
            match enemy_powerup_type:
                # Powered-up / fast type 1 enemy.
                case 1:
                    self.image.fill("#CFCF70")  # Yellow and gray / grey.
                    self.speed = ENEMY_SPEED_FAST
                # Powered-down / slow type 1 enemy.
                case 2:
                    self.image.fill("#40CFFF")  # Slightly darker cyan.
                    self.speed = ENEMY_SPEED_SLOW
                # Normal type 1 enemy.
                case 3:
                    self.image.fill("#4040ff")  # Blue / dark blue.
                    self.speed = ENEMY_SPEED_NORMAL
        # Type 2 is for enemies that keep moving in random directions.
        elif enemy_type == 2:
            match enemy_powerup_type:
                # Powered-up / fast type 2 enemy.
                case 1:
                    self.image.fill("#C0A060")  # Light brown.
                    self.speed = ENEMY_SPEED_FAST
                # Powered-down / slow type 2 enemy.
                case 2:
                    self.image.fill("#60A0C0")  # Something between light and dark blue.
                    self.speed = ENEMY_SPEED_SLOW
                # Normal type 2 enemy.
                case 3:
                    self.image.fill("#804080")  # Purple / violet.
                    self.speed = ENEMY_SPEED_NORMAL
        
        self.rect = self.image.get_rect(**kwargs)

        self.direction = direction
    
    @staticmethod
    def enemy_generation() -> pygame.sprite.Group:
        """Generate sprites for the enemies of a maze."""

        enemy_group = pygame.sprite.Group()

        for row in range(1, ROWS + 1):
            for column in range(1, COLUMNS + 1):
                if randint(1, enemy_chance) == 1:
                    # Calculates where the enemy should be placed.
                    WIDTH_times_row = -VERTICAL_OFFSET + VERTICAL_CELL_WIDTH*row
                    WIDTH_times_column = -HORIZONTAL_OFFSET + HORIZONTAL_CELL_WIDTH*column

                    # Explanation: The chances of an enemy being type 1 is 71.875% and so on.
                    selected_enemy_type = choices([1, 2], [75, 25], k=1)[0]
                    # Explanation: The chances of an enemy having a powerup of type 1 is 23.4375% and so on.
                    selected_enemy_powerup_type = choices([1, 2, 3], [23.4375, 14.0625, 62.5], k=1)[0]

                    enemy = Enemy(
                        enemy_type=selected_enemy_type,
                        enemy_powerup_type=selected_enemy_powerup_type,
                        direction=randint(1, 4),
                        centerx=WIDTH_times_column,
                        centery=WIDTH_times_row
                    )

                    enemy_group.add(enemy)

        return enemy_group
    
    def powerup_collision(self) -> None:
        """Checks to see if an enemy is touching a power-up."""

        # Pretty much the same as the powerup_collision function in the Player class.

        # Check to see if we have actually collided with a power-up first.
        collided_sprite = SPRITECOLLIDEANY(self, powerups)

        # If collided_sprite isn't None, then do stuff to the sprite.
        if collided_sprite:
            if self.enemy_type == 1:
                # Check and see what kind of power-up it is.
                match collided_sprite.type:
                    # Power-up.
                    case 1:
                        self.image.fill("#CFCF70")  # Yellow and gray / grey.
                        self.speed = ENEMY_SPEED_FAST
                    # Power-down.
                    case 2:
                        self.image.fill("#40CFFF")  # Slightly darker cyan.
                        self.speed = ENEMY_SPEED_SLOW
                    # An enemy shouldn't be able to collect the end of the maze powerup,
                    # so we end the function before it gets collected (removed).
                    case 3:
                        return None
            elif self.enemy_type == 2:
                # Check and see what kind of power-up it is.
                match collided_sprite.type:
                        # Powered-up / fast type 2 enemy.
                    case 1:
                        self.image.fill("#C0A060")  # Light brown.
                        self.speed = ENEMY_SPEED_FAST
                    # Powered-down / slow type 2 enemy.
                    case 2:
                        self.image.fill("#60A0C0")  # Something between light and dark blue.
                        self.speed = ENEMY_SPEED_SLOW
                    # An enemy shouldn't be able to collect the end of the maze powerup,
                    # so we end the function before it gets collected (removed).
                    case 3:
                        return None
            
            # Once a power-up has been "collected", the enemy shouldn't be able to get
            # it again.
            powerups.remove(collided_sprite)
                    
    
    def update(self):
        """Mainly used to move each enemy and have it act.
        Also checks for maze wall collision detection.
        Also checks for powerup collision detection.
        """

        if self.enemy_type == 1:
            # Movement.
            match self.direction:
                # If it's facing right,
                case 1:
                    # then move it to the right.
                    self.rect.x += self.speed

                    # Collision detection.
                    # If it's touching a wall,
                    if SPRITECOLLIDEANY(self, maze_walls):
                        # then go in the other / opposite direction.
                        self.direction = 3
                        self.rect.x -= self.speed
                case 2:
                    # Moving down.
                    self.rect.y += self.speed

                    if SPRITECOLLIDEANY(self, maze_walls):
                        self.direction = 4
                        self.rect.y -= self.speed
                case 3:
                    # Moving to the left.
                    self.rect.x -= self.speed

                    if SPRITECOLLIDEANY(self, maze_walls):
                        self.direction = 1
                        self.rect.x += self.speed
                case 4:
                    # Moving up.
                    self.rect.y -= self.speed

                    if SPRITECOLLIDEANY(self, maze_walls):
                        self.direction = 2
                        self.rect.y += self.speed
        elif self.enemy_type == 2:
            # Movement.
            match self.direction:
                # If it's facing right,
                case 1:
                    # then move it to the right.
                    self.rect.x += self.speed

                    # Collision detection.
                    # If it's touching a wall,
                    if SPRITECOLLIDEANY(self, maze_walls):
                        # then go in a random direction.
                        self.direction = randint(1, 4)
                        self.rect.x -= self.speed
                case 2:
                    # Moving down.
                    self.rect.y += self.speed

                    if SPRITECOLLIDEANY(self, maze_walls):
                        self.direction = randint(1, 4)
                        self.rect.y -= self.speed
                case 3:
                    # Moving to the left.
                    self.rect.x -= self.speed

                    if SPRITECOLLIDEANY(self, maze_walls):
                        self.direction = randint(1, 4)
                        self.rect.x += self.speed
                case 4:
                    # Moving up.
                    self.rect.y -= self.speed

                    if SPRITECOLLIDEANY(self, maze_walls):
                        self.direction = randint(1, 4)
                        self.rect.y += self.speed
        
        # Explains itself, but this checks for collisions with powerups.
        self.powerup_collision()


class MazeWall(SPRITE):
    """Used to create the individual walls of a maze."""

    def __init__(self, width: int, height: int, **kwargs):
        super().__init__()

        self.image = pygame.Surface((width, height))
        self.image.fill("white")
        self.rect = self.image.get_rect(**kwargs)
    
    @staticmethod
    def maze_generation() -> pygame.sprite.Group:
        """Generate sprites for the walls of a maze."""

        # I know that the maze generation is a bit questionable
        # and odd, but it works fine, Imo.

        maze_wall_group = pygame.sprite.Group()

        # Determines the range of directions that maze walls can face.
        direction_start = 1
        direction_end = 4

        # This changes the maze wall RNG sometimes, so that a greater variety
        # of mazes can generate.
        if randint(1, 4) == 1:
            direction_start = randint(1, 2)

            if direction_start == 1:
                direction_end = randint(3, 4)
            else:
                direction_end = 4

        for row in range(1, ROWS):
            # Calculates where the player should be placed vertically (what row).
            WIDTH_times_row = VERTICAL_CELL_WIDTH * row
            for column in range(1, COLUMNS):
                # Calculates where the player should be placed horizontally (what column).
                WIDTH_times_column = HORIZONTAL_CELL_WIDTH * column

                direction = randint(direction_start, direction_end)

                # Attempts to make maze walls somewhat more connected.
                if randint(1, 8) == 1:
                    match direction:
                        case 2:
                            direction = randint(1, 3)
                        case 1 | 3 | 4:
                            direction = 4

                match direction:
                    case 1:
                        # Create a wall facing up.
                        maze_wall = MazeWall(
                            width=1,
                            height=VERTICAL_CELL_WIDTH,
                            x=WIDTH_times_column,
                            bottom=WIDTH_times_row
                        )
                    case 2:
                        # Create a wall facing right.
                        maze_wall = MazeWall(
                            width=HORIZONTAL_CELL_WIDTH,
                            height=1,
                            x=WIDTH_times_column,
                            y=WIDTH_times_row
                        )
                    case 3:
                        # Create a wall facing down.
                        maze_wall = MazeWall(
                            width=1,
                            height=VERTICAL_CELL_WIDTH,
                            x=WIDTH_times_column,
                            y=WIDTH_times_row
                        )
                    case 4:
                        # Create a wall facing left.
                        maze_wall = MazeWall(
                            width=HORIZONTAL_CELL_WIDTH,
                            height=1,
                            y=WIDTH_times_row,
                            right=WIDTH_times_column
                        )

                maze_wall_group.add(maze_wall)

        # Add a boundary to the maze, so that the player can't escape it.
        maze_wall_group.add(
            MazeWall(SCREEN_WIDTH, 1, x=0, y=0),  # Top wall.
            MazeWall(1, SCREEN_HEIGHT, x=SCREEN_WIDTH - 1, y=0),  # Right wall. Shifted 1 (pixel) to the left, so you can see it.
            MazeWall(SCREEN_WIDTH, 1, x=0, y=SCREEN_HEIGHT - 1),  # Bottom wall. Shifted 1 to up, so you can see it.
            MazeWall(1, SCREEN_HEIGHT, x=0, y=0)  # Left wall.
        )

        return maze_wall_group

###############################################################################
# Section 3: Defining functions.
###############################################################################


def draw_stuff() -> None:
    """Used to draw things (creates a frame)."""

    SCREEN.fill("#000000")  # Black.
    player.draw(SCREEN)
    maze_walls.draw(SCREEN)
    powerups.draw(SCREEN)
    enemies.draw(SCREEN)


###############################################################################
# Section 4: The gameplay loop (and other stuff).
###############################################################################

# The game loop.
while True:
    # Sets up the chances of stuff appearing in the maze.
    powerup_chance = abs(round((COLUMNS*ROWS - 15)/(COLUMNS*ROWS / 75) * uniform(uniform(0, 1.1289), 1.1289)))
    enemy_chance = abs(round((COLUMNS*ROWS - 15)/(COLUMNS*ROWS / 140.625) * uniform(uniform(0, 1.1289), 1.1289)))

    # Every now and then, there will either be a really good maze (lots of powerups)
    # or a really challenging maze (lots of enemies).
    if randint(1, 50) == 1:
        if randint(1, 3) == 1:
            powerup_chance = randint(3, 4)
        else:
            enemy_chance = randint(4, 5)

            # Stop any music currently playing
            pygame.mixer.stop()
            # and play the epic music.
            MUSIC[0].play()

    # All of these are groups.
    player = pygame.sprite.GroupSingle(Player())
    maze_walls = MazeWall.maze_generation()
    powerups = PowerUp.powerup_generation()
    enemies = Enemy.enemy_generation()

    # Repeats for as long as you are in a maze.
    while True:
        # The event loop. Only used to end the game.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
        
        draw_stuff()

        player.sprite.player_input()

        # If it returns "End" rather than None,
        if player.sprite.powerup_collision() == "End":
            # then go on to the next maze.
            break

        # Move / update all of the enemies.
        # This function runs on every enemy in the maze.
        enemies.update()

        player.sprite.enemy_collision()

        # Chooses the music.
        # If there is no music, then skip this all together.
        # Also, if no music is playing, then randomly choose some music and play it.
        # Also, if music is playing, then the following will be ignored.
        if MUSIC and pygame.mixer.get_busy() == False:
            selected_music = MUSIC[randint(1, len(MUSIC) - 1)]
            # The music will fade in for 7.5 seconds.
            selected_music.play(fade_ms=7500)
            # The end of the music will start to fade out with 5 seconds remaining.
            # Currently disabled, because it doesn't work for some dumb reason.
            # selected_music.fadeout(int(selected_music.get_length() * 1000 - 5000))

        # Extra stuff.
        pygame.display.update()
        CLOCK.tick(60)
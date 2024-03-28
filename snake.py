import pygame
import random
import math


class Snake:
    # Size of the each block in pixels
    block_size = 20

    # Size of the info bar
    info_bar = 50

    bg_color = pygame.Color("black")
    snake_head_color = pygame.Color("blue")
    snake_color = pygame.Color("white")
    food_color = pygame.Color("green")

    # The different (x, y) velocities for each direction
    LEFT = (-1, 0)
    RIGHT = (1, 0)
    UP = (0, -1)
    DOWN = (0, 1)

    DIRECTIONS = [
        "LEFT",
        "RIGHT",
        "UP",
        "DOWN",
    ]

    # The different key presses and the velocity changes
    KEY_PRESSES = {
        pygame.K_LEFT: LEFT,
        pygame.K_RIGHT: RIGHT,
        pygame.K_UP: UP,
        pygame.K_DOWN: DOWN,
        pygame.K_a: LEFT,
        pygame.K_d: RIGHT,
        pygame.K_w: UP,
        pygame.K_s: DOWN,
        # vim bindings
        pygame.K_h: LEFT,
        pygame.K_j: DOWN,
        pygame.K_k: UP,
        pygame.K_l: RIGHT,
    }

    AI_MODES = {
        pygame.K_r: "random",
        pygame.K_p: "path",
        pygame.K_t: "survival",
    }

    def __init__(self, grid_size=30):
        pygame.init()
        self.clock = pygame.time.Clock()

        self.grid_size = grid_size

        # Set the initial state for a game
        self.reset()

    def reset(self):
        self.screen = None

        # Work out the size of the screen based on the block and grid size
        self.screen_width = self.block_size * self.grid_size
        self.screen_height = self.block_size * self.grid_size + self.info_bar

        # Create a random head of the snake somewhere
        self.body = [
            (random.randint(1, self.grid_size), random.randint(1, self.grid_size))
        ]
        self.food = self._generate_food_position()
        self.velocity = random.choice(list(self.KEY_PRESSES.values()))

        # The different states of the app
        self.is_running = True
        self.is_alive = True
        self.is_paused = False
        self.ai = False
        self.ai_mode = "survival"
        self.frame = 0

        # The game speed based on the clock speed
        self.game_speed = 15

        # Show the window
        self._show_window()

    def play(self):
        while self.is_running:
            # Handle key presses and quiting the game
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    self._key_press(event.key)
                elif event.type == pygame.QUIT:
                    self.is_running = False

            # Only update if we are in game mode
            if self.is_alive and not self.is_paused:
                # If in AI mode, work out any moves needed
                if self.ai:
                    self.change_velocity(self.calculate_ai_move())

                self.play_frame(self.velocity)


    def play_frame(self, velocity):
        self.velocity = velocity

        # Set the new frame this move is for
        self.frame += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False

        # Get the new head of the snake
        future_head = self.future_head(velocity)

        # Insert the new position of the head of the snake
        self.body.insert(0, future_head)

        # Check to see if we have just eaten the food - if we have we dont remove the last block of the snake so it grows
        if future_head == self.food:
            # Set a new position for the food
            self.food = self._generate_food_position()
        else:
            # Remove the last block of the body to appear as if the whole snake moved
            removed_block = self.body.pop()

            # Draw over the position of the removed block to make it match the background colour
            # this means we dont have to already draw the whole screen again
            self._draw_block(removed_block, self.bg_color)

        # Check for collisions - the first block has already been added - so dont check that part of the body
        if self.is_collision(future_head):
            self.is_alive = False

        # Set the clock speed for how fast he game runs
        self.clock.tick(self.game_speed)

        # Display the updates to the UI
        self.display_frame()

    def is_collision(self, point):
        return point in self.body[1:]

    def pause(self):
        self.is_paused = not self.is_paused
        self.display_frame()

    @property
    def head(self):
        return self.body[0]

    def score(self):
        return len(self.body)-1

    def _key_press(self, keypress):
        if keypress in self.KEY_PRESSES:
            # If keypress is valid (up/down/left/right) - change the velocity
            self.change_velocity(self.KEY_PRESSES[keypress])
        elif keypress == pygame.K_PERIOD:
            # increase the speed
            self.game_speed += 5
        elif keypress == pygame.K_COMMA:
            # decrease the speed
            self.game_speed -= 5
            if self.game_speed < 5:
                self.game_speed = 5
        elif keypress == pygame.K_0:
            # set speed to 1
            self.game_speed = 15
        elif keypress == pygame.K_9:
            # set speed to 9
            self.game_speed = 1000
        elif keypress in self.AI_MODES:
            # Set different AI modes
            self.ai_mode = self.AI_MODES[keypress]
        elif keypress == pygame.K_SPACE:
            if self.is_alive:
                # Pause/resume the game
                self.pause()
            else:
                # Reset the game if you are dead
                self.reset()
        elif keypress == pygame.K_c:
            # toggle ai cheat mode
            self.ai = not self.ai

    def _can_change_velocity(self, new_velocity):
        # You can change any direction if you are only 1 block in size
        if self.score() == 0:
            return True

        # If current velocity plus new velocity is zero then you are trying to go back on yourself
        if self.add_points(self.velocity, new_velocity) == (0, 0):
            return False

        return True

    def change_velocity(self, velocity):
        # Check to make sure the velocity change is valid
        if self._can_change_velocity(velocity):
            self.velocity = velocity

    def future_head(self, velocity):
        # Get the next position of the head of the snake given the velocity
        # If you move off the edge of the screen you will wrap back around to the other side
        calculated_head = self.add_points(self.head, velocity)
        new_head = [None, None]
        for i, value in enumerate(calculated_head):
            if value > self.grid_size:
                new_head[i] = 1
            elif value < 1:
                new_head[i] = self.grid_size
            else:
                new_head[i] = value

        return tuple(new_head)

    def _generate_food_position(self):
        # Set the food to be within the snake so we run the loop at least once
        food = self.body[0]
        while food in self.body:
            # Generate random position for the food on the grid
            food = (
                random.randint(1, self.grid_size),
                random.randint(1, self.grid_size),
            )

        return food

    def _show_window(self):
        # Set window title bar
        pygame.display.set_caption("Snake")

        # Set the size of the window
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))

        # Show the starting screen to set a known state
        self._start_screen()

        # Display the current frame in the window
        self.display_frame()

    def _start_screen(self):
        # Fill screen with black
        self.screen.fill(self.bg_color)

    def _end_screen(self):
        # Set background to red
        self.screen.fill(pygame.Color("red"))

        # Overlay the snake and food
        self._display_screen_components()

        # Show the users score over the top
        font = pygame.font.Font("freesansbold.ttf", 120)
        text = font.render(str(self.score()), True, self.bg_color)
        textRect = text.get_rect()
        textRect.center = (self.screen_width // 2, self.screen_height // 2)
        self.screen.blit(text, textRect)

    def _get_block_position(self, block):
        # This is for the top left of the block on our grid
        # If block size is 30px:
        # (1,1) is (0, 0)
        # (5, 2) is (120, 30)
        x = (block[0] - 1) * self.block_size
        y = (block[1] - 1) * self.block_size

        return (x, y)

    def _draw_block(self, block, color):
        # Get the top left position of the block to draw
        position = self._get_block_position(block)

        # Draw the square block
        pygame.draw.rect(
            self.screen,
            color,
            pygame.Rect(position, (self.block_size, self.block_size)),
        )

    def _draw_snake(self):
        # Loop through each block in the snake body and draw it
        color = self.snake_head_color
        for block in self.body:
            self._draw_block(block, color)
            color = self.snake_color

    def _draw_food(self):
        # Draw the food as a single block
        self._draw_block(self.food, self.food_color)

    def _draw_info_bar(self):
        pygame.draw.rect(
            self.screen,
            pygame.Color("grey"),
            pygame.Rect((0, self.screen_height-self.info_bar), (self.screen_width, self.info_bar)),
        )

        font = pygame.font.Font("freesansbold.ttf", 20)
        text = font.render("Score: " + str(self.score()), True, pygame.Color("white"))
        textRect = text.get_rect()
        textRect.center = (70, self.screen_height - (self.info_bar / 2))
        self.screen.blit(text, textRect)

        text = font.render("Speed: " + str(self.game_speed), True, pygame.Color("white"))
        textRect = text.get_rect()
        textRect.center = (self.screen_width - 70, self.screen_height - (self.info_bar / 2))
        self.screen.blit(text, textRect)

        if self.is_paused:
            text = font.render("Paused", True, pygame.Color("white"))
            textRect = text.get_rect()
            textRect.center = (self.screen_width/2, self.screen_height - (self.info_bar / 2))
            self.screen.blit(text, textRect)

    def _display_screen_components(self):
        # Draw the whole snake
        self._draw_snake()

        # Draw the food
        self._draw_food()

        # Draw the info bar
        self._draw_info_bar()

    def display_frame(self):
        self._display_screen_components()

        # If game has ended show end screen
        if not self.is_alive:
            self._end_screen()

        # Flip the display to show the new content we just drew
        pygame.display.flip()

    def calculate_ai_move(self):
        # Make the move based on whatever AI model is selected
        if self.ai_mode == "random":
            velocity = self.calculate_ai_random_move()
        elif self.ai_mode == "path":
            velocity = self.calculate_ai_path_move()
        elif self.ai_mode == "survival":
            velocity = self.calculate_ai_survival_move()

        return velocity

    def calculate_ai_random_move(self):
        # Total random move each time
        return getattr(self, random.choice(self.DIRECTIONS))

    def calculate_ai_path_move(self):
        # Follow a pre-defined path for the snake to follow
        velocity = self.DOWN if self.head[0] % 2 else self.UP
        if self.head[1] == 1 and velocity == self.UP:
            velocity = self.RIGHT
        elif self.head[1] == self.grid_size and velocity == self.DOWN:
            velocity = self.RIGHT

        return velocity

    def calculate_ai_survival_move(self):
        current_velocity = self.velocity
        best_velocity = current_velocity
        best_score = None

        for direction in self.DIRECTIONS:
            check_velocity = getattr(self, direction)
            if self._can_change_velocity(check_velocity):
                future_head = self.future_head(check_velocity)
                if future_head not in self.body:
                    score = self.calculate_move_score(future_head, self.food)
                    if best_score==None or score > best_score:
                        print(direction, score)
                        best_velocity = check_velocity
                        best_score = score

        print("-")

        return best_velocity

    def distance_between(self, point1, point2):
        # These maps allow us to expand the grid to see if its
        # closer to go off the edge to reach the point
        grid_maps = [
            (-self.grid_size, 0),
            (0, -self.grid_size), (0, self.grid_size),
            (self.grid_size, 0),
        ]

        # The distance if you don't go off the edges
        distance = math.dist(point1, point2)

        # Work out if its close to go off the edge of the screen and wrap around
        for grid_map in grid_maps:
            grid_distance = math.dist(point1, self.add_points(point2, grid_map))
            if grid_distance < distance:
                distance = grid_distance

        return distance

    def calculate_move_score(self, head, food):
        grid = self.reachable_points(head)
        accessible = 0
        inaccessible = 0
        can_get_food = False

        if grid[food[0]-1][food[1]-1] == 2:
            can_get_food = True

        for x in range(self.grid_size):
            for y in range(self.grid_size):
                if grid[x][y] == 0:
                    inaccessible += 1
                elif grid[x][y] == 2:
                    accessible += 1

        grid_size = self.grid_size * self.grid_size
        snake_size = self.score()
        open_grid_size = grid_size - snake_size
        accessible_percentage = 0
        inaccessible_percentage = 0
        if accessible:
            accessible_percentage = (accessible/open_grid_size)*100
        if inaccessible:
            inaccessible_percentage = (inaccessible/open_grid_size)*100

        distance_score = self.distance_between(head, food)

        # Work out a score for this move
        score = accessible_percentage + (self.grid_size-distance_score) + (5 if can_get_food else 0)

        print(score,can_get_food, grid_size, snake_size, open_grid_size, f"{accessible} ({accessible_percentage}%)", f"{inaccessible} ({inaccessible_percentage}%)")

        return score


    def reachable_points(self, head):
        grid = [[0 for x in range(self.grid_size)] for i in range(self.grid_size)]

        # mark in points blocked by the snakes body
        for point in self.body:
            grid[point[0]-1][point[1]-1] = 1

        # work out any points that can be accessed
        grid = self.check_reachable_point(grid, head)

        return grid

    def add_points(self, point1, point2):
        return (
            point1[0] + point2[0],
            point1[1] + point2[1],
        )

    def check_reachable_point(self, grid, head):
        # the points to check
        points = [
            (-1, 0),
            (0, -1), (0, 1),
            (1, 0),
        ]

        to_check = []

        for point in points:
            new_head = self.add_points(head, point)

            # TODO: doesnt account for wrapping screen
            if new_head[0] < 0 or new_head[1] < 0 or new_head[0] > self.grid_size or new_head[1] > self.grid_size:
                break

            if grid[new_head[0]-1][new_head[1]-1] == 0:
                grid[new_head[0]-1][new_head[1]-1] = 2
                to_check.append(new_head)

        for check in to_check:
            grid = self.check_reachable_point(grid, check)

        return grid


if __name__ == '__main__':
    # Init the Snake object and run the game
    snake = Snake()
    snake.play()

import torch
import numpy as np
from collections import deque
import random

from snake import Snake
from model import Model, QTrainer
from helper import plot

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001

class Trainer:

    def __init__(self):
        self.games_played = 0
        self.gamma = 0.9 # discount rate

        self.moves = deque(maxlen=MAX_MEMORY)

        self.model = Model(12, 256, 4)
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)

    def get_game_state(self, game):
        future_left = game.future_head(game.LEFT)
        future_right = game.future_head(game.RIGHT)
        future_up = game.future_head(game.UP)
        future_down = game.future_head(game.DOWN)

        food_left = game.distance_between(future_left, game.food)
        food_right = game.distance_between(future_right, game.food)
        food_up = game.distance_between(future_up, game.food)
        food_down = game.distance_between(future_down, game.food)

        game_state = [
            # If death in any direction
            game.is_collision(future_left),
            game.is_collision(future_right),
            game.is_collision(future_up),
            game.is_collision(future_down),
            # move score
            # game.calculate_move_score(future_left, game.food),
            # game.calculate_move_score(future_right, game.food),
            # game.calculate_move_score(future_up, game.food),
            # game.calculate_move_score(future_down, game.food),
            # Current direction
            game.velocity == game.LEFT,
            game.velocity == game.RIGHT,
            game.velocity == game.UP,
            game.velocity == game.DOWN,
            # direction to food
            food_left < food_right,
            food_right < food_left,
            food_up < food_down,
            food_down < food_up,
        ]

        return np.array(game_state, dtype=int)

    def get_move(self, game, state):
        self.epsilon = 200 - self.games_played

        if random.randint(0, 200) < self.epsilon:
            print("random")
            return game.calculate_ai_random_move()
            # return game.calculate_ai_survival_move()
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            # print(state0)
            # print(prediction)
            print("AI move: ", game.DIRECTIONS[move])

            # import pdb; pdb.set_trace()

            return getattr(game, game.DIRECTIONS[move])

        # return game.calculate_ai_random_move()

    def get_max_frame(self, game):
        # Max number of frames a game can go on for so there is natural evolution
        return (game.score()*100)+100

    def play_and_calculate_reward(self, game, velocity):
        reward = 0
        score = game.score()

        # Play the frame
        game.play_frame(velocity)

        # End the game if we are over the max frame size
        if game.frame > self.get_max_frame(game):
            game.is_alive = False

        # Work out any reward changes
        if game.score() > score:
            # Give a reward for eating the food
            reward += 100

        if game.is_alive:
            # Potential reward for surviving?
            reward += 0
        else:
            # Add penalty for dying
            reward -= 10

        return reward

    def train_move(self, pre_state, move, reward, post_state, alive):
        self.trainer.train_move(pre_state, move, reward, post_state, alive)

        # Remember the move so we can train the whole game
        self.moves.append((pre_state, move, reward, post_state, alive))

    def train_game(self):
        if len(self.moves) > BATCH_SIZE:
            mini_sample = random.sample(self.moves, BATCH_SIZE) # list of tuples
        else:
            mini_sample = self.moves

        pre_states, moves, rewards, post_states, alives = zip(*mini_sample)
        self.trainer.train_move(pre_states, moves, rewards, post_states, alives)


def train():
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0

    trainer = Trainer()
    snake = Snake()

    while snake.is_running:
        snake.game_speed = 50
        if trainer.games_played < 2000:
            snake.game_speed = 1000

        # get current game state
        pre_state = trainer.get_game_state(snake)
        # print("pre", pre_state)

        # get move
        move_velocity = trainer.get_move(snake, pre_state)

        move = [0,0,0,0]
        for i, direction in enumerate(snake.DIRECTIONS):
            if move_velocity == getattr(snake, direction):
                move[i] = 1

        # perform the suggested move
        reward = trainer.play_and_calculate_reward(snake, move_velocity)
        # print("reward", reward)

        # get post move state
        post_state = trainer.get_game_state(snake)
        # print("post", post_state)

        # train on the move
        trainer.train_move(pre_state, move, reward, post_state, snake.is_alive)

        if not snake.is_alive:
            trainer.games_played += 1

            # Train for the whole game
            trainer.train_game()

            if snake.score() > record:
                record = snake.score()
                trainer.model.save()

            print('Game', trainer.games_played, 'Score', snake.score(), 'Record:', record)

            plot_scores.append(snake.score())
            total_score += snake.score()
            mean_score = total_score / trainer.games_played
            plot_mean_scores.append(mean_score)
            plot(plot_scores, plot_mean_scores)

            # Restart the game so we keep playing
            snake.reset()



if __name__ == '__main__':
    train()

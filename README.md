# Snake
Version of the classic Snake game using PyGame.

![Screenshot of the game](snake.gif)

To setup:
```
virtualenv -p python3 .venv
source .venv/bin/activate
pip install -r requirmements.txt
```

To run:
```
python snake.py
```

## Game settings
- Move with WASD or 🔼◀️🔽▶️
- Pause the game with the spacebar
- Adjust the game speed with 1-9
- Let the game play itself in cheat mode with `c`

## AI Options
There are a few different options that the computer can use in cheat mode:

### Random moves
Activated with `r`. This tells the computer to always use a completely random move.

### Path
Activated with `p`. This tells the computer to follow a path to hit every location.

### Survival
Activated with `t`. This scores each move based on the chance of survival of the move along with some incentive to move closer to the food.

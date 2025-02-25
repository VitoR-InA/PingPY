#Game vars
MAIN_STATE = 0
SHOP_STATE = 1
PREPARATION_STATE = 2
THROWING_STATE = 3
PLAYING_STATE = 4
END_STATE = 5
STATES = {val: var for var, val in globals().items() if var.endswith("_STATE")}

FPS_LOCK = 120

#GUI
GUI_SIZE = (280, 80)
GUI_SPACING = 5

#Colors
WHITE = (255, 255, 255, 255)
BLACK = (0, 0, 0, 255)
RED = (255, 0, 0, 255)
GREEN = (0, 255, 0, 255)
BLUE = (0, 0, 255, 255)

#Ball value
BALL_DEFAULT_COLOR = RED
BALL_DEFAULT_RADIUS = 10

#Player values
PLAYER_DEFAULT_DAMAGE = 1
PLAYER_DEFAULT_HEALTH = 3
PLAYER_DEFAULT_SCORE = 0
PLAYER_DEFAULT_SIZE = (250, 20)
PLAYER_DEFAULT_SPEED = 500

#Wall values
WALL_DEFAULT_WIDTH = 10
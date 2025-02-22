#Game vars
MENU_STATE = 0
SHOP_STATE = 1
PREPARATION_STATE = 2
THROWING_STATE = 3
PLAYING_STATE = 4
DIED_STATE = 5
WINNED_STATE = 6

STATES = {val: var for var, val in globals().items() if var.endswith("_STATE")}

FPS_LOCK = 120

#Colors
WHITE = (255, 255, 255, 255)
BLACK = (0, 0, 0, 255)
RED = (255, 0, 0, 255)
GREEN = (0, 255, 0, 255)
BLUE = (0, 0, 255, 255)


#Player values
PLAYER_DEFAULT_SPEED = 500
PLAYER_DEFAULT_HEALTH = 3
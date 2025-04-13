# config.py
import pygame

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_CORAL = (240, 128, 128)  # For start/end and solution path
CORN_FLOWER_BLUE = (100, 149, 237)  # For searched cells
BACKGROUND_COLOR = (186, 204, 217)  # Background color from CSS
BUTTON_COLOR = (255, 255, 255)  # White buttons
BUTTON_HOVER = (230, 210, 210)
HEADER_COLOR = (216, 227, 231)

# Fonts
pygame.font.init()
TITLE_FONT = pygame.font.SysFont("Arial", 48, bold=True)
TEXT_FONT = pygame.font.SysFont("Arial", 24)
BUTTON_FONT = pygame.font.SysFont("Arial", 20)
SMALL_FONT = pygame.font.SysFont("Arial", 18)

# Default Maze Dimensions
ROW_OPTIONS = [5, 10, 20, 30, 40, 50]
COL_OPTIONS = [5, 10, 20, 30, 40, 50]
DEFAULT_ROW_IDX = 2  # 20 rows
DEFAULT_COL_IDX = 2  # 20 cols

# Pathfinding modes
MODE_IDLE = 0
MODE_DFS = 1
MODE_BFS = 2
MODE_MANUAL = 3
MODE_A1 = 4
MODE_A2 = 5
MODE_UCS = 6  
MODE_ACO = 7  

# Window dimensions
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800

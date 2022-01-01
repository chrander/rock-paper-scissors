import os

import cv2

# Drawing and text
font = cv2.FONT_HERSHEY_SIMPLEX
font_line_type = cv2.LINE_AA
choice_font_color = (0, 255, 255)
choice_font_scale = 2
choice_font_thickness = 3
outcome_font_color_win = (0, 255, 0)
outcome_font_color_lose = (0, 0, 255)
outcome_font_color_draw = (200, 200, 200)
outcome_font_scale = 5
outcome_font_thickness = 14

# Game mechanics
WIN = 1
DRAW = 0
LOSS = -1

# String constants
QUIT = 'QUIT'

# Models
class_names = ['paper', 'rock', 'scissors']
models_dir = '/Users/chris/Documents/projects/rps/rock-paper-scissors/models'
model_path = os.path.join(models_dir, 'model_2021-12-27_2057.pth')
import os
from enum import Enum

import cv2

CURRENT_DIR = os.path.realpath(os.path.dirname(__file__))

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



# String constants
QUIT = "QUIT"

# Models
models_dir = os.path.join(CURRENT_DIR, "..", "models")
model_path = os.path.join(models_dir, "model_2021-12-27_2057.pth")

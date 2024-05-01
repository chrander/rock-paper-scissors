from dataclasses import dataclass
import os
from enum import Enum

import cv2

CURRENT_DIR = os.path.realpath(os.path.dirname(__file__))

# Game properties
game_id = 7

# Image properties
WINDOW_NAME = "Rock, Paper, Scissors"
# IMAGE_SIZE = (int(1280*3), int(720*3))
IMAGE_SIZE = (int(1920*2), int(1080*2))
VIDEO_SOURCE = 0  # 0: built-in camera; 1: webcam

# Drawing and text
font = cv2.FONT_HERSHEY_SIMPLEX
font_line_type = cv2.LINE_AA
choice_font_color = (0, 255, 255)
choice_font_scale = 2
choice_font_thickness = 3
outcome_font_color_win = (0, 255, 0)
outcome_font_color_lose = (0, 0, 255)
outcome_font_color_draw = (255, 50, 50)
outcome_font_scale = 4.5
outcome_font_thickness = 14


class RoundOutcome(Enum):
    """Outcomes for a round"""
    WIN = 1
    DRAW = 0
    LOSS = -1


class PlayerChoice(Enum):
    """Player choices"""
    PAPER = 0
    ROCK = 1
    SCISSORS = 2


class PlayerType(Enum):
    """Type of player"""
    HUMAN = "HUMAN"
    MACHINE = "MACHINE"


class PlayerStrategy(Enum):
    """Strategy used by the player (mostly useful for machine players)"""
    HUMAN = "HUMAN"
    RANDOM = "RANDOM"
    LEARN = "LEARN"


@dataclass
class Player:
    """Class for storing Player information"""
    name: str
    type: PlayerType
    strategy: PlayerStrategy = PlayerStrategy.HUMAN


# Order of this list is important--must match model prediction outputs
PLAYER_CHOICES = [PlayerChoice.PAPER, PlayerChoice.ROCK, PlayerChoice.SCISSORS]

# String constants
QUIT = "QUIT"

# Models
models_dir = os.path.join(CURRENT_DIR, "..", "models")
# model_path = os.path.join(models_dir, "yolov8n_tfdata.pt")
model_path = os.path.join(models_dir, "best.pt")

# Database
DATABASE_URI = os.path.join("sqlite:///rps.db")

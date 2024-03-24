from dataclasses import dataclass
from enum import Enum
import logging
import random

import cv2
import numpy as np

from rps.classify import get_choice_from_video
from rps import constants


logger = logging.getLogger(__name__)


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


class RPSRound:
    def __init__(
            self, 
            player1: Player, 
            player2: Player, 
            player1_choice: PlayerChoice,
            player2_choice: PlayerChoice
        ) -> None:
        self.player1 = player1
        self.player2 = player2
        self.player1_choice = player1_choice
        self.player2_choice = player2_choice
        self.outcome = self.determine_round_winner(player1_choice, player2_choice)
        
    @staticmethod
    def determine_round_winner(choice1: PlayerChoice, choice2: PlayerChoice) -> RoundOutcome:
        """Determines the result of one round from player 1's perspective

        Parameters
        ----------
        choice1 : PlayerChoice
            Player 1's choice (ROCK, PAPER, or SCISSORS)
        choice2 : PlayerChoice
            Player 2's choice (ROCK, PAPER, or SCISSORS)

        Returns
        -------
        RoundOutcome
            The outcome of the round from Player 1's perspective--WIN, DRAW, or LOSS
        """
        if choice1 == choice2:
            # Draw
            return RoundOutcome.DRAW

        if (choice1 == PlayerChoice.PAPER) and (choice2 == PlayerChoice.ROCK) \
                or (choice1 == PlayerChoice.SCISSORS) and (choice2 == PlayerChoice.PAPER) \
                or (choice1 == PlayerChoice.ROCK) and (choice2 == PlayerChoice.SCISSORS):
            # Choice 1 wins
            return RoundOutcome.WIN

        else:
            # Choice 2 wins (should be the only other valid options)
            return RoundOutcome.LOSS

class RPSGame:

    def __init__(self, player1: Player, player2: Player) -> None:
        self.player1 = player1
        self.player2 = player2
        self.rounds_played = 0
        self.player1_wins = 0
        self.player2_wins = 0
        self.draws = 0

    def get_player_choice(self, player: Player) -> tuple[str, PlayerChoice]:
        """Gets the rock/paper/scissors choice for a player"""
        if player.type == PlayerType.HUMAN:
            img, player_choice = get_choice_from_video()

        elif player.type == PlayerType.MACHINE:
            if player.strategy == PlayerStrategy.RANDOM:
                # Use a random strategy--no image output for machine, so
                # use "None" as the image component of the choice
                img = None
                player_choice = random.choice(constants.class_names)

            else:
                # Use a learning strategy
                raise NotImplementedError
        else:
            raise ValueError(f"Unknown player type: {player.type}")

        return img, player_choice

    def play_round(self) -> bool:
        """Plays a single RPS round
        
        Returns
        -------
        bool
            Whether to play another round
        """
        # Get player choices
        img1, player1_choice = self.get_player_choice(self.player1)
        img2, player2_choice = self.get_player_choice(self.player2)

        # If either player quits, return False
        if player1_choice == constants.QUIT or player2_choice == constants.QUIT:
            logger.info("Player choice quit option. Quitting")
            return False

        # Decide which image to draw on, if any
        if img1 is None and img2 is None:
            # We won't display an image, just play the game
            img = None
        elif img2 is None:
            # Use player 1's image
            img = img1
        else:
            # Use player 2's image
            img = img2

        # Create a new round object. Also determines the outcome
        game_round = RPSRound(self.player1, self.player2, player1_choice, player2_choice)

        # Display the round outcome on the image
        self.display_round_outcome(img, game_round) 
        
        # Print stats
        self.print_stats()

        # Wait for user input. If player presses 'q', quit; otherwise play again
        key = cv2.waitKey(0) & 0xFF
        if key == ord('q'):
            # Player quit
            return False
        else:
            # Play another round
            return True

    def display_round_outcome(self, img: np.array, game_round: RPSRound) -> None:
        result_str = (f" {self.player1.name} choice: {game_round.player1_choice.name}.",
                      f" {self.player2.name} choice: {game_round.player2_choice.name}.")
        outcome_text = ""
        if game_round.outcome == RoundOutcome.DRAW:
            # Draw
            self.draws += 1
            outcome_text = "DRAW!"
            outcome_font_color = constants.outcome_font_color_draw
            logger.info(f"{result_str} Draw!")
        elif game_round.outcome == RoundOutcome.WIN:
            # Win for player 1
            self.player1_wins += 1
            outcome_text = "YOU WIN!"
            outcome_font_color = constants.outcome_font_color_win
            logger.info(f"{result_str} {game_round.player1.name} Wins!")
        else:
            # Loss for player 1
            self.player2_wins += 1
            outcome_text = "YOU LOSE!"
            outcome_font_color = constants.outcome_font_color_lose
            logger.info(f"{result_str} {game_round.player2.name} Wins!")

        self.rounds_played += 1

        # These lines allow us to center the outcome text horizontally
        # get boundary of the outcome text
        outcome_text_size = cv2.getTextSize(outcome_text, 
                                            constants.font, 
                                            constants.outcome_font_scale, 
                                            constants.outcome_font_thickness)[0]
        # get coords based on boundary
        outcome_textX = int((img.shape[1] - outcome_text_size[0]) / 2)
        # outcome_textY = (img.shape[0] + outcome_text_size[1]) / 2

        if img is not None:
            height, width = img.shape[:2]
            logger.debug(f"Img shape: {height}, {width}")
            cv2.putText(img, f"{self.player1.name} choice: {game_round.player1_choice.name}", (10, 50), 
                        constants.font, 
                        constants.choice_font_scale, 
                        constants.choice_font_color, 
                        constants.choice_font_thickness, 
                        constants.font_line_type)
            cv2.putText(img, f"{self.player2.name} choice: {game_round.player2_choice.name}", (10, 120), 
                        constants.font, 
                        constants.choice_font_scale, 
                        constants.choice_font_color, 
                        constants.choice_font_thickness, 
                        constants.font_line_type)
            cv2.putText(img, outcome_text, (outcome_textX, height - 100), 
                        constants.font, 
                        constants.outcome_font_scale, 
                        outcome_font_color, 
                        constants.outcome_font_thickness, 
                        constants.font_line_type)
            cv2.putText(img, "Press any key to play again, q to quit", (10, height-10), 
                        constants.font, 1, constants.choice_font_color, 2, constants.font_line_type)
            cv2.imshow("Rock, Paper, Scissors", img)

    def print_stats(self) -> None:
        """Prints wins and winning percentages"""
        print(f" {self.player1.name} record: {self.player1_wins} wins, {self.player2_wins} losses, {self.draws} draws")
        if self.player1_wins == 0:
            player_1_winning_pct = 0.0
        else:
            decisive_rounds = self.player1_wins + self.player2_wins
            player_1_winning_pct = self.player1_wins / decisive_rounds
        print(f" {self.player1.name} Winning percentage: {player_1_winning_pct:.3f}")


@dataclass
class RoundResult:
    player1_name: str
    player2_name: str
    player1_choice: PlayerChoice
    player2_choice: PlayerChoice
    outcome: str

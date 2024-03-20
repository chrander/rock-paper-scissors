from dataclasses import dataclass
import logging
import random

import cv2

from rps.classify import get_choice_from_video
from rps import constants
from rps.constants import Outcome, PlayerChoice


logger = logging.getLogger(__name__)


class RPSRound:

    def __init__(self, player1_name, player2_name) -> None:
        self.player1_name = player1_name
        self.player2_name = player2_name

    def get_player2_choice(self) -> str:
        """Gets the machine's rock/paper/scissors choice for a single round"""
        # Using a random strategy
        machine_choice = random.choice(constants.class_names)
        return machine_choice

    def get_player1_choice(self) -> str:
        """Gets the human's rock/paper/scissors choice for a single round"""
        img, human_choice = get_choice_from_video()
        return img, human_choice

    def play(self):
        """Plays a single rock, paper, scissors round"""
        logger.info(f'*****  Round {self.rounds} *****')
        img, human_choice = self.get_player1_choice()
        machine_choice = self.get_player2_choice()

        result_str = f'  {self.player1_name} choice: {human_choice}. Machine Choice: {machine_choice}.'

        if human_choice == constants.QUIT:
            logger.info('Quitting')
            return False

        outcome_text = ''
        outcome = self.determine_round_winner(human_choice, machine_choice)
        if outcome == Outcome.DRAW:
            self.draws += 1
            outcome_text = 'DRAW'
            outcome_font_color = constants.outcome_font_color_draw
            logger.info(f'{result_str} Draw!')
        elif outcome == Outcome.WIN:
            self.human_wins += 1
            outcome_text = 'YOU WIN!'
            outcome_font_color = constants.outcome_font_color_win
            logger.info(f'{result_str} Human Wins!')
        else:
            self.machine_wins += 1
            outcome_text = 'YOU LOSE!'
            outcome_font_color = constants.outcome_font_color_lose
            logger.info(f'{result_str} Machine Wins!')

        self.rounds += 1
        # These lines allow us to center the outcome text horizontally
        # get boundary of the outcome text
        outcome_text_size = cv2.getTextSize(outcome_text, 
                                            constants.font, 
                                            constants.outcome_font_scale, 
                                            constants.outcome_font_thickness)[0]
        # get coords based on boundary
        outcome_textX = int((img.shape[1] - outcome_text_size[0]) / 2)
        # outcome_textY = (img.shape[0] + outcome_text_size[1]) / 2

        height, width = img.shape[:2]
        logger.debug(f'Img shape: {height}, {width}')
        cv2.putText(img, f'Your choice: {human_choice}', (10, 50), 
                    constants.font, 
                    constants.choice_font_scale, 
                    constants.choice_font_color, 
                    constants.choice_font_thickness, 
                    constants.font_line_type)
        cv2.putText(img, f'Machine choice: {machine_choice}', (10, 120), 
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
        cv2.putText(img, 'Press any key to play again, q to quit', (10, height-10), 
                    constants.font, 1, constants.choice_font_color, 2, constants.font_line_type)
        cv2.imshow('Rock, Paper, Scissors', img)
        
        self.print_stats()
        
        key = cv2.waitKey(0) & 0xFF
        if key == ord('q'):
            return False
        else:
            return True

    def print_stats(self):
        """Prints wins and winning percentages"""
        print(f' .    Human record: {self.human_wins} wins, {self.machine_wins} losses, {self.draws} draws')
        total_wins = self.human_wins + self.machine_wins
        if total_wins == 0:
            winning_pct = 0.0
        else:
            winning_pct = self.human_wins / total_wins
        print(f'Winning percentage: {winning_pct:.3f}')

    @staticmethod
    def determine_round_winner(choice1, choice2) -> int:
        """Determines the result of one round"""
        # Make sure we have valid inputs
        if (choice1 not in constants.class_names) or (choice2 not in constants.class_names):
            raise ValueError(f'Unrecognized choice: {choice1} or {choice2}')

        if choice1 == choice2:
            # Draw
            return Outcome.DRAW

        if (choice1 == PlayerChoice.PAPER) and (choice2 == PlayerChoice.ROCK) \
                or (choice1 == PlayerChoice.SCISSORS) and (choice2 == PlayerChoice.PAPER) \
                or (choice1 == PlayerChoice.ROCK) and (choice2 == PlayerChoice.SCISSORS):
            # Choice 1 wins
            return Outcome.WIN

        else:
            # Choice 2 wins (should be the only other valid options)
            return Outcome.LOSS

@dataclass
class RoundResult:
    player1_name: str
    player2_name: str
    player1_choice: PlayerChoice
    player2_choice: PlayerChoice
    outcome: str
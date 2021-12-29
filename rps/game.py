import random
import logging

from rps import class_names
from rps.classify import get_choice_from_video


logger = logging.getLogger(__name__)


class RPSGame:

    def __init__(self) -> None:
        self.rounds = 0
        self.human_wins = 0
        self.machine_wins = 0
        self.draws = 0

    def get_machine_choice(self) -> str:
        # Using a random strategy
        machine_choice = random.choice(class_names)
        return machine_choice

    def get_human_choice(self) -> str:
        human_choice = get_choice_from_video()
        return human_choice

    def play_round(self):
        self.rounds += 1
        logger.info(f'*****  Round {self.rounds} *****')
        machine_choice = self.get_machine_choice()
        human_choice = self.get_human_choice()

        result_str = f'  Human choice: {human_choice}. Machine Choice: {machine_choice}.'

        if human_choice == 'QUIT':
            logger.info('Quitting')

            return False

        else:
            outcome = self.determine_round_winner(human_choice, machine_choice)
            if outcome == 0:
                self.draws += 1
                logger.info(f'{result_str} Draw!')
            elif outcome > 0:
                self.human_wins += 1
                logger.info(f'{result_str} Human Wins!')
            else:
                self.machine_wins += 1
                logger.info(f'{result_str} Machine Wins!')
            self.print_stats()
            return True

    def print_stats(self):
        print(f' .    Human record: {self.human_wins} wins, {self.machine_wins} losses, {self.draws} draws')
        print(f'Winning percentage: {self.human_wins / (self.human_wins + self.machine_wins)}')

    @staticmethod
    def determine_round_winner(choice1, choice2) -> int:
        """Determines the result of one round"""
        # Make sure we have valid inputs
        if (choice1 not in class_names) or (choice2 not in class_names):
            raise ValueError(f'Unrecognized choice: {choice1} or {choice2}')
        
        if choice1 == choice2:
            # Draw
            return 0

        if (choice1 == 'paper') and (choice2 == 'rock') \
               or (choice1 == 'scissors') and (choice2 == 'paper') \
               or (choice1 == 'rock') and (choice2 == 'scissors'):
            # Choice 1 wins
            return 1

        else:
            # Choice 2 wins (should be the only other valid options)
            return -1
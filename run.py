
from rps.game import RPSGame

game = RPSGame()

play_again = True
while play_again:
    play_again = game.play_round()

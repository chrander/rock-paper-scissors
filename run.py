from rps.game import RPSGame, Player, PlayerType, PlayerStrategy
from rps.constants import game_id


def play(player1, player2) -> None:

    game = RPSGame(player1, player2, game_id=game_id)
    play_another_round = True

    while play_another_round:
        play_another_round = game.play_round()


if __name__ == "__main__":
    human_name = "Human"
    computer_name = "Computer"

    human_player = Player(human_name, PlayerType.HUMAN, PlayerStrategy.HUMAN)
    computer_player = Player(computer_name, PlayerType.MACHINE, PlayerStrategy.RANDOM)

    play(human_player, computer_player)

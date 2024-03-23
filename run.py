from rps.game import RPSGame, Player, PlayerType, PlayerStrategy


def play(player1, player2) -> None:

    game = RPSGame(player1, player2)
    play_another_round = True

    while play_another_round:
        play_another_round = game.play_round()


if __name__ == "__main__":
    human_name = "Human"
    computer_name = "Computer"

    human_player = Player(human_name, PlayerType.HUMAN, PlayerStrategy.HUMAN)
    computer_player = Player(computer_name, PlayerType.MACHINE, PlayerStrategy.RANDOM)

    play(human_player, computer_player)


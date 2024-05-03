from rps.gameplay.game import RPSGame, Player, PlayerType, PlayerStrategy


def play(player1: Player, player2: Player, game_id: int = None) -> None:
    game = RPSGame(player1, player2, game_id=game_id)
    play_another_round = True

    while play_another_round:
        play_another_round = game.play_round()


if __name__ == "__main__":
    human_name = "Human"
    computer_name = "Computer"
    game_id = 7

    human_player = Player(human_name, PlayerType.HUMAN, PlayerStrategy.HUMAN)
    computer_player = Player(computer_name, PlayerType.MACHINE, PlayerStrategy.LEARN)

    play(human_player, computer_player, game_id=game_id)

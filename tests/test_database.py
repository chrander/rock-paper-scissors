from datetime import datetime
import logging
import os

from rps.database import DatabaseClient
from rps.constants import RPSGame, RPSRound 


logger = logging.getLogger(__name__)

def test_database_client(db_path: str) -> None:
    client = DatabaseClient(connection_string=db_path)
    client.drop_tables()
    client.create_tables()

    rps_game = RPSGame(
        game_id=1,
        game_timestamp=datetime.now(),
        player1_name="player1", 
        player1_type="HUMAN", 
        player1_strategy="HUMAN",
        player2_name="player2",
        player2_type="MACHINE",
        player2_strategy="RANDOM"
    )

    rps_round = RPSRound(
        round_id=1,
        game_id=1,
        round_timestamp=datetime.now(),
        player1_choice="ROCK",
        player2_choice="SCISSORS",
        outcome="WIN"
    )

    client.insert_game(rps_game)
    client.insert_round(rps_round)
    games = client.select_all_games()
    rounds = client.select_all_rounds()
    client.close()

    logger.debug(f"Games: {games}")
    logger.debug(f"Rounds: {rounds}")


if __name__ == "__main__":
    db_path = "./test.db"
    # if os.path.isfile(db_path):
    #     logger.debug(f"Deleting file: {db_path}")
    #     os.remove(db_path)
    
    test_database_client(db_path)
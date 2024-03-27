from datetime import datetime
import logging
import os

from rps.database.client import DatabaseClient
from rps.database.models import Game, Round


logger = logging.getLogger(__name__)

def test_database_client(db_path: str) -> None:
    client = DatabaseClient(database_uri=db_path)
    client.create_tables()

    rps_game = Game(
        player1_name="player1", 
        player1_type="HUMAN", 
        player1_strategy="HUMAN",
        player2_name="player2",
        player2_type="MACHINE",
        player2_strategy="RANDOM"
    )

    rps_round = Round(
        game_id=1,
        timestamp=datetime.now(),
        player1_choice="ROCK",
        player2_choice="SCISSORS",
        outcome="WIN"
    )

    client.insert_artifact(rps_game)
    client.add_round_to_game(rps_round, 1)
    games = client.select_all_games()
    rounds = client.select_all_rounds()

    logger.debug(f"Games: {games}")
    logger.debug(f"Rounds: {rounds}")


if __name__ == "__main__":
    db_uri= "sqlite:///test.db"
    db_path = "./test.db"
    if os.path.isfile(db_path):
        logger.debug(f"Deleting file: {db_path}")
        os.remove(db_path)
    
    test_database_client(db_uri)
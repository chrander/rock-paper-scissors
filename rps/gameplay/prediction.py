import numpy as np
import pandas as pd

from rps.constants import DATABASE_URI
from rps.database.client import DatabaseClient


class Featurizer:

    def __init__(
        self,
        game_id: int,
        database_uri: str = DATABASE_URI,
        history_length: int = 10
    ) -> None:
        self.game_id = game_id
        self.db_client = DatabaseClient(database_uri=database_uri)
        self.db_game = self.db_client.select_game(self.game_id)
        self.history_length = history_length

    def get_history(self) -> np.array:
        history = [r.outcome for r in self.db_game.rounds]
        return history

    def get_features(self, round_history) -> pd.DataFrame:
        print(round_history)

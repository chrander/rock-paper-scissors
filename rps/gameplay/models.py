from abc import ABC, abstractmethod
import logging
import random

import numpy as np
import pandas as pd

from rps.constants import PlayerChoice, DATABASE_URI, PLAYER_CHOICES
from rps.database.client import DatabaseClient


logger = logging.getLogger(__name__)
db_client = DatabaseClient(database_uri=DATABASE_URI)


def beats(choice: PlayerChoice):
    value = (choice.value - 1) % 3
    return PlayerChoice(value)


def loses_to(choice: PlayerChoice):
    value = (choice.value + 1) % 3
    return PlayerChoice(value)


def get_round_score(predict_choice: PlayerChoice, actual_choice: PlayerChoice) -> int:
    if predict_choice == beats(actual_choice):
        return 1
    elif predict_choice == loses_to(actual_choice):
        return -1
    else:
        return 0


class RPSModel(ABC):

    def __init__(self, name: str) -> None:
        self.name = name
        self.results_df = None
        self.score = -100.0  # Set to something very small

    @abstractmethod
    def predict(self, round_history_df: pd.DataFrame) -> PlayerChoice:
        pass

    def update_results(
            self, 
            round_history_df: pd.DataFrame, 
            n: int = 7
        ) -> None:
        results = {
            "pred_choice": [],
            "true_choice": []
        }

        for i in range(n):
            current_hist_df = round_history_df.iloc[i+1:i+n+1]
            pred_choice = self.predict(current_hist_df)
            true_choice = PlayerChoice[round_history_df.iloc[i].player1_choice]

            results["pred_choice"].append(pred_choice)
            results["true_choice"].append(true_choice)

        self.results_df = pd.DataFrame(results)
        self.results_df["score"] = self.results_df.apply(
            lambda row: get_round_score(row.pred_choice, row.true_choice), axis=1
        )

    def update_score(self) -> None:
        round_scores = self.results_df.score.values
        n = len(round_scores)
        numerator = np.sum(round_scores * (n ** 2))
        denominator = np.sum(n ** 2)
        self.score = numerator / denominator


class PreviousChoiceModel(RPSModel):
    def __init__(self) -> None:
        name = "Previous Choice"
        super().__init__(name)

    def predict(self, history_df: pd.DataFrame, n: int = 7) -> PlayerChoice:
        previous_choice = PlayerChoice[history_df.iloc[0].player1_choice]
        return beats(previous_choice)


class MostFrequentChoiceModel(RPSModel):
    def __init__(self) -> None:
        name = "Most Frequent Choice"
        super().__init__(name)

    def predict(self, history_df: pd.DataFrame, n: int = 7) -> PlayerChoice:
        choice_counts = history_df.player1_choice.value_counts()
        most_frequent_choice = PlayerChoice[choice_counts.index[0]]
        return beats(most_frequent_choice)


class LeastFrequentChoiceModel(RPSModel):
    def __init__(self) -> None:
        name = "Least Frequent Choice"
        super().__init__(name)

    def predict(self, history_df: pd.DataFrame, n: int = 7) -> PlayerChoice:
        choice_counts = history_df.player1_choice.value_counts()
        least_frequent_choice = PlayerChoice[choice_counts.index[-1]]
        return beats(least_frequent_choice)


def get_round_history(game_id: int, n: int = 10) -> pd.DataFrame:
    sql = f"SELECT * FROM rounds WHERE game_id = {game_id} ORDER BY timestamp DESC LIMIT {n}"
    df = pd.read_sql(sql, con=db_client.engine)
    return df


def random_prediction() -> PlayerChoice:
    return random.choice(PLAYER_CHOICES)


def get_prediction(game_id: int, n: int = 7):
    round_history_df = get_round_history(game_id, n=2*n)

    models = [
        PreviousChoiceModel(),
        MostFrequentChoiceModel(),
        LeastFrequentChoiceModel()
    ]

    for model in models:
        logger.debug(f"Updating {model.name}")
        logger.debug(f"Type of model: {type(model)}")
        model.update_results(round_history_df, n=n)
        model.update_score()
        logger.debug(f"{model.name} score is {model.score}")

    # Compute model scores and select the model with the highest score
    model_scores =  [m.score for m in models]

    best_idx = np.argmax(model_scores)
    best_model = models[best_idx]
    logger.debug(f"Best model: {best_model.name} (index {best_idx})")

    # Use prediction for the best prediction
    prediction = best_model.predict(round_history_df, n=n)
    return prediction


if __name__ == "__main__":
    # print(get_model_history(7))
    print(get_prediction(58))

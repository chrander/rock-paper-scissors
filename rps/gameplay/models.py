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

    def __init__(self, name: str, min_datapoints: int = 5, max_datapoints: int = 10) -> None:
        self.name = name
        self.min_datapoints = min_datapoints
        self.max_datapoints = max_datapoints
        self.results_df = None
        self.score = -100.0  # Set to something very small

    @abstractmethod
    def predict(self, round_history_df: pd.DataFrame) -> PlayerChoice:
        pass

    def update_results(self, round_history_df: pd.DataFrame) -> None:

        # Require at least twice the number of minimum data points to
        # get a valid score for the model
        if len(round_history_df) < 2*self.min_datapoints:
            logger.debug(f"Round history has only {len(round_history_df)} points. "
                         f"Setting results for model {self.name} to None")
            self.results_df = None
            return

        results = {
            "pred_choice": [],
            "true_choice": []
        }

        print()
        n = np.minimum(np.floor(len(round_history_df) / 2), self.max_datapoints)
        n = int(n)
        logger.debug(f"Computing model {self.name} history for {n} datapoints")
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
        if self.results_df is None:
            logger.debug(f"Model {self.name} has no results. Setting score to -1.")
            self.score = -1
        else:
            round_scores = self.results_df.score.values
            print(round_scores)
            n = len(round_scores)
            index = np.arange(1, n+1)[::-1]
            print(index)
            numerator = np.sum(round_scores * (index ** 2))
            denominator = np.sum(index ** 2)
            self.score = numerator / denominator


class PreviousChoiceModel(RPSModel):
    def __init__(self, min_datapoints: int = 1, max_datapoints: int = 7) -> None:
        name = "Previous Choice"
        super().__init__(name, min_datapoints=min_datapoints, max_datapoints=max_datapoints)

    def predict(self, history_df: pd.DataFrame) -> PlayerChoice:
        if len(history_df) < self.min_datapoints:
            logger.info(f"Returning random prediction for {self.name}")
            return random_prediction()
        else:
            previous_choice = PlayerChoice[history_df.iloc[0].player1_choice]
            prediction = beats(previous_choice)
            return prediction


class BeatsPreviousChoiceModel(RPSModel):
    def __init__(self, min_datapoints: int = 1, max_datapoints: int = 7) -> None:
        name = "Beats Previous Choice"
        super().__init__(name, min_datapoints=min_datapoints, max_datapoints=max_datapoints)

    def predict(self, history_df: pd.DataFrame) -> PlayerChoice:
        if len(history_df) < self.min_datapoints:
            logger.info(f"Returning random prediction for {self.name}")
            return random_prediction()
        else:
            previous_choice = PlayerChoice[history_df.iloc[0].player1_choice]
            next_choice = beats(previous_choice)
            prediction = beats(next_choice)
            return prediction


class LosesToPreviousChoiceModel(RPSModel):
    def __init__(self, min_datapoints: int = 1, max_datapoints: int = 7) -> None:
        name = "Loses To Previous Choice"
        super().__init__(name, min_datapoints=min_datapoints, max_datapoints=max_datapoints)

    def predict(self, history_df: pd.DataFrame) -> PlayerChoice:
        if len(history_df) < self.min_datapoints:
            logger.info(f"Returning random prediction for {self.name}")
            return random_prediction()
        else:
            previous_choice = PlayerChoice[history_df.iloc[0].player1_choice]
            next_choice = loses_to(previous_choice)
            prediction = beats(next_choice)
            return prediction


class MostFrequentChoiceModel(RPSModel):
    def __init__(self, min_datapoints: int = 1, max_datapoints: int = 7) -> None:
        name = "Most Frequent Choice"
        super().__init__(name, min_datapoints=min_datapoints, max_datapoints=max_datapoints)

    def predict(self, history_df: pd.DataFrame) -> PlayerChoice:
        if len(history_df) < self.min_datapoints:
            logger.info(f"Returning random prediction for {self.name}")
            return random_prediction()
        else:
            choice_counts = history_df.player1_choice.value_counts()
            most_frequent_choice = PlayerChoice[choice_counts.index[0]]
            prediction = beats(most_frequent_choice)
            return prediction


class LeastFrequentChoiceModel(RPSModel):
    def __init__(self, min_datapoints: int = 1, max_datapoints: int = 10) -> None:
        name = "Least Frequent Choice"
        super().__init__(name, min_datapoints=min_datapoints, max_datapoints=max_datapoints)

    def predict(self, history_df: pd.DataFrame) -> PlayerChoice:
        if len(history_df) < self.min_datapoints:
            logger.info(f"Returning random prediction for {self.name}")
            return random_prediction()
        else:
            choice_counts = history_df.player1_choice.value_counts()
            least_frequent_choice = PlayerChoice[choice_counts.index[-1]]
            prediction = beats(least_frequent_choice)
            return prediction


class RandomModel(RPSModel):
    def __init__(self, min_datapoints: int = 1, max_datapoints: int = 10) -> None:
        name = "Random"
        super().__init__(name, min_datapoints=min_datapoints, max_datapoints=max_datapoints)

    def predict(self, history_df: pd.DataFrame) -> PlayerChoice:
        return random_prediction()


def get_round_history(game_id: int, n: int = 10) -> pd.DataFrame:
    sql = f"SELECT * FROM rounds WHERE game_id = {game_id} ORDER BY timestamp DESC LIMIT {n}"
    df = pd.read_sql(sql, con=db_client.engine)
    return df


def random_prediction() -> PlayerChoice:
    return random.choice(PLAYER_CHOICES)


def get_prediction(game_id: int, n: int = 12) -> PlayerChoice:
    round_history_df = get_round_history(game_id, n=2*n)

    # TODO: don't instantiate new models for each prediction cycle
    models = [
        PreviousChoiceModel(min_datapoints=1, max_datapoints=5),
        BeatsPreviousChoiceModel(min_datapoints=1, max_datapoints=5),
        LosesToPreviousChoiceModel(min_datapoints=1, max_datapoints=5),
        MostFrequentChoiceModel(min_datapoints=1, max_datapoints=12),
        LeastFrequentChoiceModel(min_datapoints=1, max_datapoints=12),
        RandomModel(min_datapoints=1, max_datapoints=12)
    ]

    for model in models:
        logger.debug(f"Updating {model.name}")
        model.update_results(round_history_df)
        model.update_score()
        logger.debug(f"{model.name} score is {model.score}")

    # Compute model scores and select the model with the highest score
    model_scores = [m.score for m in models]

    best_idx = np.argmax(model_scores)
    best_model = models[best_idx]
    prediction = best_model.predict(round_history_df)
    logger.info(f"Best model: {best_model.name} (index {best_idx}) predicts {prediction}")

    # Use prediction for the best prediction
    return prediction


if __name__ == "__main__":
    # print(get_model_history(7))
    print(get_prediction(58))

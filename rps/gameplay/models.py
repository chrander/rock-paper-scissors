import random

import numpy as np
import pandas as pd

from rps.constants import PlayerChoice, DATABASE_URI, PLAYER_CHOICES
from rps.database.client import DatabaseClient


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


def score_model(model_score_history: pd.Series) -> float:
    n = len(model_score_history)
    numerator = np.sum(model_score_history * (n ** 2))
    denominator = np.sum(n ** 2)
    score = numerator / denominator
    return score


def get_round_history(game_id: int, n: int = 10) -> pd.DataFrame:
    sql = f"SELECT * FROM rounds WHERE game_id = {game_id} ORDER BY timestamp DESC LIMIT {n}"
    df = pd.read_sql(sql, con=db_client.engine)
    return df


def previous_choice_model(history_df: pd.DataFrame) -> PlayerChoice:
    """Selects the choice that would beat the opponent's previous choice"""
    # history_df should already be sorted in descending timestamp order, so take the
    # first row as the previous choice
    previous_choice = PlayerChoice[history_df.iloc[0].player1_choice]
    return beats(previous_choice)


def choice_frequency_model(history_df: pd.DataFrame) -> PlayerChoice:
    """Selects the choices that beat the most frequent and least frequent choices"""
    choice_counts = history_df.player1_choice.value_counts()
    most_frequent_choice = PlayerChoice[choice_counts.index[0]]
    least_frequent_choice = PlayerChoice[choice_counts.index[-1]]
    return beats(most_frequent_choice), beats(least_frequent_choice)


def xgb_model(history_df: pd.DataFrame) -> PlayerChoice:
    pass


def random_prediction() -> PlayerChoice:
    return random.choice(PLAYER_CHOICES)


def get_model_predictions(history_df: pd.DataFrame, n: int = 7):
    k = len(history_df)
    if k < 1:
        prev_choice_pred = random_prediction()
        most_freq_choice_pred = random_prediction()
        least_freq_choice_pred = random_prediction()
    else:
        prev_choice_pred = previous_choice_model(history_df)
        most_freq_choice_pred, least_freq_choice_pred = choice_frequency_model(history_df.iloc[:n])

    model_preds = [
        prev_choice_pred,
        most_freq_choice_pred,
        least_freq_choice_pred
    ]
    return model_preds


def get_model_history(game_id: int, n: int = 7):
    history_df = get_round_history(game_id, n=2*n)
    results = {
        "previous_choice_pred": [],
        "most_freq_choice_pred": [],
        "least_freq_choice_pred": [],
        "choice": []
    }

    for i in range(n):
        current_hist_df = history_df.iloc[i+1:i+n+1]
        prev_choice_pred = previous_choice_model(current_hist_df)
        most_freq_choice_pred, least_freq_choice_pred = choice_frequency_model(current_hist_df)
        choice = PlayerChoice[history_df.iloc[i].player1_choice]

        results["previous_choice_pred"].append(prev_choice_pred)
        results["most_freq_choice_pred"].append(most_freq_choice_pred)
        results["least_freq_choice_pred"].append(least_freq_choice_pred)
        results["choice"].append(choice)

    results_df = pd.DataFrame(results)
    results_df["previous_choice_score"] = results_df.apply(
        lambda row: get_round_score(row.previous_choice_pred, row.choice), axis=1)
    results_df["most_freq_choice_score"] = results_df.apply(
        lambda row: get_round_score(row.most_freq_choice_pred, row.choice), axis=1)
    results_df["least_freq_choice_score"] = results_df.apply(
        lambda row: get_round_score(row.least_freq_choice_pred, row.choice), axis=1)

    return results_df


if __name__ == "__main__":
    print(get_model_history(7))

import sqlite3

from rps.constants import DATABASE_PATH, RPSRound, RPSGame


class DatabaseClient:

    def __init__(self, connection_string: str = DATABASE_PATH) -> None:
        self.connection_string = connection_string
        self.conn = sqlite3.connect(self.connection_string, 
                                    detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)

    def close(self) -> None:
        self.conn.close()

    def drop_tables(self) -> None:
        cur = self.conn.cursor()
        cur.execute("DROP TABLE IF EXISTS games")
        cur.execute("DROP TABLE IF EXISTS rounds")

    def create_tables(self) -> None:
        create_games_sql = "CREATE TABLE games( \
                game_id INTEGER PRIMARY KEY AUTOINCREMENT, \
                game_timestamp TIMESTAMP, \
                player1_name TEXT, player1_type TEXT, player1_strategy TEXT, \
                player2_name TEXT, player2_type TEXT, player2_strategy TEXT)"

        create_results_sql = "CREATE TABLE rounds( \
                round_id INTEGER PRIMARY KEY AUTOINCREMENT, \
                round_timestamp TIMESTAMP, game_id INTEGER, \
                player1_choice TEXT, player2_choice TEXT, player1_outcome TEXT)"

        cur = self.conn.cursor() 
        cur.execute(create_games_sql)
        cur.execute(create_results_sql)

    def insert_game(self, game: RPSGame) -> None:
        sql = "INSERT INTO games(game_id, game_timestamp, player1_name, player1_type, player1_strategy, \
               player2_name, player2_type, player2_strategy) \
               VALUES (:game_id, :game_timestamp, :player1_name, :player1_type, :player1_strategy, \
               :player2_name, :player2_type, :player2_strategy)"
        cur = self.conn.cursor()
        cur.execute(sql, game.__dict__)
        self.conn.commit()

    def insert_round(self, round: RPSRound) -> None:
        sql = "INSERT INTO rounds(round_id, round_timestamp, game_id, \
               player1_choice, player2_choice, player1_outcome) VALUES \
               (:round_id, :round_timestamp, :game_id, :player1_choice, :player2_choice, :outcome)"
        cur = self.conn.cursor()
        cur.execute(sql, round.__dict__)
        self.conn.commit()

    def select_all_games(self) -> list:
        sql = "SELECT * FROM games"
        cur = self.conn.cursor()
        cur.execute(sql)
        results = cur.fetchall()
        return results
        
    def select_all_rounds(self) -> list:
        sql = "SELECT * FROM rounds"
        cur = self.conn.cursor()
        cur.execute(sql)
        results = cur.fetchall()
        return results


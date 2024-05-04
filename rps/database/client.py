from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from rps.constants import DATABASE_URI, RoundOutcome
from rps.database.models import Base, Game, Round, GameStats


class DatabaseClient:

    def __init__(self, database_uri: str = DATABASE_URI) -> None:
        self.database_uri = database_uri
        self.engine = create_engine(self.database_uri)
        self.create_tables()

        # Keep a session open
        self.session = Session(self.engine)

    def close(self) -> None:
        self.session.close()

    def create_tables(self) -> None:
        Base.metadata.create_all(self.engine)

    def insert_game(self, game: Game) -> None:
        game.game_stats = GameStats()
        self.session.add(game)
        self.session.commit()

    def select_game(self, game_id: int) -> Game:
        statement = select(Game).where(Game.game_id == game_id)
        result = self.session.scalars(statement).one()
        return result

    def select_most_recent_game(self) -> Game:
        """Retrieves game with mimimum created time"""
        stmt = select(Game).order_by(Game.created_time.desc()).limit(1)
        result = self.session.scalars(stmt).one()
        return result

    def select_all_games(self) -> list:
        statement = select(Game)
        results = self.session.scalars(statement).all()
        return results

    def select_all_rounds(self) -> list:
        statement = select(Round)
        results = self.session.scalars(statement).all()
        return results

    def select_rounds_by_game_id(self, game_id: int) -> None:
        statement = select(Round).where(Round.game_id == game_id)
        results = self.session.scalars(statement).all()
        return results

    def add_round_by_game_id(self, round: Round, game_id: int) -> None:
        statement = select(Game).where(Game.game_id == game_id)
        game = self.session.scalars(statement).one()
        game.rounds.append(round)
        self.session.commit()

    def add_round_to_game(self, game: Game, round: Round) -> None:
        game.rounds.append(round)
        self._update_game_stats(game, round)
        self.session.commit()

    def _update_game_stats(self, game: Game, round: Round) -> None:
        if round.outcome == RoundOutcome.WIN.name:
            game.game_stats.win_count += 1
        elif round.outcome == RoundOutcome.LOSS.name:
            game.game_stats.loss_count += 1
        else:
            game.game_stats.draw_count += 1

        wins = game.game_stats.win_count
        losses = game.game_stats.loss_count
        if wins == 0:
            game.game_stats.win_pct = 0.0
        else:
            game.game_stats.win_pct = wins / (wins + losses)

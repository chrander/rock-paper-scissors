from typing import Union

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from rps.constants import DATABASE_URI, Player, RoundOutcome
from rps.database.models import Base, Game, Round



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
        self.session.add(game)
        self.session.commit()

    def select_game(self, game_id: int) -> Game:
        statement = select(Game).where(Game.game_id == game_id)
        result = self.session.scalars(statement).one()
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
        self.session.commit()



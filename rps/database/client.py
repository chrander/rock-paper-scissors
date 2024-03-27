from typing import Union

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from rps.constants import DATABASE_PATH
from rps.database.models import Base, Game, Round



class DatabaseClient:

    def __init__(self, database_uri: str = DATABASE_PATH) -> None:
        self.database_uri = database_uri
        self.engine = create_engine(self.database_uri)

    def drop_tables(self) -> None:
        pass
    
    def create_tables(self) -> None:
        Base.metadata.create_all(self.engine)

    def insert_game(self, game: Game) -> None:
        with Session(self.engine) as session:
            session.add(game)
            session.commit()
    
    def select_all_games(self) -> list:
        with Session(self.engine) as session:
            statement = select(Game)
            results = session.scalars(statement).all()
        return results
        
    def select_all_rounds(self) -> list:
        with Session(self.engine) as session:
            statement = select(Round)
            results = session.scalars(statement).all()
        return results

    def add_round_by_game_id(self, round: Round, game_id: int) -> None:
        with Session(self.engine) as session:
            statement = select(Game).where(Game.game_id == game_id)
            game = session.scalars(statement).one()
            game.rounds.append(round)
            session.commit()

    def add_round_to_game(self, game: Game, round: Round) -> None:
        with Session(self.engine) as session:
            game.rounds.append(round)
            session.commit()

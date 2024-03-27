from datetime import datetime
from typing import List

from sqlalchemy import DateTime, String, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship


class Base(DeclarativeBase):
    pass


class Game(Base):
    __tablename__ = "games"

    game_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    player1_name: Mapped[str] = mapped_column(String)
    player1_type: Mapped[str] = mapped_column(String)
    player1_strategy: Mapped[str] = mapped_column(String)
    player2_name: Mapped[str] = mapped_column(String)
    player2_type: Mapped[str] = mapped_column(String)
    player2_strategy: Mapped[str] = mapped_column(String)

    rounds: Mapped[List["Round"]] = relationship(back_populates="game")

    def __repr__(self) -> str:
        return f"Game(id={self.game_id!r}, player1_name={self.player1_name!r}, player2_name={self.player2_name!r})"


# class RPSRound:
#     round_id: int
#     round_timestamp: datetime
#     game_id: int
#     player1_choice: str
#     player2_choice: str
#     outcome: str

class Round(Base):
    __tablename__ = "rounds"

    round_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    player1_choice: Mapped[str] = mapped_column(String)
    player2_choice: Mapped[str] = mapped_column(String)
    outcome: Mapped[str] = mapped_column(String)
    game_id = mapped_column(ForeignKey("games.game_id"))

    game: Mapped[Game] = relationship(back_populates="rounds")
    
    def __repr__(self) -> str:
        return f"Round(id={self.round_id!r}, game_id={self.game_id}, " \
               f"p1_choice={self.player1_choice!r}, p2_choice={self.player2_choice!r})"

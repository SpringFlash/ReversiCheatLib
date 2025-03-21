"""Библиотека, реализующая игру Реверси (Отелло).

Этот пакет содержит классы и функции для игры в Реверси.
"""

from src.core.board import Board
from src.core.heuristics import ReversiHeuristics
from src.core.reversi_logic import ReversiLogic

__all__ = ['Board', 'ReversiHeuristics', 'ReversiLogic']

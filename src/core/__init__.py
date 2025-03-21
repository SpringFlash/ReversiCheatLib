"""Основной пакет с игровой логикой Реверси.

Содержит модули для управления игровым процессом.
"""

from src.core.board import Board
from src.core.heuristics import ReversiHeuristics
from src.core.reversi_logic import ReversiLogic

__all__ = ['Board', 'ReversiHeuristics', 'ReversiLogic']

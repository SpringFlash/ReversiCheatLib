"""Пакет с алгоритмами для игры в Реверси.

Содержит различные алгоритмы для выбора оптимального хода в игре.
"""

from src.algorithms.minimax import MinimaxAlgorithm
from src.algorithms.mcts import MCTSAlgorithm
from src.algorithms.negascout import NegaScoutAlgorithm

__all__ = ['MinimaxAlgorithm', 'MCTSAlgorithm', 'NegaScoutAlgorithm']

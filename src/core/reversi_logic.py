"""
Логика игры Реверси - основной модуль для управления ходом игры и выбора алгоритмов.
"""
from src.core.board import Board
from src.core.heuristics import ReversiHeuristics
from src.algorithms.minimax import MinimaxAlgorithm
from src.algorithms.mcts import MCTSAlgorithm
from src.algorithms.negascout import NegaScoutAlgorithm
import os
import datetime
import json
import time

class ReversiLogic:
    """
    Класс для управления логикой игры Реверси с возможностью выбора алгоритма
    в зависимости от фазы игры.
    """
    def __init__(self):
        # Инициализация доски 8x8
        self.board = Board()
        
        # Инициализация алгоритмов
        self.minimax = MinimaxAlgorithm()
        self.mcts = MCTSAlgorithm()
        self.negascout = NegaScoutAlgorithm()
        self.heuristics = ReversiHeuristics()
        
        # Инициализация оптимальных ходов
        self.optimal_sequence = {}
        
        # Инициализация структур для логирования
        self.game_log = []
        self.log_file = None
        self.moves_count = 0
        self.algorithm_stats = {
            "mcts": {"used": 0, "time": 0, "avg_score": 0},
            "negascout": {"used": 0, "time": 0, "avg_score": 0},
            "minimax": {"used": 0, "time": 0, "avg_score": 0}
        }
        
        # Последовательность ходов оптимальной игры
        self.optimal_game_sequence = "F5D6C3D3C4F4F6F3E6E7D7C5B6D8C6C7D2B5A5A6A7G5E3B4C8G6G4C2E8D1F7E2G3H4F1E1F2G1B1F8G8B3H3B2H5B7A3A4A1A2C1H2H1G2B8A8G7H8H7H6"
        
        # Преобразуем последовательность в индексы от 0 до 7
        self.optimal_moves = []
        for i in range(0, len(self.optimal_game_sequence), 2):
            if i+1 < len(self.optimal_game_sequence):
                col = ord(self.optimal_game_sequence[i]) - ord('A')
                row = int(self.optimal_game_sequence[i+1]) - 1
                self.optimal_moves.append((row, col))
        
        # Создаем директорию для логов, если она не существует
        if not os.path.exists("logs"):
            os.makedirs("logs")
            
        # Создаем имя файла лога на основе текущего времени
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = f"logs/game_{timestamp}.json"
    
    def reset_game(self):
        """
        Сбрасывает игру к начальному состоянию
        """
        self.board = Board()
        
        # Инициализация структур для логирования новой игры
        self.game_log = []
        # Создаем имя файла лога на основе текущего времени
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = f"logs/game_{timestamp}.json"
        self.moves_count = 0
        
        # Сбрасываем статистику алгоритмов
        self.algorithm_stats = {
            "mcts": {"used": 0, "time": 0, "avg_score": 0},
            "negascout": {"used": 0, "time": 0, "avg_score": 0},
            "minimax": {"used": 0, "time": 0, "avg_score": 0}
        }
        
        # Создаем директорию для логов, если она не существует
        if not os.path.exists("logs"):
            os.makedirs("logs")
    
    def get_board(self):
        """
        Возвращает текущее состояние доски
        
        Returns:
            list: текущее состояние доски
        """
        return self.board.get_board()
    
    def is_valid_move(self, row, col, player):
        """
        Проверяет, является ли ход допустимым
        
        Args:
            row (int): строка
            col (int): столбец
            player (str): цвет игрока ('black' или 'white')
            
        Returns:
            bool: True если ход допустим, иначе False
        """
        return self.board.is_valid_move(row, col, player)
    
    def make_move(self, row, col, player):
        """
        Выполняет ход
        
        Args:
            row (int): строка
            col (int): столбец
            player (str): цвет игрока ('black' или 'white')
            
        Returns:
            bool: True если ход был выполнен успешно, иначе False
        """
        if self.is_valid_move(row, col, player):
            self.board.make_move(row, col, player)
            self.moves_count += 1
            return True
        return False
    
    def get_valid_moves(self, player, board_state=None):
        """
        Находит все допустимые ходы для игрока
        
        Args:
            player (str): цвет игрока ('black' или 'white')
            board_state (list, optional): опциональное состояние доски для анализа. 
                                         Если не указано, используется текущее состояние.
            
        Returns:
            list: список координат допустимых ходов [(row, col), ...]
        """
        valid_moves = []
        
        # Если передано состояние доски, создаем временную доску
        if board_state is not None:
            temp_board = Board()
            temp_board.set_board(board_state)
            board = temp_board
        else:
            board = self.board
        
        for row in range(board.size):
            for col in range(board.size):
                if board.is_valid_move(row, col, player):
                    valid_moves.append((row, col))
        
        # Отладочная информация
        if valid_moves and board_state is None:  # Выводим только для текущей доски
            moves_str = ", ".join([f"{chr(65 + col)}{row + 1}" for row, col in valid_moves])
            print(f"Найдено {len(valid_moves)} доступных ходов для {player}: {moves_str}")
        elif board_state is None:  # Выводим только для текущей доски
            print(f"Не найдено доступных ходов для {player}")
                    
        return valid_moves
    
    def count_pieces(self, player=None):
        """
        Подсчитывает количество фишек каждого цвета на доске
        
        Args:
            player (str, optional): цвет игрока ('black' или 'white'). 
                                    Если указан, возвращает только количество фишек этого цвета.
        
        Returns:
            dict или int: словарь с количеством фишек {'black': int, 'white': int, 'empty': int}
                          или количество фишек указанного цвета
        """
        pieces = self.board.count_pieces()
        
        if player is not None:
            if player in pieces:
                return pieces[player]
            else:
                return 0
                
        return pieces
    
    def is_game_over(self):
        """
        Проверяет, завершена ли игра
        
        Returns:
            bool: True если игра завершена (никто не может сделать ход), иначе False
        """
        return self.board.is_game_over()
    
    def get_winner(self):
        """
        Определяет победителя, если игра завершена
        
        Returns:
            str: 'black', 'white' или 'tie', или None если игра не окончена
        """
        return self.board.get_winner()
    
    def get_best_move(self, player, max_depth=None, game_phase=None):
        """
        Определяет лучший ход с использованием подходящего алгоритма
        в зависимости от фазы игры
        
        Args:
            player: цвет игрока ('black' или 'white')
            max_depth: максимальная глубина поиска (необязательно)
            game_phase: фаза игры ("early", "middle", "late") (необязательно)
            
        Returns:
            tuple: координаты хода (row, col) и оценка
        """
        # Определяем текущую фазу игры, если она не указана
        empty_count = sum(row.count("empty") for row in self.get_board())
        
        if game_phase is None:
            if empty_count > 45:
                game_phase = "early"
            elif empty_count > 15:
                game_phase = "middle"
            else:
                game_phase = "late"
        
        # Выбираем алгоритм в зависимости от фазы игры
        algorithm = None
        algorithm_name = ""
        
        # Измеряем время для анализа производительности
        start_time = time.time()
        
        # Проверяем, можно ли сделать оптимальный ход
        optimal_move = self.get_optimal_move(player)
        if optimal_move:
            row, col = optimal_move
            return (row, col), 1000.0
            
        # Проверяем наличие угловых ходов - они всегда приоритетны
        corner_moves = self.get_corner_moves(player)
        if corner_moves:
            row, col = corner_moves[0]
            return (row, col), 1000.0
            
        # На ранней стадии игры, приоритет позиционной игре
        if empty_count > 48 or game_phase == "early":  # Очень раннее начало - простые эвристики
            valid_moves = self.get_valid_moves(player)
            if valid_moves:
                # Избегаем ходы, которые дают противнику доступ к углам
                safe_moves = []
                for move in valid_moves:
                    if not self.gives_corner_access(move[0], move[1], player):
                        safe_moves.append(move)
                
                if safe_moves:
                    # Выбираем ход, который дает наибольшее количество фишек
                    best_move = None
                    max_pieces = -1
                    
                    for move in safe_moves:
                        # Создаем копию доски для проверки хода
                        board_copy = Board()
                        board_copy.board = [row.copy() for row in self.board.board]
                        board_copy.make_move(move[0], move[1], player)
                        
                        # Подсчитываем количество фишек
                        count = 0
                        for row in board_copy.board:
                            count += row.count(player)
                        
                        if count > max_pieces:
                            max_pieces = count
                            best_move = move
                    
                    if best_move:
                        row, col = best_move
                        return (row, col), 0.95
        
        if game_phase == "early" or empty_count > 45:  # Ранняя игра - используем MCTS с увеличенной выборкой
            algorithm = self.mcts
            algorithm_name = "mcts"
            # Увеличиваем количество итераций для MCTS
            algorithm.iterations = 2000  # Увеличиваем для лучшего просчета
        elif game_phase == "middle" or empty_count > 15:  # Середина игры - используем NegaScout
            algorithm = self.negascout
            algorithm_name = "negascout"
            # Настраиваем глубину поиска в зависимости от количества пустых клеток
            if not max_depth:
                if empty_count < 25:
                    max_depth = 6
                else:
                    max_depth = 5
        else:  # Конец игры - используем Minimax
            algorithm = self.minimax
            algorithm_name = "minimax"
            # В конце игры можем позволить себе большую глубину
            if not max_depth:
                if empty_count < 10:
                    max_depth = 9  # Почти точный расчет концовки
                else:
                    max_depth = 7
        
        # Получаем лучший ход
        move_data = algorithm.get_best_move(self.board, player, max_depth)
        
        # Если ход все еще не найден, выбираем любой допустимый
        if not move_data or not "row" in move_data:
            valid_moves = self.get_valid_moves(player)
            if valid_moves:
                row, col = valid_moves[0]
                print(f"Запасной вариант: выбран первый доступный ход ({row},{col}) из {len(valid_moves)} ходов")
                move_data = {"row": row, "col": col, "score": 0.5}
        
        # Рассчитываем время выполнения
        elapsed_time = time.time() - start_time
        
        # Обновляем статистику использования алгоритма
        self.algorithm_stats[algorithm_name]["used"] += 1
        self.algorithm_stats[algorithm_name]["time"] += elapsed_time
        
        # Обновляем среднюю оценку
        if move_data and "score" in move_data:
            current_avg = self.algorithm_stats[algorithm_name]["avg_score"]
            used_count = self.algorithm_stats[algorithm_name]["used"]
            if used_count > 0:
                new_avg = ((current_avg * (used_count - 1)) + move_data["score"]) / used_count
                self.algorithm_stats[algorithm_name]["avg_score"] = new_avg
        
        # Преобразуем возвращаемое значение из dict в tuple для совместимости
        if move_data and "row" in move_data and "col" in move_data:
            return (move_data["row"], move_data["col"]), move_data.get("score", 0.0)
        
        # Последняя попытка: проверяем еще раз наличие валидных ходов
        valid_moves = self.get_valid_moves(player)
        if valid_moves:
            row, col = valid_moves[0]
            print(f"Крайний случай: выбран первый доступный ход ({row},{col}) из {len(valid_moves)} ходов")
            return (row, col), 0.1
        
        return None, 0.0
    
    def get_optimal_move(self, player):
        """
        Проверяет, можно ли сделать ход из оптимальной последовательности
        
        Args:
            player (str): цвет игрока ('black' или 'white')
            
        Returns:
            tuple: координаты хода из оптимальной последовательности или None
        """
        # Подсчитываем количество фишек на доске
        pieces = self.count_pieces()
        total_pieces = pieces["black"] + pieces["white"]
        
        # Проверяем только в начале игры
        if total_pieces < 10 and total_pieces // 2 < len(self.optimal_moves):
            next_move = self.optimal_moves[total_pieces // 2]
            row, col = next_move
            
            # Проверяем, возможен ли этот ход
            if self.is_valid_move(row, col, player):
                return next_move
        
        return None
    
    def evaluate_board(self, player):
        """
        Оценивает текущее состояние доски для игрока
        
        Args:
            player: цвет игрока ('black' или 'white')
            
        Returns:
            float: оценка позиции
        """
        # Определяем текущую фазу игры
        board_state = self.get_board()
        empty_count = sum(row.count("empty") for row in board_state)
        
        game_phase = "early"
        if empty_count <= 15:
            game_phase = "late"
        elif empty_count <= 45:
            game_phase = "middle"
        
        return self.minimax.heuristics.evaluate_position(board_state, player, game_phase)
    
    def log_move(self, player, move, opponent_move=None, algorithm=None, is_our_move=None):
        """
        Записывает информацию о ходе в лог
        
        Args:
            player: цвет игрока ('black' или 'white')
            move: координаты хода (row, col)
            opponent_move: координаты хода противника (row, col) или None
            algorithm: название использованного алгоритма или None
            is_our_move: флаг, указывающий наш ход или нет (необязательно)
        """
        # Если не указан алгоритм, определяем его по фазе игры
        if algorithm is None:
            empty_count = sum(row.count("empty") for row in self.get_board())
            if empty_count > 45:
                algorithm = "mcts"
            elif empty_count > 15:
                algorithm = "negascout"
            else:
                algorithm = "minimax"
        
        # Получаем текущее состояние доски
        board_state = self.get_board()
        
        # Переводим координаты в шахматную нотацию
        chess_notation = None
        if move:
            # Проверяем тип move - это может быть кортеж или словарь
            if isinstance(move, tuple) and len(move) == 2:
                row, col = move
                col_letter = chr(ord('A') + col)
                chess_notation = f"{col_letter}{row + 1}"
            elif isinstance(move, dict) and 'row' in move and 'col' in move:
                row, col = move['row'], move['col']
                col_letter = chr(ord('A') + col)
                chess_notation = f"{col_letter}{row + 1}"
        
        opponent_notation = None
        if opponent_move:
            if isinstance(opponent_move, tuple) and len(opponent_move) == 2:
                opp_row, opp_col = opponent_move
                opp_col_letter = chr(ord('A') + opp_col)
                opponent_notation = f"{opp_col_letter}{opp_row + 1}"
            elif isinstance(opponent_move, dict) and 'row' in opponent_move and 'col' in opponent_move:
                opp_row, opp_col = opponent_move['row'], opponent_move['col']
                opp_col_letter = chr(ord('A') + opp_col)
                opponent_notation = f"{opp_col_letter}{opp_row + 1}"
        
        # Определяем фазу игры
        empty_count = sum(row.count("empty") for row in board_state)
        game_phase = "early"
        if empty_count <= 15:
            game_phase = "late"
        elif empty_count <= 45:
            game_phase = "middle"
            
        # Подсчитываем количество фишек
        pieces = self.count_pieces()
        
        # Оцениваем позицию
        score = self.evaluate_board(player)
        
        # Создаем запись для лога
        log_entry = {
            "move_number": self.moves_count,
            "board": board_state,
            "pieces": pieces,
            "game_phase": game_phase,
            "player": player,
            "move": chess_notation,
            "opponent_move": opponent_notation,
            "score": score,
            "timestamp": datetime.datetime.now().isoformat(),
            "algorithm": algorithm,
            "algorithm_stats": self.algorithm_stats
        }
        
        # Добавляем информацию о том, чей ход
        if is_our_move is not None:
            log_entry["is_our_move"] = is_our_move
        
        # Добавляем запись в лог
        self.game_log.append(log_entry)
        
        # Записываем в файл
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(self.game_log, f, indent=2)
    
    def get_corner_moves(self, player):
        """
        Проверяет, можно ли занять угловые клетки
        
        Args:
            player (str): цвет игрока ('black' или 'white')
            
        Returns:
            list: список доступных угловых ходов
        """
        corners = [(0, 0), (0, 7), (7, 0), (7, 7)]
        valid_corner_moves = []
        
        for row, col in corners:
            if self.is_valid_move(row, col, player):
                valid_corner_moves.append((row, col))
        
        return valid_corner_moves
    
    def gives_corner_access(self, row, col, player):
        """
        Проверяет, дает ли ход доступ противнику к углу
        
        Args:
            row (int): строка
            col (int): столбец
            player (str): цвет игрока ('black' или 'white')
            
        Returns:
            bool: True если ход опасный, иначе False
        """
        # Клетки рядом с углами - обычно дают доступ к углам
        dangerous_cells = [
            (0, 1), (1, 0), (1, 1),  # Рядом с углом (0,0)
            (0, 6), (1, 6), (1, 7),  # Рядом с углом (0,7)
            (6, 0), (6, 1), (7, 1),  # Рядом с углом (7,0)
            (6, 6), (6, 7), (7, 6)   # Рядом с углом (7,7)
        ]
        
        if (row, col) in dangerous_cells:
            # Проверяем, есть ли соответствующий угол пуст
            if (row, col) in [(0, 1), (1, 0), (1, 1)] and self.board.board[0][0] == "empty":
                return True
            elif (row, col) in [(0, 6), (1, 6), (1, 7)] and self.board.board[0][7] == "empty":
                return True
            elif (row, col) in [(6, 0), (6, 1), (7, 1)] and self.board.board[7][0] == "empty":
                return True
            elif (row, col) in [(6, 6), (6, 7), (7, 6)] and self.board.board[7][7] == "empty":
                return True
        
        return False
    
    def determine_game_phase(self, empty_count=None):
        """
        Определяет текущую фазу игры на основе количества пустых клеток
        
        Args:
            empty_count (int): количество пустых клеток (необязательно)
            
        Returns:
            str: фаза игры ("early", "middle", "late")
        """
        if empty_count is None:
            empty_count = sum(row.count("empty") for row in self.get_board())
            
        if empty_count > 45:
            return "early"
        elif empty_count > 15:
            return "middle"
        else:
            return "late"
    
    def get_opponent_move(self, player, strength="medium"):
        """
        Имитирует ход противника разной силы
        
        Args:
            player (str): Цвет фишек противника ('black' или 'white')
            strength (str): Уровень противника ('weak', 'medium', 'strong')
            
        Returns:
            tuple: Ход в формате (row, col)
        """
        valid_moves = self.get_valid_moves(player)
        
        if not valid_moves:
            return None
            
        if strength == "weak":
            # Слабый противник выбирает случайный ход, избегая углов
            import random
            corners = [(0, 0), (0, 7), (7, 0), (7, 7)]
            non_corner_moves = [move for move in valid_moves if move not in corners]
            
            if non_corner_moves:
                return random.choice(non_corner_moves)
            else:
                return random.choice(valid_moves)
                
        elif strength == "strong":
            # Сильный противник выбирает оптимальный ход
            # Используем NegaScout с меньшей глубиной для скорости
            empty_count = sum(row.count("empty") for row in self.board.board)
            game_phase = self.determine_game_phase(empty_count)
            
            move, score = self.get_best_move(player, max_depth=4, game_phase=game_phase)
            return move
            
        else:  # medium
            # Средний противник баланс между случайным и оптимальным
            import random
            
            # 70% случаев делаем разумный ход
            if random.random() < 0.7:
                # Предпочитаем края и углы
                scored_moves = []
                for move in valid_moves:
                    score = 0
                    
                    # Углы - высокий приоритет
                    if move in [(0, 0), (0, 7), (7, 0), (7, 7)]:
                        score += 10
                        
                    # Края - средний приоритет
                    elif move[0] in [0, 7] or move[1] in [0, 7]:
                        score += 5
                        
                    # Клетки рядом с углами - низкий приоритет (если угол пуст)
                    elif move in [(0, 1), (1, 0), (1, 1)] and self.board.board[0][0] == "empty":
                        score -= 5
                    elif move in [(0, 6), (1, 6), (1, 7)] and self.board.board[0][7] == "empty":
                        score -= 5
                    elif move in [(6, 0), (6, 1), (7, 1)] and self.board.board[7][0] == "empty":
                        score -= 5
                    elif move in [(6, 6), (6, 7), (7, 6)] and self.board.board[7][7] == "empty":
                        score -= 5
                        
                    # Учитываем количество переворачиваемых фишек
                    board_copy = Board()
                    board_copy.board = [row.copy() for row in self.board.board]
                    board_copy.make_move(move[0], move[1], player)
                    
                    # Подсчитываем, сколько фишек перевернули
                    flipped = 0
                    for r in range(8):
                        for c in range(8):
                            if board_copy.board[r][c] == player and self.board.board[r][c] != player:
                                flipped += 1
                    
                    score += flipped * 0.1
                    
                    scored_moves.append((move, score))
                    
                # Сортируем ходы по оценке
                scored_moves.sort(key=lambda x: x[1], reverse=True)
                
                # Выбираем один из 3 лучших ходов
                top_moves = [move for move, _ in scored_moves[:3]]
                return random.choice(top_moves if top_moves else valid_moves)
            else:
                # 30% случаев делаем случайный ход
                return random.choice(valid_moves)
    
    def reset_statistics(self):
        """
        Сбрасывает всю накопленную статистику по алгоритмам
        """
        # Сбрасываем статистику для MCTS
        self.mcts_used = 0
        self.mcts_time = 0
        self.mcts_scores = []
        
        # Сбрасываем статистику для NegaScout
        self.negascout_used = 0
        self.negascout_time = 0
        self.negascout_scores = []
        
        # Сбрасываем статистику для Minimax
        self.minimax_used = 0
        self.minimax_time = 0
        self.minimax_scores = []
    
    def make_move_internal(self, board, move, player):
        """
        Делает ход на копии доски без изменения исходной доски
        
        Args:
            board (list): Текущее состояние доски
            move (tuple): Ход в формате (row, col)
            player (str): Цвет фишек игрока ('black' или 'white')
            
        Returns:
            tuple: (новая доска, количество перевернутых фишек)
        """
        if move is None:
            return board, 0
            
        row, col = move
        opponent = "white" if player == "black" else "black"
        directions = [(0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1)]
        
        # Создаем копию доски
        new_board = [row[:] for row in board]
        new_board[row][col] = player
        
        pieces_flipped = 0
        
        for dr, dc in directions:
            r, c = row + dr, col + dc
            to_flip = []
            
            while 0 <= r < 8 and 0 <= c < 8 and new_board[r][c] == opponent:
                to_flip.append((r, c))
                r += dr
                c += dc
            
            if 0 <= r < 8 and 0 <= c < 8 and new_board[r][c] == player and to_flip:
                for flip_r, flip_c in to_flip:
                    new_board[flip_r][flip_c] = player
                    pieces_flipped += 1
        
        return new_board, pieces_flipped
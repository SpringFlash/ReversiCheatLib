"""
Модуль для реализации алгоритма Minimax с отсечением альфа-бета
"""
import time
from src.core.heuristics import ReversiHeuristics

class MinimaxAlgorithm:
    """
    Класс для реализации алгоритма Minimax с отсечением альфа-бета
    для игры Реверси.
    """
    def __init__(self):
        self.heuristics = ReversiHeuristics()
        self.transposition_table = {}  # Кэш для уже вычисленных позиций
        self.max_time = 0.5  # Максимальное время на ход в секундах
        self.start_time = 0
        self.nodes_visited = 0
        self.tt_hits = 0
        
    def get_best_move(self, board, player, max_depth=None):
        """
        Находит лучший ход с использованием алгоритма Minimax
        
        Args:
            board: объект класса Board с текущим состоянием доски
            player: цвет игрока ('black' или 'white')
            max_depth: максимальная глубина поиска
            
        Returns:
            dict: словарь с координатами хода и оценкой, или None если ходов нет
        """
        # Сбрасываем счетчики для аналитики
        self.nodes_visited = 0
        self.tt_hits = 0
        self.start_time = time.time()
        
        # Получаем текущее состояние доски
        board_state = board.get_board()
        
        # Определяем фазу игры для выбора глубины поиска и оценочной функции
        game_phase = self.heuristics.determine_game_phase(board_state)
        
        # Выбираем глубину поиска в зависимости от фазы игры, если не задана
        if max_depth is None:
            empty_count = sum(row.count("empty") for row in board_state)
            if empty_count <= 10:  # Эндшпиль
                max_depth = 9  # Увеличиваем глубину для эндшпиля
            elif empty_count <= 15:  # Поздняя середина
                max_depth = 7  # Увеличиваем глубину для поздней середины
            else:  # Раннее и середина
                max_depth = 5  # Увеличиваем стандартную глубину
        
        # Получаем все допустимые ходы
        valid_moves = board.get_valid_moves(player)
        
        if not valid_moves:
            return None
            
        # Если есть только один ход, возвращаем его
        if len(valid_moves) == 1:
            move = valid_moves[0]
            return {"row": move[0], "col": move[1], "score": 0}
            
        # Сортируем ходы для оптимизации отсечения альфа-бета
        corners = [(0, 0), (0, 7), (7, 0), (7, 7)]
        edges = [(0, i) for i in range(1, 7)] + [(7, i) for i in range(1, 7)] + \
                [(i, 0) for i in range(1, 7)] + [(i, 7) for i in range(1, 7)]
        
        # Сначала проверяем углы и края
        sorted_moves = []
        for move in valid_moves:
            if move in corners:
                sorted_moves.insert(0, move)  # Углы в начало списка
            elif move in edges:
                if len(sorted_moves) > 0 and sorted_moves[0] in corners:
                    sorted_moves.insert(1, move)  # После углов
                else:
                    sorted_moves.insert(0, move)  # В начало, если нет углов
            else:
                sorted_moves.append(move)  # Остальные ходы в конец
                
        # Если у нас есть ход в угол, сразу берем его (эвристика)
        for move in valid_moves:
            if move in corners:
                return {"row": move[0], "col": move[1], "score": 1000}
        
        # Используем итеративное углубление - начинаем с меньшей глубины и постепенно увеличиваем
        best_move = None
        best_score = float('-inf')
        max_search_depth = min(max_depth, 3)  # Начинаем с небольшой глубины
        
        while max_search_depth <= max_depth and time.time() - self.start_time < self.max_time:
            # Инициализация для алгоритма Minimax
            alpha = float('-inf')
            beta = float('inf')
            current_best_move = None
            current_best_score = float('-inf')
            
            # Перебираем все возможные ходы
            for move in sorted_moves:
                # Проверяем, не истекло ли время
                if time.time() - self.start_time >= self.max_time:
                    break
                    
                row, col = move
                board_copy = board.clone()
                board_copy.make_move(row, col, player)
                opponent = "white" if player == "black" else "black"
                
                # Адаптивная глубина поиска - на угловых ходах идем глубже
                adaptive_depth = max_search_depth
                if move in corners:
                    adaptive_depth += 1  # Углы исследуем глубже
                
                # Получаем оценку хода с помощью рекурсивного вызова Minimax
                score = -self.alpha_beta(board_copy, adaptive_depth - 1, -beta, -alpha, opponent, game_phase)
                
                if score > current_best_score:
                    current_best_score = score
                    current_best_move = {"row": row, "col": col, "score": score}
                    alpha = max(alpha, score)
            
            # Обновляем лучший ход, если нашли лучший на этой глубине
            if current_best_move is not None and (best_move is None or current_best_score > best_score):
                best_move = current_best_move
                best_score = current_best_score
            
            # Увеличиваем глубину для следующей итерации
            max_search_depth += 1
            
            # Если достигли максимальной глубины или кончилось время, прекращаем поиск
            if max_search_depth > max_depth or time.time() - self.start_time >= self.max_time:
                break
        
        # Добавляем аналитику
        elapsed = time.time() - self.start_time
        # print(f"Minimax: глубина={max_search_depth-1}, узлы={self.nodes_visited}, time={elapsed:.3f}s, TT hits={self.tt_hits}")
        
        return best_move
    
    def alpha_beta(self, board, depth, alpha, beta, player, game_phase):
        """
        Рекурсивная функция алгоритма Minimax с отсечением альфа-бета
        
        Args:
            board: объект класса Board с текущим состоянием доски
            depth: текущая глубина поиска
            alpha: альфа-граница
            beta: бета-граница
            player: текущий игрок ('black' или 'white')
            game_phase: фаза игры ('early', 'middle', 'late')
            
        Returns:
            float: оценка позиции
        """
        self.nodes_visited += 1
        
        # Проверяем, не истекло ли время
        if time.time() - self.start_time >= self.max_time:
            # Если время истекло, возвращаем приблизительную оценку
            board_state = board.get_board()
            return self.heuristics.evaluate_position(board_state, player, game_phase)
            
        board_state = board.get_board()
        board_hash = self._board_to_hash(board_state)
        
        # Проверяем транспозиционную таблицу - хешируем с учетом игрока и глубины
        tt_key = f"{board_hash}:{player}:{depth}"
        if tt_key in self.transposition_table and self.transposition_table[tt_key]["depth"] >= depth:
            # Проверяем тип записи в таблице
            tt_entry = self.transposition_table[tt_key]
            self.tt_hits += 1
            
            if tt_entry["type"] == "exact":
                return tt_entry["score"]
            elif tt_entry["type"] == "lower_bound" and tt_entry["score"] > alpha:
                alpha = tt_entry["score"]
            elif tt_entry["type"] == "upper_bound" and tt_entry["score"] < beta:
                beta = tt_entry["score"]
            
            if alpha >= beta:
                return tt_entry["score"]
        
        # Если достигли максимальной глубины или игра окончена, возвращаем оценку позиции
        if depth == 0 or board.is_game_over():
            score = self.heuristics.evaluate_position(board_state, player, game_phase)
            # Для конечных позиций храним точную оценку
            self.transposition_table[tt_key] = {"score": score, "depth": depth, "type": "exact"}
            return score
        
        # Получаем возможные ходы
        valid_moves = board.get_valid_moves(player)
        
        # Если нет возможных ходов, пропускаем ход
        if not valid_moves:
            opponent = "white" if player == "black" else "black"
            opponent_moves = board.get_valid_moves(opponent)
            
            # Если и у противника нет ходов, игра окончена
            if not opponent_moves:
                score = self.heuristics.evaluate_position(board_state, player, game_phase)
                self.transposition_table[tt_key] = {"score": score, "depth": depth, "type": "exact"}
                return score
            
            # Пропускаем ход и даем слово противнику
            return -self.alpha_beta(board, depth - 1, -beta, -alpha, opponent, game_phase)
        
        # Сортируем ходы для улучшения эффективности отсечения
        # В первую очередь рассматриваем углы и края
        corners = [(0, 0), (0, 7), (7, 0), (7, 7)]
        edges = [(0, i) for i in range(1, 7)] + [(7, i) for i in range(1, 7)] + \
                [(i, 0) for i in range(1, 7)] + [(i, 7) for i in range(1, 7)]
                
        # Сортируем ходы
        sorted_moves = []
        for move in valid_moves:
            if move in corners:
                sorted_moves.insert(0, move)
            elif move in edges:
                if len(sorted_moves) > 0 and sorted_moves[0] in corners:
                    sorted_moves.insert(1, move)
                else:
                    sorted_moves.insert(0, move)
            else:
                sorted_moves.append(move)
        
        best_score = float('-inf')
        entry_type = "upper_bound"  # По умолчанию - верхняя граница
        
        # Перебираем все возможные ходы
        for move in sorted_moves:
            # Проверяем, не истекло ли время
            if time.time() - self.start_time >= self.max_time:
                break
                
            row, col = move
            board_copy = board.clone()
            board_copy.make_move(row, col, player)
            opponent = "white" if player == "black" else "black"
            
            # Адаптивная глубина поиска - на угловых ходах идем глубже
            adaptive_depth = depth
            if move in corners:
                adaptive_depth += 1  # Углы исследуем глубже
            
            # Получаем оценку хода с помощью рекурсивного вызова
            score = -self.alpha_beta(board_copy, adaptive_depth - 1, -beta, -alpha, opponent, game_phase)
            
            if score > best_score:
                best_score = score
                entry_type = "exact"  # Точная оценка
                
            alpha = max(alpha, best_score)
            
            # Альфа-бета отсечение
            if alpha >= beta:
                # Сохраняем нижнюю границу
                self.transposition_table[tt_key] = {"score": best_score, "depth": depth, "type": "lower_bound"}
                return best_score
        
        # Сохраняем результат в транспозиционной таблице
        self.transposition_table[tt_key] = {"score": best_score, "depth": depth, "type": entry_type}
        
        return best_score
    
    def _board_to_hash(self, board):
        """
        Преобразует доску в хеш для использования в транспозиционной таблице
        
        Args:
            board: состояние доски
            
        Returns:
            str: хеш-строка доски
        """
        board_str = ""
        for row in board:
            for cell in row:
                if cell == "black":
                    board_str += "b"
                elif cell == "white":
                    board_str += "w"
                else:
                    board_str += "e"
        return board_str 
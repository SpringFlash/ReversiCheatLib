"""
Модуль с различными оценочными функциями и эвристиками для игры Реверси
"""

import math

class ReversiHeuristics:
    """
    Класс с различными эвристиками для оценки позиции в Реверси
    """
    def __init__(self):
        """
        Инициализирует объект с положительными весами для оценки позиций на доске
        """
        # Веса для оценки положения фишек
        self.position_weights = [
            [120, -20, 20, 5, 5, 20, -20, 120],  # Увеличены веса углов
            [-20, -40, -5, -5, -5, -5, -40, -20],
            [20, -5, 15, 3, 3, 15, -5, 20],
            [5, -5, 3, 3, 3, 3, -5, 5],
            [5, -5, 3, 3, 3, 3, -5, 5],
            [20, -5, 15, 3, 3, 15, -5, 20],
            [-20, -40, -5, -5, -5, -5, -40, -20],
            [120, -20, 20, 5, 5, 20, -20, 120]
        ]
        
        # Определяем угловые позиции для быстрого доступа
        self.corners = [(0, 0), (0, 7), (7, 0), (7, 7)]
        
        # Опасные клетки рядом с углами
        self.dangerous_cells = [
            (0, 1), (1, 0), (1, 1),  # Рядом с углом (0,0)
            (0, 6), (1, 6), (1, 7),  # Рядом с углом (0,7)
            (6, 0), (6, 1), (7, 1),  # Рядом с углом (7,0)
            (6, 6), (6, 7), (7, 6)   # Рядом с углом (7,7)
        ]
        
        # Клетки X (диагонально примыкающие к углам)
        self.x_squares = [(1, 1), (1, 6), (6, 1), (6, 6)]
        
        # Клетки C (примыкающие к углам по горизонтали/вертикали)
        self.c_squares = [(0, 1), (1, 0), (0, 6), (1, 7), 
                           (6, 0), (7, 1), (6, 7), (7, 6)]
        
        # Направления для проверки стабильности
        self.directions = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1),  (1, 0),  (1, 1),
        ]
    
    def evaluate_position(self, board, player, game_phase="middle"):
        """
        Оценка позиции для игрока, учитывая текущую стадию игры
        
        Args:
            board (list): текущее состояние доски
            player (str): игрок ('black' или 'white')
            game_phase (str): фаза игры ('early', 'middle', 'late')
            
        Returns:
            float: оценка позиции в диапазоне [-1, 1]
        """
        opponent = 'white' if player == 'black' else 'black'
        
        # Веса для разных компонент оценки в зависимости от фазы игры
        if game_phase == "early":
            weights = {
                'pieces': 0.05,     # Меньше внимания количеству фишек в начале
                'position': 0.35,   # Больше внимания позиции в начале
                'mobility': 0.25,   # Больше внимания доступным ходам
                'stability': 0.05,  # Меньше стабильных фишек в начале
                'corners': 0.20,    # Много внимания углам
                'edges': 0.05,      # Немного внимания краям
                'patterns': 0.05,   # Немного внимания паттернам
                'parity': 0.0       # Паритет не важен в начале
            }
        elif game_phase == "middle":
            weights = {
                'pieces': 0.1,
                'position': 0.3,
                'mobility': 0.15,
                'stability': 0.1,
                'corners': 0.25,
                'edges': 0.05,
                'patterns': 0.05,
                'parity': 0.0
            }
        else:  # late
            weights = {
                'pieces': 0.3,      # В конце важно количество фишек
                'position': 0.1,    # Позиция менее важна
                'mobility': 0.05,   # Мобильность менее важна
                'stability': 0.2,   # Стабильность очень важна
                'corners': 0.2,     # Углы по-прежнему важны
                'edges': 0.1,       # Края более важны
                'patterns': 0.0,    # Паттерны не важны в конце
                'parity': 0.05      # Паритет важен в конце
            }
            
        # 1. Количество фишек
        player_pieces = 0
        opponent_pieces = 0
        for row in board:
            player_pieces += row.count(player)
            opponent_pieces += row.count(opponent)
        
        total_pieces = player_pieces + opponent_pieces
        if total_pieces > 0:
            piece_ratio = (player_pieces - opponent_pieces) / total_pieces
        else:
            piece_ratio = 0
        
        # 2. Позиционная оценка на основе весовой таблицы
        positional_score = 0
        max_position_score = 0
        
        for i in range(8):
            for j in range(8):
                if board[i][j] == player:
                    positional_score += self.position_weights[i][j]
                elif board[i][j] == opponent:
                    positional_score -= self.position_weights[i][j]
                
                max_position_score += abs(self.position_weights[i][j])
        
        # Нормализация позиционной оценки
        if max_position_score > 0:
            positional_score = positional_score / max_position_score
        
        # 3. Мобильность (доступные ходы)
        player_mobility = self.count_mobility(board, player)
        opponent_mobility = self.count_mobility(board, opponent)
        
        # Избегаем деление на ноль
        total_mobility = player_mobility + opponent_mobility
        if total_mobility > 0:
            mobility_score = (player_mobility - opponent_mobility) / total_mobility
        else:
            # Если нет доступных ходов, это плохо
            if player_mobility == 0 and opponent_mobility == 0:
                mobility_score = 0  # Ничья
            elif player_mobility == 0:
                mobility_score = -1  # Мы проиграли
            else:
                mobility_score = 1  # Мы выиграли
        
        # 4. Стабильные фишки (которые нельзя перевернуть)
        player_stable = self.count_stable_discs(board, player)
        opponent_stable = self.count_stable_discs(board, opponent)
        
        total_stable = player_stable + opponent_stable
        if total_stable > 0:
            stability_score = (player_stable - opponent_stable) / total_stable
        else:
            stability_score = 0
        
        # 5. Угловые клетки (особые весы для углов)
        player_corners = sum(1 for x, y in self.corners if board[x][y] == player)
        opponent_corners = sum(1 for x, y in self.corners if board[x][y] == opponent)
        
        total_corners = player_corners + opponent_corners
        if total_corners > 0:
            corner_score = (player_corners - opponent_corners) / 4
        else:
            corner_score = 0
            
        # 6. Краевые клетки
        edges = []
        for i in range(8):
            edges.append((0, i))  # Верхний край
            edges.append((7, i))  # Нижний край
            edges.append((i, 0))  # Левый край
            edges.append((i, 7))  # Правый край
        
        # Удаляем углы из списка краев, чтобы избежать двойного подсчета
        for corner in self.corners:
            if corner in edges:
                edges.remove(corner)
        
        player_edges = sum(1 for x, y in edges if board[x][y] == player)
        opponent_edges = sum(1 for x, y in edges if board[x][y] == opponent)
        
        total_edges = player_edges + opponent_edges
        if total_edges > 0:
            edge_score = (player_edges - opponent_edges) / 24  # 24 края без углов
        else:
            edge_score = 0
            
        # 7. Паттерны (формирование клиньев, захват диагоналей и т.д.)
        # Пример: диагональ из углов
        diagonals = [
            [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7)],
            [(0, 7), (1, 6), (2, 5), (3, 4), (4, 3), (5, 2), (6, 1), (7, 0)]
        ]
        
        pattern_score = 0
        for diagonal in diagonals:
            player_count = sum(1 for x, y in diagonal if board[x][y] == player)
            opponent_count = sum(1 for x, y in diagonal if board[x][y] == opponent)
            
            if player_count > opponent_count:
                pattern_score += 0.1
            elif opponent_count > player_count:
                pattern_score -= 0.1
        
        # 8. Паритет (четность/нечетность пустых клеток)
        empty_count = sum(row.count("empty") for row in board)
        parity_score = 0
        
        # Четный/нечетный паритет важен только в конце игры
        if game_phase == "late" and empty_count < 10:
            if empty_count % 2 == 0:  # Четное число пустых клеток
                parity_score = 0.1
            else:  # Нечетное число пустых клеток
                parity_score = -0.1
        
        # 9. Потенциальная мобильность (количество пустых клеток рядом с фишками противника)
        player_potential_mobility = self.count_potential_mobility(board, player)
        opponent_potential_mobility = self.count_potential_mobility(board, opponent)
        
        total_potential_mobility = player_potential_mobility + opponent_potential_mobility
        if total_potential_mobility > 0:
            potential_mobility_score = (player_potential_mobility - opponent_potential_mobility) / total_potential_mobility
        else:
            potential_mobility_score = 0
        
        # Если игрок владеет всеми углами, то это сильный бонус
        if player_corners == 4:
            corner_score = 1.0
        
        # Если противник владеет всеми углами, то это сильный штраф
        if opponent_corners == 4:
            corner_score = -1.0
        
        # Комбинированная оценка с весами
        final_score = (
            weights['pieces'] * piece_ratio +
            weights['position'] * positional_score +
            weights['mobility'] * mobility_score +
            weights['stability'] * stability_score +
            weights['corners'] * corner_score +
            weights['edges'] * edge_score +
            weights['patterns'] * pattern_score +
            weights['parity'] * parity_score
        )
        
        # Добавляем штраф за опасные клетки рядом с углами
        for i, j in self.dangerous_cells:
            if board[i][j] == player:
                # Проверяем, не занят ли соответствующий угол
                if (i <= 1 and j <= 1) and board[0][0] == "empty":
                    final_score -= 0.05
                elif (i <= 1 and j >= 6) and board[0][7] == "empty":
                    final_score -= 0.05
                elif (i >= 6 and j <= 1) and board[7][0] == "empty":
                    final_score -= 0.05
                elif (i >= 6 and j >= 6) and board[7][7] == "empty":
                    final_score -= 0.05
            elif board[i][j] == opponent:
                # Если противник занимает опасные клетки, это хорошо для нас
                if (i <= 1 and j <= 1) and board[0][0] == "empty":
                    final_score += 0.05
                elif (i <= 1 and j >= 6) and board[0][7] == "empty":
                    final_score += 0.05
                elif (i >= 6 and j <= 1) and board[7][0] == "empty":
                    final_score += 0.05
                elif (i >= 6 and j >= 6) and board[7][7] == "empty":
                    final_score += 0.05
        
        # Ограничиваем оценку в диапазоне [-1, 1]
        return max(-1, min(1, final_score))
    
    def count_mobility(self, board, player):
        """
        Считает количество всех возможных ходов для игрока
        
        Args:
            board (list): текущее состояние доски
            player (str): игрок ('black' или 'white')
            
        Returns:
            int: количество возможных ходов
        """
        valid_moves = self._count_valid_moves(board, player)
        return valid_moves
    
    def _count_valid_moves(self, board, player):
        """
        Подсчитывает количество допустимых ходов для игрока
        
        Args:
            board (list): текущее состояние доски
            player (str): игрок ('black' или 'white')
            
        Returns:
            int: количество возможных ходов
        """
        valid_count = 0
        opponent = "white" if player == "black" else "black"
        directions = [(0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1)]
        
        for row in range(8):
            for col in range(8):
                if board[row][col] != "empty":
                    continue
                
                # Проверяем все направления
                for dr, dc in directions:
                    r, c = row + dr, col + dc
                    # Первая соседняя клетка должна быть занята противником
                    if not (0 <= r < 8 and 0 <= c < 8 and board[r][c] == opponent):
                        continue
                    
                    # Идем дальше в этом направлении
                    r += dr
                    c += dc
                    valid_direction = False
                    
                    while 0 <= r < 8 and 0 <= c < 8:
                        if board[r][c] == "empty":
                            break
                        if board[r][c] == player:
                            valid_direction = True
                            break
                        r += dr
                        c += dc
                    
                    if valid_direction:
                        valid_count += 1
                        break  # Достаточно найти один валидный ход для этой клетки
        
        return valid_count
    
    def count_potential_mobility(self, board, player):
        """
        Алиас для _count_potential_mobility для обратной совместимости
        """
        return self._count_potential_mobility(board, player)
    
    def _count_potential_mobility(self, board, player):
        """
        Подсчитывает потенциальную мобильность - пустые клетки рядом с фишками противника
        
        Args:
            board (list): текущее состояние доски
            player (str): игрок ('black' или 'white')
            
        Returns:
            int: оценка потенциальной мобильности
        """
        opponent = "white" if player == "black" else "black"
        potential = 0
        directions = [(0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1)]
        
        for row in range(8):
            for col in range(8):
                if board[row][col] == opponent:
                    # Для каждой фишки противника считаем пустые клетки вокруг
                    for dr, dc in directions:
                        r, c = row + dr, col + dc
                        if 0 <= r < 8 and 0 <= c < 8 and board[r][c] == "empty":
                            potential += 1
        
        return potential
    
    def count_stable_discs(self, board, player):
        """
        Алиас для _count_stable_discs для обратной совместимости
        """
        return self._count_stable_discs(board, player)
    
    def _count_stable_discs(self, board, player):
        """
        Подсчитывает количество стабильных фишек (которые нельзя перевернуть)
        Стабильные фишки - это фишки в углах, на краях, а также те, которые образуют 
        непрерывную линию с угловыми фишками
        
        Args:
            board (list): текущее состояние доски
            player (str): игрок ('black' или 'white')
            
        Returns:
            int: количество стабильных фишек
        """
        stable_count = 0
        stable_positions = set()
        
        # Проверяем углы
        for r, c in self.corners:
            if board[r][c] == player:
                stable_positions.add((r, c))
        
        # Проверяем края и фишки, связанные с углами
        changed = True
        while changed:
            changed = False
            
            for row in range(8):
                for col in range(8):
                    if board[row][col] != player or (row, col) in stable_positions:
                        continue
                    
                    # Проверяем, стабильна ли фишка
                    is_stable = self._is_stable_disc(board, row, col, stable_positions)
                    
                    if is_stable:
                        stable_positions.add((row, col))
                        changed = True
        
        return len(stable_positions)
    
    def _is_stable_disc(self, board, row, col, stable_positions):
        """
        Проверяет, является ли фишка стабильной
        
        Args:
            board (list): текущее состояние доски
            row (int): ряд фишки
            col (int): колонка фишки
            stable_positions (set): множество уже определенных стабильных позиций
            
        Returns:
            bool: True если фишка стабильна, иначе False
        """
        # Фишка на краю доски
        is_edge = row == 0 or row == 7 or col == 0 or col == 7
        
        if not is_edge:
            # Не краевая фишка - проверяем связи со стабильными фишками
            directions = [(0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1)]
            stable_directions = 0
            
            for dr, dc in directions:
                r, c = row + dr, col + dc
                # Фишка стабильна в направлении, если она соединена со стабильной фишкой
                # или достигает края доски без прерываний в этом направлении
                while 0 <= r < 8 and 0 <= c < 8:
                    if board[r][c] != board[row][col]:
                        break
                    if (r, c) in stable_positions:
                        stable_directions += 1
                        break
                    r += dr
                    c += dc
            
            # Фишка стабильна, если она стабильна хотя бы в 4 различных направлениях
            return stable_directions >= 4
        
        # Краевая фишка уже считается стабильной, если связана со стабильной фишкой
        directions = []
        if row == 0:
            directions.append((0, 1))
            directions.append((0, -1))
        elif row == 7:
            directions.append((0, 1))
            directions.append((0, -1))
        if col == 0:
            directions.append((1, 0))
            directions.append((-1, 0))
        elif col == 7:
            directions.append((1, 0))
            directions.append((-1, 0))
            
        for dr, dc in directions:
            r, c = row + dr, col + dc
            while 0 <= r < 8 and 0 <= c < 8:
                if board[r][c] != board[row][col]:
                    break
                if (r, c) in stable_positions:
                    return True
                r += dr
                c += dc
                    
        # Если это краевая фишка, но не связана со стабильной, 
        # она все равно может быть стабильной, если нет пустых клеток в линии
        return is_edge
    
    def count_corners(self, board, player, opponent):
        """
        Подсчитывает количество углов, занятых каждым игроком
        """
        player_corners = 0
        opponent_corners = 0
        
        for row, col in self.corners:
            if board[row][col] == player:
                player_corners += 1
            elif board[row][col] == opponent:
                opponent_corners += 1
        
        return player_corners, opponent_corners
    
    def count_edges(self, board, player, opponent):
        """
        Подсчитывает количество краевых клеток, занятых каждым игроком
        """
        player_edges = 0
        opponent_edges = 0
        
        # Верхняя и нижняя строки
        for col in range(1, 7):
            if board[0][col] == player:
                player_edges += 1
            elif board[0][col] == opponent:
                opponent_edges += 1
                
            if board[7][col] == player:
                player_edges += 1
            elif board[7][col] == opponent:
                opponent_edges += 1
        
        # Левый и правый столбцы
        for row in range(1, 7):
            if board[row][0] == player:
                player_edges += 1
            elif board[row][0] == opponent:
                opponent_edges += 1
                
            if board[row][7] == player:
                player_edges += 1
            elif board[row][7] == opponent:
                opponent_edges += 1
        
        return player_edges, opponent_edges
    
    def evaluate_patterns(self, board, player, opponent):
        """
        Оценивает позицию на основе распознавания паттернов
        """
        score = 0
        
        # Проверяем опасность X-клеток (диагонали от углов)
        for row, col in self.x_squares:
            corner_row, corner_col = 0 if row < 4 else 7, 0 if col < 4 else 7
            
            if board[corner_row][corner_col] == "empty":
                if board[row][col] == player:
                    score -= 10  # Увеличиваем штраф за X-клетку
                elif board[row][col] == opponent:
                    score += 5  # Хорошо, если противник занял опасную позицию
            elif board[corner_row][corner_col] == player:
                # Если угол наш, X-клетка уже не опасна
                if board[row][col] == player:
                    score += 2
        
        # Проверяем опасность C-клеток (рядом с углами)
        for row, col in self.c_squares:
            corner_row = 0 if row < 4 else 7
            corner_col = 0 if col < 4 else 7
            
            if board[corner_row][corner_col] == "empty":
                if board[row][col] == player:
                    score -= 8  # Увеличиваем штраф за C-клетку
                elif board[row][col] == opponent:
                    score += 4  # Хорошо, если противник занял опасную позицию
            elif board[corner_row][corner_col] == player:
                # Если угол наш, C-клетка уже не опасна
                if board[row][col] == player:
                    score += 1
        
        # Проверяем диагональные структуры (сложнее атаковать)
        diag1_player = sum(1 for i in range(8) if i < 8 and board[i][i] == player)
        diag1_opponent = sum(1 for i in range(8) if i < 8 and board[i][i] == opponent)
        
        diag2_player = sum(1 for i in range(8) if i < 8 and board[i][7-i] == player)
        diag2_opponent = sum(1 for i in range(8) if i < 8 and board[i][7-i] == opponent)
        
        score += (diag1_player - diag1_opponent) * 2
        score += (diag2_player - diag2_opponent) * 2
        
        # Бонус за контроль центра (4x4 квадрат в центре)
        center_player = 0
        center_opponent = 0
        for row in range(2, 6):
            for col in range(2, 6):
                if board[row][col] == player:
                    center_player += 1
                elif board[row][col] == opponent:
                    center_opponent += 1
        
        score += (center_player - center_opponent) * 0.5
        
        return score
    
    def evaluate_parity(self, board, player):
        """
        Оценивает паритет (четность числа пустых клеток)
        """
        empty_count = sum(row.count("empty") for row in board)
        score = 0
        
        # На поздней стадии игры паритет становится важным
        if empty_count < 20:
            # Если количество пустых клеток четное, то последний ход сделает тот,
            # кто не делает первый ход в этом регионе
            is_even = empty_count % 2 == 0
            
            # Предполагаем, что черные ходят первыми
            if (player == "black" and is_even) or (player == "white" and not is_even):
                score -= 10  # Увеличиваем значимость паритета
            else:
                score += 10
                
        # В середине игры тоже немного учитываем паритет
        elif empty_count < 40:
            is_even = empty_count % 2 == 0
            if (player == "black" and is_even) or (player == "white" and not is_even):
                score -= 2
            else:
                score += 2
        
        return score
    
    def determine_game_phase(self, board):
        """
        Определяет текущую фазу игры на основе количества пустых клеток
        
        Args:
            board: текущее состояние доски
            
        Returns:
            str: фаза игры ('early', 'middle', 'late')
        """
        empty_count = sum(row.count("empty") for row in board)
        
        if empty_count > 45:
            return "early"  # Дебют (первые 10-15 ходов)
        elif empty_count > 15:  # Слегка корректируем границу
            return "middle"  # Миттельшпиль
        else:
            return "late"  # Эндшпиль 
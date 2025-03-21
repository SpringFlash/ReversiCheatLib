"""
Базовый модуль для работы с игровой доской Реверси
"""

class Board:
    """
    Класс для представления и манипуляции с игровой доской Реверси
    """
    def __init__(self):
        self.size = 8
        self.directions = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1),  (1, 0),  (1, 1),
        ]
        
        # Инициализация пустой доски
        self.reset()
    
    def reset(self):
        """
        Сбрасывает доску к начальному состоянию
        """
        # Создаем пустую доску
        self.board = [["empty" for _ in range(self.size)] for _ in range(self.size)]
        
        # Устанавливаем начальные фишки в центре доски
        self.board[3][3] = "white"
        self.board[3][4] = "black"
        self.board[4][3] = "black"
        self.board[4][4] = "white"
    
    def get_board(self):
        """
        Получает текущее состояние доски
        
        Returns:
            list: двумерный массив, представляющий доску
        """
        return self.board
    
    def set_board(self, board):
        """
        Устанавливает состояние доски
        
        Args:
            board (list): двумерный массив, представляющий новое состояние доски
        """
        if len(board) != self.size or any(len(row) != self.size for row in board):
            raise ValueError(f"Размер доски должен быть {self.size}x{self.size}")
        
        self.board = [row[:] for row in board]  # Создаем глубокую копию доски
    
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
        if not (0 <= row < self.size and 0 <= col < self.size):
            return False
            
        if self.board[row][col] != "empty":
            return False
        
        opponent = "white" if player == "black" else "black"
        
        for dx, dy in self.directions:
            x, y = row + dx, col + dy
            found_opponent = False
            
            while 0 <= x < self.size and 0 <= y < self.size:
                if self.board[x][y] == "empty":
                    break
                if self.board[x][y] == opponent:
                    found_opponent = True
                elif self.board[x][y] == player and found_opponent:
                    return True
                else:
                    break
                x += dx
                y += dy
        
        return False
    
    def get_flips(self, row, col, player):
        """
        Определяет, какие фишки будут перевернуты при ходе
        
        Args:
            row (int): строка
            col (int): столбец
            player (str): цвет игрока ('black' или 'white')
            
        Returns:
            list: список координат переворачиваемых фишек
        """
        opponent = "white" if player == "black" else "black"
        flip_positions = []
        
        for dx, dy in self.directions:
            x, y = row + dx, col + dy
            direction_flips = []
            
            while 0 <= x < self.size and 0 <= y < self.size:
                if self.board[x][y] == "empty":
                    break
                if self.board[x][y] == opponent:
                    direction_flips.append((x, y))
                elif self.board[x][y] == player:
                    flip_positions.extend(direction_flips)
                    break
                else:
                    break
                x += dx
                y += dy
                
        return flip_positions
    
    def make_move(self, row, col, player):
        """
        Выполняет ход и обновляет доску
        
        Args:
            row (int): строка
            col (int): столбец
            player (str): цвет игрока ('black' или 'white')
            
        Returns:
            bool: True если ход был выполнен успешно, иначе False
        """
        if not self.is_valid_move(row, col, player):
            return False
        
        flip_positions = self.get_flips(row, col, player)
        
        # Размещаем фишку игрока
        self.board[row][col] = player
        
        # Переворачиваем фишки противника
        for row, col in flip_positions:
            self.board[row][col] = player
            
        return True
    
    def get_valid_moves(self, player):
        """
        Находит все допустимые ходы для игрока
        
        Args:
            player (str): цвет игрока ('black' или 'white')
            
        Returns:
            list: список координат допустимых ходов [(row, col), ...]
        """
        valid_moves = []
        
        for row in range(self.size):
            for col in range(self.size):
                if self.is_valid_move(row, col, player):
                    valid_moves.append((row, col))
        
        # Отладочная информация
        if valid_moves:
            moves_str = ", ".join([f"{chr(65 + col)}{row + 1}" for row, col in valid_moves])
            print(f"Найдено {len(valid_moves)} доступных ходов для {player}: {moves_str}")
        else:
            print(f"Не найдено доступных ходов для {player}")
                    
        return valid_moves
    
    def count_pieces(self):
        """
        Подсчитывает количество фишек каждого цвета на доске
        
        Returns:
            dict: словарь с количеством фишек {'black': int, 'white': int, 'empty': int}
        """
        black_count = sum(row.count("black") for row in self.board)
        white_count = sum(row.count("white") for row in self.board)
        empty_count = sum(row.count("empty") for row in self.board)
        
        return {
            "black": black_count,
            "white": white_count,
            "empty": empty_count
        }
    
    def is_game_over(self):
        """
        Проверяет, завершена ли игра
        
        Returns:
            bool: True если игра завершена (никто не может сделать ход), иначе False
        """
        # Если нет пустых клеток, игра закончена
        if self.count_pieces()["empty"] == 0:
            return True
            
        # Если хотя бы один игрок может сделать ход, игра не закончена
        black_moves = self.get_valid_moves("black")
        white_moves = self.get_valid_moves("white")
        
        return len(black_moves) == 0 and len(white_moves) == 0
    
    def get_winner(self):
        """
        Определяет победителя, если игра завершена
        
        Returns:
            str: 'black', 'white' или 'tie', или None если игра не окончена
        """
        if not self.is_game_over():
            return None
            
        counts = self.count_pieces()
        
        if counts["black"] > counts["white"]:
            return "black"
        elif counts["white"] > counts["black"]:
            return "white"
        else:
            return "tie"
    
    def board_to_string(self):
        """
        Конвертирует доску в строку для хеширования
        
        Returns:
            str: строковое представление доски
        """
        result = ""
        for row in self.board:
            for cell in row:
                if cell == "black":
                    result += "b"
                elif cell == "white":
                    result += "w"
                else:
                    result += "e"
        return result
    
    def clone(self):
        """
        Создает копию доски
        
        Returns:
            Board: новый экземпляр Board с такой же позицией
        """
        new_board = Board()
        new_board.board = [row[:] for row in self.board]
        return new_board 
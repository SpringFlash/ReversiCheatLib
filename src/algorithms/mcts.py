"""
Модуль для реализации алгоритма Monte Carlo Tree Search (MCTS)
"""
import time
import math
import random
from src.core.heuristics import ReversiHeuristics

class MCTSNode:
    """
    Узел дерева для алгоритма Monte Carlo Tree Search
    """
    def __init__(self, board, parent=None, move=None, player=None):
        self.board = board  # Текущее состояние доски
        self.parent = parent  # Родительский узел
        self.move = move  # Ход, приведший к этому узлу
        self.player = player  # Игрок, который сделал ход
        self.children = []  # Дочерние узлы
        self.visits = 0  # Количество посещений узла
        self.wins = 0  # Количество "побед" с этого узла
        self.untried_moves = None  # Неисследованные ходы
    
    def select_child(self, exploration_weight=1.414):
        """
        Выбирает дочерний узел с наибольшим UCT значением
        
        Args:
            exploration_weight: вес для члена исследования
            
        Returns:
            MCTSNode: выбранный дочерний узел
        """
        # Выбираем дочерний узел с максимальным UCT значением
        # UCT = wins/visits + exploration_weight * sqrt(ln(parent_visits)/visits)
        best_score = float('-inf')
        best_child = None
        
        # Динамически корректируем вес исследования в зависимости от количества посещений
        adjusted_weight = exploration_weight
        
        # Если были сделаны много посещений, уменьшаем вес исследования
        if self.visits > 500:
            adjusted_weight = exploration_weight * 0.8
        # Если есть несколько посещенных детей, уменьшаем вес исследования
        elif len([c for c in self.children if c.visits > 0]) > 2:
            adjusted_weight = exploration_weight * 0.9
        
        for child in self.children:
            if child.visits == 0:
                return child  # Всегда выбираем непосещенный узел в первую очередь
            
            # Вычисляем UCT значение
            exploration = math.sqrt(math.log(self.visits) / child.visits)
            uct_value = (child.wins / child.visits) + (adjusted_weight * exploration)
            
            # Для угловых ходов добавляем бонус к UCT
            if child.move in [(0, 0), (0, 7), (7, 0), (7, 7)]:
                uct_value += 0.2
            
            if uct_value > best_score:
                best_score = uct_value
                best_child = child
        
        return best_child
    
    def add_child(self, board, move, player):
        """
        Добавляет дочерний узел
        
        Args:
            board: состояние доски
            move: ход
            player: игрок
            
        Returns:
            MCTSNode: созданный дочерний узел
        """
        child = MCTSNode(board, self, move, player)
        self.children.append(child)
        return child
    
    def update(self, result):
        """
        Обновляет статистику узла
        
        Args:
            result: результат симуляции (True - победа, False - поражение)
        """
        self.visits += 1
        self.wins += result

class MCTSAlgorithm:
    """
    Класс для реализации алгоритма Monte Carlo Tree Search
    для игры Реверси
    """
    def __init__(self):
        self.heuristics = ReversiHeuristics()
        self.max_time = 0.5  # Максимальное время на ход в секундах
        self.max_iterations = 3000  # Максимальное количество итераций
        self.exploration_weight = 1.414  # Параметр для баланса исследования/использования
        self.position_weights = [
            [120, -20, 20, 5, 5, 20, -20, 120],
            [-20, -40, -5, -5, -5, -5, -40, -20],
            [20, -5, 15, 3, 3, 15, -5, 20],
            [5, -5, 3, 3, 3, 3, -5, 5],
            [5, -5, 3, 3, 3, 3, -5, 5],
            [20, -5, 15, 3, 3, 15, -5, 20],
            [-20, -40, -5, -5, -5, -5, -40, -20],
            [120, -20, 20, 5, 5, 20, -20, 120]
        ]
        self.root = None  # Корневой узел дерева поиска
        
    def get_best_move(self, board, player, max_iterations=None):
        """
        Находит лучший ход с использованием алгоритма MCTS
        
        Args:
            board: объект класса Board с текущим состоянием доски
            player: цвет игрока ('black' или 'white')
            max_iterations: максимальное количество итераций
            
        Returns:
            dict: словарь с координатами хода и оценкой, или None если ходов нет
        """
        # Устанавливаем максимальное количество итераций, если не указано
        if max_iterations is None:
            max_iterations = self.max_iterations
        
        start_time = time.time()
        iterations = 0
        
        # Получаем все допустимые ходы
        valid_moves = board.get_valid_moves(player)
        
        if not valid_moves:
            return None
            
        # Если есть только один ход, возвращаем его
        if len(valid_moves) == 1:
            move = valid_moves[0]
            return {"row": move[0], "col": move[1], "score": 0}
            
        # Если есть ход в угол, сразу берем его
        corners = [(0, 0), (0, 7), (7, 0), (7, 7)]
        for move in valid_moves:
            if move in corners:
                return {"row": move[0], "col": move[1], "score": 1000}
        
        # Проверяем, можем ли мы повторно использовать дерево поиска
        if self.root is not None:
            # Находим дочерний узел, соответствующий последнему ходу противника
            board_hash = self._board_to_hash(board.get_board())
            matching_child = None
            
            for child in self.root.children:
                if self._board_to_hash(child.board.get_board()) == board_hash:
                    matching_child = child
                    break
            
            if matching_child:
                # Переиспользуем поддерево
                self.root = matching_child
                self.root.parent = None  # Отсоединяем от родителя
        else:
            # Создаем новый корневой узел
            self.root = MCTSNode(board.clone())
            self.root.untried_moves = valid_moves.copy()
        
        # Основной цикл MCTS
        while iterations < max_iterations and (time.time() - start_time) < self.max_time:
            # 1. Выбор
            node = self._select(self.root)
            
            # 2. Расширение
            if node.untried_moves and len(node.untried_moves) > 0:
                node = self._expand(node, player)
            
            # 3. Симуляция
            result = self._simulate(node, player)
            
            # 4. Обратное распространение
            self._backpropagate(node, result)
            
            iterations += 1
        
        # Выбираем лучший ход
        best_child = None
        best_visits = -1
        
        for child in self.root.children:
            # Выбираем ход с наибольшим количеством посещений
            if child.visits > best_visits:
                best_visits = child.visits
                best_child = child
        
        if best_child:
            win_rate = best_child.wins / best_child.visits if best_child.visits > 0 else 0
            return {"row": best_child.move[0], "col": best_child.move[1], "score": win_rate}
        else:
            # Если почему-то нет детей, берем случайный ход
            move = random.choice(valid_moves)
            return {"row": move[0], "col": move[1], "score": 0}
    
    def _select(self, node):
        """
        Выбор: проходим по дереву, выбирая узлы с максимальным UCT
        пока не дойдем до листа или узла с неисследованными ходами
        
        Args:
            node: начальный узел
            
        Returns:
            MCTSNode: выбранный узел
        """
        while node.untried_moves is None or len(node.untried_moves) == 0:
            if not node.children:
                # Лист дерева
                return node
            
            # Выбираем дочерний узел с наибольшим UCT
            node = node.select_child(self.exploration_weight)
        
        return node
    
    def _expand(self, node, player):
        """
        Расширение: добавляем новый дочерний узел, делая один из
        неисследованных ходов
        
        Args:
            node: узел для расширения
            player: текущий игрок
            
        Returns:
            MCTSNode: созданный дочерний узел
        """
        # Используем эвристику для выбора хода для расширения
        if node.untried_moves:
            # Сортируем ходы по позиционной ценности
            weighted_moves = []
            for move in node.untried_moves:
                row, col = move
                weight = self.position_weights[row][col]
                weighted_moves.append((move, weight))
            
            # С вероятностью 0.7 выбираем лучший ход, иначе случайный
            if random.random() < 0.7:
                weighted_moves.sort(key=lambda x: x[1], reverse=True)
                move = weighted_moves[0][0]
            else:
                move = random.choice(node.untried_moves)
            
            node.untried_moves.remove(move)
            
            # Создаем новую доску с этим ходом
            new_board = node.board.clone()
            new_board.make_move(move[0], move[1], player)
            
            # Определяем следующего игрока
            next_player = "white" if player == "black" else "black"
            
            # Создаем и добавляем новый дочерний узел
            child = node.add_child(new_board, move, player)
            
            # Инициализируем список неисследованных ходов для нового узла
            child.untried_moves = new_board.get_valid_moves(next_player)
            
            return child
        
        return node
    
    def _simulate(self, node, player):
        """
        Симуляция: проводим случайную игру от текущего узла до конца
        
        Args:
            node: узел, от которого начинается симуляция
            player: текущий игрок
            
        Returns:
            float: результат симуляции (1 - победа, 0 - поражение, 0.5 - ничья)
                  для исходного игрока
        """
        simulation_board = node.board.clone()
        current_player = "white" if player == "black" else "black"  # Меняем игрока после расширения
        
        # Запоминаем исходного игрока
        original_player = player
        
        # Максимальное количество ходов для симуляции
        max_simulation_moves = 40
        simulation_moves = 0
        
        # Пока игра не закончена и не превышено максимальное количество ходов
        while not simulation_board.is_game_over() and simulation_moves < max_simulation_moves:
            # Получаем возможные ходы
            valid_moves = simulation_board.get_valid_moves(current_player)
            
            if not valid_moves:
                # Пропускаем ход, если нет возможных ходов
                current_player = "white" if current_player == "black" else "black"
                continue
            
            # Используем эвристику для выбора хода в симуляции
            if random.random() < 0.8:  # 80% случаев используем эвристику
                # Сортируем ходы по эвристической ценности
                moves_with_values = []
                
                for move in valid_moves:
                    row, col = move
                    
                    # Базовая позиционная ценность
                    value = self.position_weights[row][col]
                    
                    # Для углов и краев дополнительный бонус
                    if move in [(0, 0), (0, 7), (7, 0), (7, 7)]:
                        value += 1000  # Углы очень ценны
                    elif row == 0 or row == 7 or col == 0 or col == 7:
                        value += 100  # Края тоже ценны
                    
                    # Проверяем захват фишек
                    board_copy = simulation_board.clone()
                    board_copy.make_move(row, col, current_player)
                    pieces_diff = board_copy.count_pieces()[current_player] - simulation_board.count_pieces()[current_player]
                    value += pieces_diff * 10
                    
                    moves_with_values.append((move, value))
                
                # Выбираем лучший ход с вероятностью 80%, иначе случайный из топ-3
                if random.random() < 0.8 and moves_with_values:
                    moves_with_values.sort(key=lambda x: x[1], reverse=True)
                    move = moves_with_values[0][0]
                else:
                    # Выбираем случайный ход из топ-3 (или меньше, если ходов меньше)
                    moves_with_values.sort(key=lambda x: x[1], reverse=True)
                    top_n = min(3, len(moves_with_values))
                    move = moves_with_values[random.randint(0, top_n-1)][0]
            else:
                # Случайный ход
                move = random.choice(valid_moves)
            
            # Делаем ход
            simulation_board.make_move(move[0], move[1], current_player)
            
            # Меняем игрока
            current_player = "white" if current_player == "black" else "black"
            
            simulation_moves += 1
        
        # Определяем результат игры
        if simulation_board.is_game_over():
            winner = simulation_board.get_winner()
            if winner == original_player:
                return 1.0  # Победа
            elif winner == "tie":
                return 0.5  # Ничья
            else:
                return 0.0  # Поражение
        else:
            # Если игра не окончена (превышено максимальное количество ходов),
            # используем эвристику для оценки позиции
            game_phase = self.heuristics.determine_game_phase(simulation_board.get_board())
            score = self.heuristics.evaluate_position(simulation_board.get_board(), original_player, game_phase)
            
            # Нормализуем оценку к диапазону [0, 1]
            normalized_score = (score + 1) / 2
            return normalized_score
    
    def _backpropagate(self, node, result):
        """
        Обратное распространение: обновляем статистику для всех узлов
        на пути от листа до корня
        
        Args:
            node: узел, от которого начинается обратное распространение
            result: результат симуляции
        """
        # Обновляем статистику для всех узлов на пути от листа до корня
        while node is not None:
            node.update(result)
            node = node.parent
            # Инвертируем результат для родительского узла (другого игрока)
            result = 1 - result
    
    def _board_to_hash(self, board):
        """
        Преобразует доску в хеш-строку для сравнения состояний
        
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
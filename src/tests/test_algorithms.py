"""
Тестирование улучшенных алгоритмов для игры Реверси
"""
from reversi_logic import ReversiLogic
import time

def test_algorithms():
    """
    Тестирует улучшенные алгоритмы на разных стадиях игры
    """
    # Создаем экземпляр логики игры
    logic = ReversiLogic()
    
    print("Тестирование улучшенных алгоритмов для игры Реверси")
    print("=" * 70)
    
    # Начальная стадия (MCTS)
    test_algorithm(logic, "black", "MCTS (начальная стадия)")
    
    # Имитируем переход к середине игры путем заполнения доски
    fill_board_to_middle_game(logic)
    
    # Середина игры (NegaScout)
    test_algorithm(logic, "black", "NegaScout (середина игры)")
    
    # Имитируем переход к концу игры
    fill_board_to_end_game(logic)
    
    # Конец игры (Minimax)
    test_algorithm(logic, "black", "Minimax (конец игры)")
    
    # Выводим статистику использования алгоритмов
    print("\nСтатистика использования алгоритмов:")
    print("-" * 70)
    print(f"MCTS:      Использовано {logic.algorithm_stats['mcts']['used']} раз, " 
          f"среднее время: {logic.algorithm_stats['mcts']['time'] / max(1, logic.algorithm_stats['mcts']['used']):.3f} сек, "
          f"средняя оценка: {logic.algorithm_stats['mcts']['avg_score']:.3f}")
    print(f"NegaScout: Использовано {logic.algorithm_stats['negascout']['used']} раз, "
          f"среднее время: {logic.algorithm_stats['negascout']['time'] / max(1, logic.algorithm_stats['negascout']['used']):.3f} сек, "
          f"средняя оценка: {logic.algorithm_stats['negascout']['avg_score']:.3f}")
    print(f"Minimax:   Использовано {logic.algorithm_stats['minimax']['used']} раз, "
          f"среднее время: {logic.algorithm_stats['minimax']['time'] / max(1, logic.algorithm_stats['minimax']['used']):.3f} сек, "
          f"средняя оценка: {logic.algorithm_stats['minimax']['avg_score']:.3f}")
    
    # Проверяем файл лога
    print(f"\nЛог игры сохранен в файле: {logic.log_file}")

def test_algorithm(logic, player, algorithm_name):
    """
    Тестирует работу алгоритма и выводит информацию о ходе
    
    Args:
        logic: экземпляр класса ReversiLogic
        player: цвет игрока ('black' или 'white')
        algorithm_name: название алгоритма для вывода
    """
    print(f"\nТестирование алгоритма: {algorithm_name}")
    print("-" * 70)
    
    # Выводим текущее состояние доски
    print("Текущее состояние доски:")
    print_board(logic.get_board())
    
    # Получаем количество фишек
    pieces = logic.count_pieces()
    print(f"Черных: {pieces['black']}, Белых: {pieces['white']}, Пустых: {pieces['empty']}")
    
    # Получаем допустимые ходы
    valid_moves = logic.get_valid_moves(player)
    print(f"Доступные ходы для {player}: {', '.join([f'({r},{c})' for r, c in valid_moves])}")
    
    # Засекаем время и получаем лучший ход
    start_time = time.time()
    best_move = logic.get_best_move(player)
    elapsed_time = time.time() - start_time
    
    if best_move:
        row, col = best_move["row"], best_move["col"]
        score = best_move["score"]
        print(f"Лучший ход: ({row}, {col}) с оценкой {score:.3f}")
        print(f"Время вычисления: {elapsed_time:.3f} сек")
        
        # Делаем ход
        logic.make_move(row, col, player)
        
        # Логируем ход
        logic.log_move(player, (row, col))
        
        # Выводим обновленное состояние доски
        print("\nДоска после хода:")
        print_board(logic.get_board())
    else:
        print("Нет доступных ходов")

def fill_board_to_middle_game(logic):
    """
    Заполняет доску для имитации середины игры
    
    Args:
        logic: экземпляр класса ReversiLogic
    """
    print("\nИмитация середины игры...")
    
    # Создаем новую доску в состоянии середины игры
    logic.reset_game()
    
    # Установка фишек для середины игры (20 ходов)
    board = logic.board.board
    
    # Очищаем доску
    for i in range(8):
        for j in range(8):
            board[i][j] = "empty"
            
    # Устанавливаем фишки для середины игры
    # Черные фишки
    black_positions = [(2, 2), (2, 3), (2, 4), (3, 2), (3, 3), (3, 4), 
                      (4, 2), (4, 3), (4, 4), (5, 2), (5, 3), (5, 4)]
    
    # Белые фишки
    white_positions = [(1, 1), (1, 2), (1, 3), (2, 1), (3, 1), (4, 1), 
                      (5, 1), (6, 1), (6, 2), (6, 3)]
    
    # Расставляем фишки
    for row, col in black_positions:
        board[row][col] = "black"
        
    for row, col in white_positions:
        board[row][col] = "white"
        
    print("Доска для середины игры подготовлена.")

def fill_board_to_end_game(logic):
    """
    Заполняет доску для имитации конца игры
    
    Args:
        logic: экземпляр класса ReversiLogic
    """
    print("\nИмитация конца игры...")
    
    # Создаем новую доску в состоянии конца игры
    logic.reset_game()
    
    # Установка фишек для конца игры (более 50 фишек на доске)
    board = logic.board.board
    
    # Очищаем доску
    for i in range(8):
        for j in range(8):
            board[i][j] = "empty"
            
    # Устанавливаем фишки для конца игры
    # Заполняем большую часть доски белыми фишками
    for i in range(8):
        for j in range(8):
            if (i <= 5 and j <= 5) or (i == 6 and j <= 3) or (i <= 3 and j == 6):
                board[i][j] = "white"
    
    # Добавляем черные фишки, которые еще могут ходить
    black_positions = [(0, 6), (0, 7), (1, 6), (1, 7), (2, 6), (2, 7), 
                      (3, 7), (4, 6), (4, 7), (5, 6), (5, 7), (6, 4), 
                      (6, 5), (6, 6), (6, 7), (7, 0), (7, 1), (7, 2), 
                      (7, 3), (7, 4), (7, 5), (7, 6), (7, 7)]
    
    for row, col in black_positions:
        board[row][col] = "black"
        
    print("Доска для конца игры подготовлена.")

def print_board(board):
    """
    Выводит доску в консоль
    
    Args:
        board: двумерный массив с состоянием доски
    """
    print("  | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |")
    print("--+---+---+---+---+---+---+---+---+")
    
    for i, row in enumerate(board):
        line = f"{i} |"
        for cell in row:
            if cell == "black":
                line += " ● |"
            elif cell == "white":
                line += " ○ |"
            else:
                line += "   |"
        print(line)
        print("--+---+---+---+---+---+---+---+---+")

if __name__ == "__main__":
    test_algorithms() 
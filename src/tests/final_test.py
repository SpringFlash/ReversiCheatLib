import time
import os
import json
import sys
from reversi_logic import ReversiLogic
from heuristics import ReversiHeuristics

def run_full_test():
    """
    Запускает полное тестирование улучшенных алгоритмов
    """
    print("=" * 80)
    print("ФИНАЛЬНОЕ ТЕСТИРОВАНИЕ УЛУЧШЕННЫХ АЛГОРИТМОВ ДЛЯ РЕВЕРСИ")
    print("=" * 80)
    print()
    
    logic = ReversiLogic()
    
    # Сбрасываем статистику перед тестированием
    logic.reset_statistics()
    
    # Статистика для оценки производительности
    stats = {
        "mcts": {
            "avg_time": 0,
            "avg_score": 0,
            "count": 0,
            "corners_captured": 0,
            "win_rate": 0
        },
        "negascout": {
            "avg_time": 0,
            "avg_score": 0,
            "count": 0,
            "corners_captured": 0,
            "win_rate": 0
        },
        "minimax": {
            "avg_time": 0,
            "avg_score": 0,
            "count": 0,
            "corners_captured": 0,
            "win_rate": 0
        }
    }
    
    # 1. Тест MCTS на ранней стадии
    print("\nТЕСТ 1: MCTS НА РАННЕЙ СТАДИИ")
    print("-" * 50)
    
    # Количество симуляций
    num_simulations = 3
    wins = 0
    
    for i in range(num_simulations):
        print(f"Симуляция {i+1}/{num_simulations}")
        
        # Сбрасываем игру
        logic.reset_game()
        
        # Игра до 15 ходов
        for move_num in range(15):
            print(f"Ход #{move_num + 1}")
            
            # Получаем текущее состояние игры
            board = logic.board
            player = "black"  # Мы всегда играем за черных
            
            # Проверяем, может ли текущий игрок ходить
            valid_moves = logic.get_valid_moves(player)
            if not valid_moves:
                print(f"Нет доступных ходов для {player}")
                continue
            
            # Получаем лучший ход с помощью MCTS
            start_time = time.time()
            move, score = logic.get_best_move(player, game_phase="early")
            end_time = time.time()
            
            if move:
                # Делаем ход
                row, col = move
                logic.make_move(row, col, player)
                
                # Обновляем статистику
                stats["mcts"]["avg_time"] += end_time - start_time
                stats["mcts"]["avg_score"] += score
                stats["mcts"]["count"] += 1
                
                # Проверяем, захватил ли ход угол
                if move in [(0, 0), (0, 7), (7, 0), (7, 7)]:
                    stats["mcts"]["corners_captured"] += 1
                    
                print(f"Ход: {move}, Оценка: {score:.3f}, Время: {end_time - start_time:.3f} сек")
            else:
                print("Не удалось найти ход")
            
            # Имитируем ход компьютера (случайный допустимый ход)
            opponent_moves = logic.get_valid_moves("white")
            if opponent_moves:
                # Берем ход, который не оптимален (имитация слабого противника)
                opponent_move = logic.get_opponent_move("white", "weak")
                if opponent_move:
                    row, col = opponent_move
                    logic.make_move(row, col, "white")
                    print(f"Ход компьютера: {opponent_move}")
                else:
                    print("Компьютер не смог сделать ход")
            else:
                print("Компьютер пропускает ход")
        
        # После 15 ходов проверяем, кто выигрывает
        black_count = logic.count_pieces("black")
        white_count = logic.count_pieces("white")
        
        if black_count > white_count:
            wins += 1
            print(f"Мы выигрываем: {black_count} vs {white_count}")
        else:
            print(f"Мы проигрываем: {black_count} vs {white_count}")
    
    # Обновляем статистику выигрышей
    stats["mcts"]["win_rate"] = wins / num_simulations
    
    # 2. Тест NegaScout на средней стадии
    print("\nТЕСТ 2: NEGASCOUT НА СРЕДНЕЙ СТАДИИ")
    print("-" * 50)
    
    # Сбрасываем счетчики
    wins = 0
    
    for i in range(num_simulations):
        print(f"Симуляция {i+1}/{num_simulations}")
        
        # Создаем доску для средней стадии игры
        logic.reset_game()
        logic = prepare_middle_game(logic)
        
        # Игра еще 10 ходов
        for move_num in range(10):
            print(f"Ход #{move_num + 1}")
            
            # Получаем текущее состояние игры
            board = logic.board
            player = "black"  # Мы всегда играем за черных
            
            # Проверяем, может ли текущий игрок ходить
            valid_moves = logic.get_valid_moves(player)
            if not valid_moves:
                print(f"Нет доступных ходов для {player}")
                continue
            
            # Получаем лучший ход с помощью NegaScout
            start_time = time.time()
            move, score = logic.get_best_move(player, game_phase="middle")
            end_time = time.time()
            
            if move:
                # Делаем ход
                row, col = move
                logic.make_move(row, col, player)
                
                # Обновляем статистику
                stats["negascout"]["avg_time"] += end_time - start_time
                stats["negascout"]["avg_score"] += score
                stats["negascout"]["count"] += 1
                
                # Проверяем, захватил ли ход угол
                if move in [(0, 0), (0, 7), (7, 0), (7, 7)]:
                    stats["negascout"]["corners_captured"] += 1
                    
                print(f"Ход: {move}, Оценка: {score:.3f}, Время: {end_time - start_time:.3f} сек")
            else:
                print("Не удалось найти ход")
            
            # Имитируем ход компьютера (случайный допустимый ход)
            opponent_moves = logic.get_valid_moves("white")
            if opponent_moves:
                # Берем средний по качеству ход (имитация среднего противника)
                opponent_move = logic.get_opponent_move("white", "medium")
                if opponent_move:
                    row, col = opponent_move
                    logic.make_move(row, col, "white")
                    print(f"Ход компьютера: {opponent_move}")
                else:
                    print("Компьютер не смог сделать ход")
            else:
                print("Компьютер пропускает ход")
        
        # После ходов проверяем, кто выигрывает
        black_count = logic.count_pieces("black")
        white_count = logic.count_pieces("white")
        
        if black_count > white_count:
            wins += 1
            print(f"Мы выигрываем: {black_count} vs {white_count}")
        else:
            print(f"Мы проигрываем: {black_count} vs {white_count}")
    
    # Обновляем статистику выигрышей
    stats["negascout"]["win_rate"] = wins / num_simulations
    
    # 3. Тест Minimax на поздней стадии
    print("\nТЕСТ 3: MINIMAX НА ПОЗДНЕЙ СТАДИИ")
    print("-" * 50)
    
    # Сбрасываем счетчики
    wins = 0
    
    for i in range(num_simulations):
        print(f"Симуляция {i+1}/{num_simulations}")
        
        # Создаем доску для поздней стадии игры
        logic.reset_game()
        logic = prepare_late_game(logic)
        
        # Игра до конца или до максимального числа ходов
        game_over = False
        move_num = 0
        max_moves = 30  # Ограничиваем количество ходов
        
        while not game_over and move_num < max_moves:
            move_num += 1
            print(f"Ход #{move_num}")
            
            # Получаем текущее состояние игры
            board = logic.board
            player = "black"  # Мы всегда играем за черных
            
            # Проверяем, может ли текущий игрок ходить
            valid_moves = logic.get_valid_moves(player)
            if not valid_moves:
                print(f"Нет доступных ходов для {player}")
                
                # Проверяем, может ли противник ходить
                opponent_moves = logic.get_valid_moves("white")
                if not opponent_moves:
                    # Никто не может ходить, игра окончена
                    game_over = True
                    break
                    
                continue
            
            # Получаем лучший ход с помощью Minimax
            start_time = time.time()
            move, score = logic.get_best_move(player, game_phase="late")
            end_time = time.time()
            
            if move:
                # Делаем ход
                row, col = move
                logic.make_move(row, col, player)
                
                # Обновляем статистику
                stats["minimax"]["avg_time"] += end_time - start_time
                stats["minimax"]["avg_score"] += score
                stats["minimax"]["count"] += 1
                
                # Проверяем, захватил ли ход угол
                if move in [(0, 0), (0, 7), (7, 0), (7, 7)]:
                    stats["minimax"]["corners_captured"] += 1
                    
                print(f"Ход: {move}, Оценка: {score:.3f}, Время: {end_time - start_time:.3f} сек")
            else:
                print("Не удалось найти ход")
            
            # Проверяем, закончилась ли игра
            if logic.is_game_over():
                game_over = True
                break
            
            # Имитируем ход компьютера (сильный противник)
            opponent_moves = logic.get_valid_moves("white")
            if opponent_moves:
                opponent_move = logic.get_opponent_move("white", "strong")
                if opponent_move:
                    row, col = opponent_move
                    logic.make_move(row, col, "white")
                    print(f"Ход компьютера: {opponent_move}")
                else:
                    print("Компьютер не смог сделать ход")
            else:
                print("Компьютер пропускает ход")
            
            # Проверяем, закончилась ли игра
            if logic.is_game_over():
                game_over = True
        
        # Если вышли по лимиту ходов
        if move_num >= max_moves and not game_over:
            print(f"Достигнут лимит ходов ({max_moves})")
        
        # После игры проверяем, кто выиграл
        black_count = logic.count_pieces("black")
        white_count = logic.count_pieces("white")
        
        if black_count > white_count:
            wins += 1
            print(f"Мы выиграли: {black_count} vs {white_count}")
        elif black_count < white_count:
            print(f"Мы проиграли: {black_count} vs {white_count}")
        else:
            print(f"Ничья: {black_count} vs {white_count}")
            # Считаем ничью как половину победы
            wins += 0.5
    
    # Обновляем статистику выигрышей
    stats["minimax"]["win_rate"] = wins / num_simulations
    
    # Нормализуем статистику
    if stats["mcts"]["count"] > 0:
        stats["mcts"]["avg_time"] /= stats["mcts"]["count"]
        stats["mcts"]["avg_score"] /= stats["mcts"]["count"]
        
    if stats["negascout"]["count"] > 0:
        stats["negascout"]["avg_time"] /= stats["negascout"]["count"]
        stats["negascout"]["avg_score"] /= stats["negascout"]["count"]
        
    if stats["minimax"]["count"] > 0:
        stats["minimax"]["avg_time"] /= stats["minimax"]["count"]
        stats["minimax"]["avg_score"] /= stats["minimax"]["count"]
    
    # Выводим итоговую статистику
    print("\n" + "=" * 80)
    print("ИТОГОВАЯ СТАТИСТИКА")
    print("=" * 80)
    
    print("\nMCTS (ранняя стадия):")
    print(f"  Среднее время: {stats['mcts']['avg_time']:.5f} сек")
    print(f"  Средняя оценка: {stats['mcts']['avg_score']:.5f}")
    print(f"  Захвачено углов: {stats['mcts']['corners_captured']}")
    print(f"  Процент побед: {stats['mcts']['win_rate'] * 100:.1f}%")
    
    print("\nNegaScout (средняя стадия):")
    print(f"  Среднее время: {stats['negascout']['avg_time']:.5f} сек")
    print(f"  Средняя оценка: {stats['negascout']['avg_score']:.5f}")
    print(f"  Захвачено углов: {stats['negascout']['corners_captured']}")
    print(f"  Процент побед: {stats['negascout']['win_rate'] * 100:.1f}%")
    
    print("\nMinimax (поздняя стадия):")
    print(f"  Среднее время: {stats['minimax']['avg_time']:.5f} сек")
    print(f"  Средняя оценка: {stats['minimax']['avg_score']:.5f}")
    print(f"  Захвачено углов: {stats['minimax']['corners_captured']}")
    print(f"  Процент побед: {stats['minimax']['win_rate'] * 100:.1f}%")
    
    print("\nОбщий процент побед: {:.1f}%".format(
        (stats["mcts"]["win_rate"] + stats["negascout"]["win_rate"] + stats["minimax"]["win_rate"]) * 100 / 3
    ))
    
    # Сохраняем статистику в файл
    save_stats_to_file(stats)
    
    print("\nРезультаты тестирования сохранены в logs/final_test_results.json")

def prepare_middle_game(logic):
    """
    Подготавливает доску для средней стадии игры
    """
    # Заполняем доску паттерном для средней игры
    for i in range(3):
        row, col = 2+i, 2
        logic.make_move(row, col, "black")
        row, col = 2+i, 3
        logic.make_move(row, col, "black")
        row, col = 2+i, 4
        logic.make_move(row, col, "black")
        row, col = 1, 2+i
        logic.make_move(row, col, "white")
        row, col = 6, 2+i
        logic.make_move(row, col, "white")
    
    return logic

def prepare_late_game(logic):
    """
    Подготавливает доску для поздней стадии игры
    """
    # Сначала очищаем доску (все клетки пустые)
    for i in range(8):
        for j in range(8):
            logic.board.board[i][j] = "empty"
    
    # Заполняем большую часть доски в шахматном порядке
    for i in range(6):
        for j in range(6):
            if (i + j) % 2 == 0:
                logic.board.board[i][j] = "black"
            else:
                logic.board.board[i][j] = "white"
    
    # Устанавливаем угловые клетки для преимущества черных
    logic.board.board[0][0] = "black"
    logic.board.board[0][7] = "black"
    
    # Оставляем несколько пустых клеток в которые можно ходить
    logic.board.board[6][0] = "empty"
    logic.board.board[6][1] = "empty"
    logic.board.board[7][0] = "empty"
    logic.board.board[7][1] = "empty"
    
    # Добавляем белые фишки рядом с пустыми клетками, чтобы их можно было перевернуть
    logic.board.board[5][0] = "white"
    logic.board.board[5][1] = "white"
    logic.board.board[6][2] = "white"
    
    return logic

def save_stats_to_file(stats):
    """
    Сохраняет статистику в JSON-файл
    """
    # Создаем директорию logs, если ее нет
    if not os.path.exists("logs"):
        os.makedirs("logs")
    
    # Создаем словарь с данными
    data = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "stats": stats,
        "overall_win_rate": (stats["mcts"]["win_rate"] + stats["negascout"]["win_rate"] + stats["minimax"]["win_rate"]) / 3
    }
    
    # Записываем в файл
    with open("logs/final_test_results.json", "w") as f:
        json.dump(data, f, indent=2)

if __name__ == "__main__":
    run_full_test() 
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Скрипт для запуска автоматической игры в Реверси
Просто запустите этот скрипт из командной строки:
python play_reversi.py
"""

import sys
import argparse
import subprocess
import json
import os
import traceback

def main():
    """
    Основная функция скрипта
    """
    # Создаем парсер аргументов командной строки
    parser = argparse.ArgumentParser(description='Автоматическая игра в Реверси')
    
    # Добавляем аргументы
    parser.add_argument('--window', '-w', type=str, default='Удаленное управление - ANT DAO TECHNOLOGY LIMITED R2022',
                        help='Название окна игры (по умолчанию: "Удаленное управление - ANT DAO TECHNOLOGY LIMITED R2022")')
    parser.add_argument('--interval', '-i', type=float, default=3.0,
                        help='Интервал между ходами в секундах (по умолчанию: 3.0)')
    parser.add_argument('--delay', '-d', type=float, default=0.5,
                        help='Задержка перед кликом в секундах (по умолчанию: 0.5)')
    parser.add_argument('--max-moves', '-m', type=int, default=None,
                        help='Максимальное количество ходов (по умолчанию: без ограничений, 0 также означает без ограничений)')
    parser.add_argument('--border-top', '-bt', type=int, default=45,
                        help='Верхний отступ в пикселях (по умолчанию: 45)')
    parser.add_argument('--border-left', '-bl', type=int, default=10,
                        help='Левый отступ в пикселях (по умолчанию: 10)')
    parser.add_argument('--border-bottom', '-bb', type=int, default=70,
                        help='Нижний отступ в пикселях (по умолчанию: 70)')
    parser.add_argument('--logic-only', '-lo', action='store_true',
                        help='Использовать только логику игры для анализа доски, без автоматических кликов')
    parser.add_argument('--board-file', '-bf', type=str,
                        help='Путь к JSON-файлу с состоянием доски (используется с --logic-only)')
    
    # Парсим аргументы
    args = parser.parse_args()
    
    try:
        # Проверяем, был ли запрошен режим работы только с логикой
        if args.logic_only:
            analyze_board_logic_only(args.board_file)
            return
            
        # Формируем команду для запуска процесса
        cmd = [
            sys.executable, 'src/process_image.py', '--auto-play-interval',
            args.window,
            str(args.interval),
            str(args.delay)
        ]
        
        # Добавляем максимальное количество ходов, если указано
        if args.max_moves is not None:
            cmd.append(str(args.max_moves))
        else:
            # Добавляем значение "0" вместо пустой строки, чтобы избежать ошибки при преобразовании в int
            # "0" будет означать неограниченное количество ходов
            cmd.append("0")
        
        # Добавляем параметры отступов
        cmd.extend([
            str(args.border_top),
            str(args.border_left),
            str(args.border_bottom)
        ])
        
        # Запускаем процесс
        print(f"Запускаем команду: {sys.executable} src/ui/process_image.py --auto-play-interval \"{args.window}\" {args.interval} {args.delay} 0 {args.border_top} {args.border_left} {args.border_bottom}")
        try:
            # Используем абсолютный путь к файлу process_image.py
            process_image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'process_image.py')
            subprocess.run([
                sys.executable, 
                process_image_path, 
                '--auto-play-interval', 
                args.window, 
                str(args.interval), 
                str(args.delay), 
                "0", 
                str(args.border_top), 
                str(args.border_left), 
                str(args.border_bottom)
            ], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Ошибка при выполнении команды: {e}")
            sys.exit(1)
        
    except KeyboardInterrupt:
        print("\nИгра остановлена пользователем")
        sys.exit(0)
    except Exception as e:
        print(f"Ошибка: {str(e)}")
        sys.exit(1)

def analyze_board_logic_only(board_file):
    """
    Анализирует доску, используя только логику игры, без автоматических кликов
    Args:
        board_file (str): Путь к JSON-файлу с состоянием доски
    """
    try:
        # Импортируем модуль логики игры
        print("Импортируем модуль логики игры...")
        import sys
        import os
        
        # Добавляем корневую директорию проекта в путь поиска модулей
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        project_root = os.path.dirname(parent_dir)
        sys.path.append(project_root)
        print(f"Добавлены пути поиска: {current_dir}, {parent_dir}, {project_root}")
        
        # Импортируем модуль логики
        from src.core.reversi_logic import ReversiLogic
        print("Модуль ReversiLogic успешно импортирован")
        
        # Если файл не указан, выводим сообщение об ошибке
        if not board_file:
            print("Ошибка: не указан файл с состоянием доски")
            print("Используйте параметр --board-file или -bf для указания пути к JSON-файлу")
            print("Пример JSON-файла:")
            example = {
                "board": [
                    ["empty", "empty", "empty", "empty", "empty", "empty", "empty", "empty"],
                    ["empty", "empty", "empty", "empty", "empty", "empty", "empty", "empty"],
                    ["empty", "empty", "empty", "empty", "empty", "empty", "empty", "empty"],
                    ["empty", "empty", "empty", "white", "black", "empty", "empty", "empty"],
                    ["empty", "empty", "empty", "black", "white", "empty", "empty", "empty"],
                    ["empty", "empty", "empty", "empty", "empty", "empty", "empty", "empty"],
                    ["empty", "empty", "empty", "empty", "empty", "empty", "empty", "empty"],
                    ["empty", "empty", "empty", "empty", "empty", "empty", "empty", "empty"]
                ],
                "player_color": "black"
            }
            print(json.dumps(example, indent=2))
            return
        
        # Проверяем существование файла
        if not os.path.exists(board_file):
            print(f"Ошибка: файл '{board_file}' не существует")
            return
        
        print(f"Чтение файла: {board_file}")
        # Загружаем состояние доски из файла
        with open(board_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Проверяем наличие необходимых полей
        if 'board' not in data:
            print("Ошибка: в файле отсутствует поле 'board'")
            return
            
        if 'player_color' not in data:
            print("Ошибка: в файле отсутствует поле 'player_color'")
            return
        
        print("Данные успешно загружены из файла")    
        # Создаем объект логики игры
        print("Создание объекта логики игры...")
        game_logic = ReversiLogic()
        print("Объект логики игры успешно создан")
        
        # Анализируем состояние доски и находим лучший ход
        board = data['board']
        player_color = data['player_color']
        
        # Получаем информацию о состоянии доски
        print("Подсчет фишек на доске...")
        piece_count = game_logic.count_pieces(board)
        print(f"Состояние доски:")
        print(f"  Черные фишки: {piece_count['black']}")
        print(f"  Белые фишки: {piece_count['white']}")
        print(f"  Пустые клетки: {piece_count['empty']}")
        print(f"Цвет игрока: {player_color}")
        
        # Находим все возможные ходы
        print("Поиск возможных ходов...")
        valid_moves = game_logic.find_valid_moves(board, player_color)
        
        if not valid_moves:
            print("Нет доступных ходов")
            return
        
        print(f"Найдено ходов: {len(valid_moves)}")    
        # Сортируем ходы по оценке
        valid_moves.sort(key=lambda x: x["score"], reverse=True)
        
        # Выводим информацию о возможных ходах
        print(f"\nДоступные ходы ({len(valid_moves)}):")
        for i, move in enumerate(valid_moves[:10]):  # Выводим только первые 10 ходов
            row, col = move["row"], move["col"]
            col_letter = chr(65 + col)  # Преобразуем столбец в букву (A, B, C, ...)
            row_number = row + 1  # Нумерация строк с 1
            print(f"{i+1}. {col_letter}{row_number} (строка {row}, столбец {col}), оценка: {move['score']}")
            
        # Находим лучший ход
        print("Поиск лучшего хода с использованием алгоритма альфа-бета...")
        # Устанавливаем доску в game_logic
        game_logic.board.set_board(board)
        # Вызываем get_best_move только с параметром player_color
        best_move, score = game_logic.get_best_move(player_color)
        
        if best_move:
            row, col = best_move
            col_letter = chr(65 + col)
            row_number = row + 1
            
            print(f"\nЛучший ход: {col_letter}{row_number} (строка {row}, столбец {col}), оценка: {score}")
            
            # Показываем, как будет выглядеть доска после этого хода
            new_board = game_logic.make_move(board, row, col, player_color)
            new_piece_count = game_logic.count_pieces(new_board)
            
            print(f"\nПосле хода:")
            print(f"  Черные фишки: {new_piece_count['black']} ({'+' if new_piece_count['black'] > piece_count['black'] else ''}{new_piece_count['black'] - piece_count['black']})")
            print(f"  Белые фишки: {new_piece_count['white']} ({'+' if new_piece_count['white'] > piece_count['white'] else ''}{new_piece_count['white'] - piece_count['white']})")
            print(f"  Пустые клетки: {new_piece_count['empty']} ({new_piece_count['empty'] - piece_count['empty']})")
        else:
            print("Не удалось найти лучший ход")
        
    except Exception as e:
        print(f"Ошибка при анализе доски: {str(e)}")
        traceback.print_exc() # Выводим полный стек ошибки

if __name__ == "__main__":
    main() 
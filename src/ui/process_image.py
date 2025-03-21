import cv2
import numpy as np
import sys
import json
import os
import pyautogui  # Добавляем импорт pyautogui для захвата экрана
import base64
from io import BytesIO
import time
import ctypes
from ctypes import wintypes, windll, create_unicode_buffer, byref, sizeof

# Добавляем корневую директорию проекта в путь поиска модулей
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
project_root = os.path.dirname(parent_dir)
sys.path.append(project_root)

# Импортируем ReversiLogic из пакета core
from src.core.reversi_logic import ReversiLogic

# Необходимые константы и структуры для работы с Windows API
class RECT(ctypes.Structure):
    _fields_ = [
        ("left", ctypes.c_long),
        ("top", ctypes.c_long),
        ("right", ctypes.c_long),
        ("bottom", ctypes.c_long)
    ]

class POINT(ctypes.Structure):
    _fields_ = [
        ("x", ctypes.c_long),
        ("y", ctypes.c_long)
    ]

def get_window_info(window_title, border_top=45, border_left=10, border_bottom=70):
    """
    Получает информацию о положении и размерах окна по его названию
    Args:
        window_title (str): Название окна
        border_top (int): Верхний отступ (рамка с заголовком)
        border_left (int): Левый отступ (рамка)
        border_bottom (int): Нижний отступ (навигационные кнопки)
    Returns:
        dict: Информация о положении и размерах окна или None, если окно не найдено
    """
    try:
        # Получаем хендл окна по его названию
        hwnd = windll.user32.FindWindowW(None, window_title)
        if hwnd == 0:
            return {
                "success": False,
                "error": f"Окно с названием '{window_title}' не найдено"
            }
        
        # Получаем размеры клиентской области окна
        client_rect = RECT()
        if not windll.user32.GetClientRect(hwnd, byref(client_rect)):
            return {
                "success": False,
                "error": "Не удалось получить размеры клиентской области окна"
            }
        
        # Преобразуем координаты клиентской области в экранные координаты
        point = POINT(0, 0)
        if not windll.user32.ClientToScreen(hwnd, byref(point)):
            return {
                "success": False,
                "error": "Не удалось преобразовать координаты клиентской области в экранные"
            }
        
        # Добавляем отступы для удаления рамок и нижней панели
        # Отступы основаны на изображении: верхняя и боковые рамки + нижний интерфейс
        
        # Возвращаем информацию о положении и размерах внутренней части окна
        return {
            "success": True,
            "window_info": {
                "x": point.x + border_left,
                "y": point.y + border_top,
                "width": client_rect.right - border_left * 2,
                "height": client_rect.bottom - border_top - border_bottom
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def calculate_click_coordinates(board_rect, row, col):
    # Получаем координаты углов доски
    top_left = board_rect[0]
    top_right = board_rect[1]
    bottom_right = board_rect[2]
    
    # Вычисляем размеры доски
    board_width = np.linalg.norm(top_right - top_left)
    board_height = np.linalg.norm(bottom_right - top_right)
    
    # Размер одной клетки
    cell_width = board_width / 8
    cell_height = board_height / 8
    
    # Вычисляем вектора направления
    x_dir = (top_right - top_left) / 8
    y_dir = (bottom_right - top_right) / 8
    
    # Вычисляем координаты клика (центр нужной клетки)
    click_point = top_left + x_dir * (col + 0.5) + y_dir * (row + 0.5)
    
    return {
        "x": int(click_point[0]),
        "y": int(click_point[1])
    }

def detect_player_color(image, board_rect):
    # Получаем координаты верхней части игрового поля
    top_left = board_rect[0]
    top_right = board_rect[1]
    
    # Вычисляем ширину игрового поля
    board_width = np.linalg.norm(top_right - top_left)
    
    # Определяем область для поиска счета игрока
    # Счет находится справа от поля, примерно на уровне верхней границы
    score_width = int(board_width * 0.1)  # Ширина области счета
    score_height = int(board_width * 0.1)  # Высота области счета

    # Координаты области счета (справа от поля)
    score_x = int(top_right[0] - board_width * 0.285)  # Сдвинули область на 18% влево (было 0.07, стало 0.25)
    score_y = int(top_right[1] - board_width * 0.3)  # Центрируем по вертикали относительно верха поля
    
    # Проверяем границы изображения
    height, width = image.shape[:2]
    score_x = min(max(0, score_x), width - score_width)
    score_y = min(max(0, score_y), height - score_height)
    
    
    # Вырезаем область счета
    score_region = image[
        score_y:score_y + score_height,
        score_x:score_x + score_width
    ]
    
    # Сохраняем область для отладки
    # cv2.imwrite('debug_score_region.png', score_region)
    
    # Преобразуем в HSV для определения цвета
    hsv = cv2.cvtColor(score_region, cv2.COLOR_BGR2HSV)
    
    # Маски для определения цвета фона счета
    white_mask = cv2.inRange(hsv, np.array([0, 0, 180]), np.array([180, 30, 255]))
    black_mask = cv2.inRange(hsv, np.array([0, 0, 0]), np.array([180, 255, 60]))
    
    # cv2.imwrite('debug_white_mask_score.png', white_mask)
    # cv2.imwrite('debug_black_mask_score.png', black_mask)
    
    # Подсчитываем пиксели каждого цвета
    white_pixels = cv2.countNonZero(white_mask)
    black_pixels = cv2.countNonZero(black_mask)
    
    # Определяем цвет игрока (противоположный цвету фона счета)
    total_pixels = score_region.shape[0] * score_region.shape[1]
    threshold = total_pixels * 0.3
    
    detected_color = None
    
    if white_pixels > threshold:
        detected_color = "white"  # Если фон белый, игрок играет черными
    elif black_pixels > threshold:
        detected_color = "black"  # Если фон темный, игрок играет белыми
    
    # Альтернативный метод определения на основе анализа доски
    if detected_color is None:
        # Получаем текущее состояние доски
        board_img, _ = find_game_board(image)
        board_state = analyze_board_state(board_img)
        
        # Подсчитываем количество фишек каждого цвета
        black_count = sum(row.count("black") for row in board_state)
        white_count = sum(row.count("white") for row in board_state)
        
        # Если белых больше, вероятно, ход черных и наоборот
        if black_count > white_count:
            detected_color = "white"
        else:
            detected_color = "black"
        
        print(f"Определение цвета по альтернативному методу: {detected_color} (черных: {black_count}, белых: {white_count})")
    
    print(f"Определен цвет игрока: {detected_color}")
    return detected_color

def find_game_board(image):
    try:
        # Преобразуем в оттенки серого
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Размываем для уменьшения шума
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Применяем адаптивную пороговую обработку
        thresh = cv2.adaptiveThreshold(
            blurred,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV,
            11,
            2
        )
        
        # Сохраняем пороговое изображение для отладки
        # cv2.imwrite('debug_threshold.png', thresh)
        
        # Ищем контуры
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Сохраняем для отладки
        debug_contours = image.copy()
        cv2.drawContours(debug_contours, contours, -1, (0, 255, 0), 2)
        # cv2.imwrite('debug_contours.png', debug_contours)
        
        # Ищем самый большой прямоугольный контур
        max_area = 0
        game_board_rect = None
        
        # Проходим по всем контурам
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > 1000:  # Фильтруем маленькие контуры
                peri = cv2.arcLength(cnt, True)
                approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
                
                # Сохраняем аппроксимацию для отладки
                debug_approx = image.copy()
                cv2.drawContours(debug_approx, [approx], -1, (0, 0, 255), 2)
                
                # Ищем прямоугольник или четырехугольник
                if 4 <= len(approx) <= 6 and area > max_area:
                    # cv2.imwrite(f'debug_approx.png', debug_approx)
                    max_area = area
                    game_board_rect = approx
        
        # Если не нашли игровое поле, попробуем найти его по другим признакам
        if game_board_rect is None:
            # Попробуем обнаружить доску по цвету фона (обычно зеленый)
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            # Зеленый цвет в HSV
            lower_green = np.array([40, 40, 40])
            upper_green = np.array([80, 255, 255])
            green_mask = cv2.inRange(hsv, lower_green, upper_green)
            
            # Применяем морфологические операции для улучшения маски
            kernel = np.ones((5, 5), np.uint8)
            green_mask = cv2.dilate(green_mask, kernel, iterations=2)
            green_mask = cv2.erode(green_mask, kernel, iterations=2)
            
            # cv2.imwrite('debug_green_mask.png', green_mask)
            
            # Ищем контуры на маске
            green_contours, _ = cv2.findContours(green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Ищем самый большой контур
            max_green_area = 0
            for cnt in green_contours:
                area = cv2.contourArea(cnt)
                if area > max_green_area:
                    max_green_area = area
                    peri = cv2.arcLength(cnt, True)
                    approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
                    game_board_rect = approx
            
            if game_board_rect is None:
                # Если все еще не нашли доску, предположим, что доска занимает большую часть изображения
                h, w = image.shape[:2]
                game_board_rect = np.array([
                    [0, 0],
                    [w-1, 0],
                    [w-1, h-1],
                    [0, h-1]
                ], dtype=np.int32).reshape(4, 1, 2)
                print("Не удалось точно обнаружить игровое поле, используем всё изображение")
        
        # Сортируем точки для правильной трансформации
        pts = game_board_rect.reshape(4, 2)
        rect = np.zeros((4, 2), dtype="float32")
        
        # Верхняя левая точка будет иметь наименьшую сумму координат
        # Нижняя правая - наибольшую
        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)]
        rect[2] = pts[np.argmax(s)]
        
        # Верхняя правая точка будет иметь наименьшую разность координат
        # Нижняя левая - наибольшую
        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)]
        rect[3] = pts[np.argmax(diff)]
        
        # Получаем ширину и высоту целевого изображения
        width = max(
            int(np.linalg.norm(rect[1] - rect[0])),
            int(np.linalg.norm(rect[2] - rect[3]))
        )
        height = max(
            int(np.linalg.norm(rect[3] - rect[0])),
            int(np.linalg.norm(rect[2] - rect[1]))
        )
        
        # Задаем точки назначения
        dst = np.array([
            [0, 0],
            [width - 1, 0],
            [width - 1, height - 1],
            [0, height - 1]
        ], dtype="float32")
        
        # Получаем матрицу трансформации и применяем её
        M = cv2.getPerspectiveTransform(rect, dst)
        warped = cv2.warpPerspective(image, M, (width, height))
        
        # Сохраняем выровненное изображение
        # cv2.imwrite('debug_warped.png', warped)
        
        return warped, rect
    except Exception as e:
        print(f"Ошибка при поиске игрового поля: {str(e)}")
        # Возвращаем исходное изображение без изменений
        h, w = image.shape[:2]
        rect = np.array([
            [0, 0],
            [w-1, 0],
            [w-1, h-1],
            [0, h-1]
        ], dtype="float32")
        return image, rect

def capture_screen_region(x, y, width, height):
    """
    Захватывает определенную область экрана и анализирует её
    Args:
        x (int): X-координата левого верхнего угла
        y (int): Y-координата левого верхнего угла
        width (int): Ширина области захвата
        height (int): Высота области захвата
    Returns:
        dict: Результат анализа изображения
    """
    try:
        # Захватываем область экрана с помощью pyautogui
        screenshot = pyautogui.screenshot(region=(x, y, width, height))

        # Конвертируем в формат OpenCV
        image = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        # Сохраняем изображение через cv2
        # cv2.imwrite('screenshot.png', image)
        # Находим и выравниваем игровое поле
        board, board_rect = find_game_board(image)
        
        # Определяем цвет игрока
        player_color = detect_player_color(image, board_rect)
        
        # Анализируем состояние доски
        board_state = analyze_board_state(board)
        
        # Создаем объект логики игры
        game_logic = ReversiLogic()
        
        # Устанавливаем текущее состояние доски
        game_logic.board.set_board(board_state)
        
        # Находим лучший ход
        best_move, score = game_logic.get_best_move(player_color)
        
        result = {
            "success": True,
            "board": board_state,
            "player_color": player_color,
            "screen_size": {
                "width": image.shape[1],
                "height": image.shape[0]
            },
            "board_rect": {
                "top_left": board_rect[0].tolist(),
                "top_right": board_rect[1].tolist(),
                "bottom_right": board_rect[2].tolist(),
                "bottom_left": board_rect[3].tolist()
            }
        }
        
        # Если есть лучший ход, добавляем его в результат
        if best_move:
            # Вычисляем координаты клика
            row, col = best_move
            click_coords = calculate_click_coordinates(board_rect, row, col)
            
            result["has_move"] = True
            result["move"] = {
                "row": row,
                "col": col,
                "score": score,
                "screen_coordinates": click_coords
            }
        else:
            # Дополнительная проверка доступных ходов
            valid_moves = game_logic.get_valid_moves(player_color)
            if valid_moves:
                # Если есть доступные ходы, но алгоритм не смог найти лучший ход,
                # выбираем первый доступный ход
                row, col = valid_moves[0]
                click_coords = calculate_click_coordinates(board_rect, row, col)
                
                result["has_move"] = True
                result["move"] = {
                    "row": row,
                    "col": col,
                    "score": 0.5,  # Нейтральная оценка
                    "screen_coordinates": click_coords
                }
                print(f"Применен запасной вариант: найдено {len(valid_moves)} доступных ходов, выбран ход ({row},{col})")
            else:
                result["has_move"] = False
                print(f"Действительно нет доступных ходов для {player_color}")
        
        return result
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def analyze_board_state(board):
    """
    Анализирует состояние доски
    """
    # Преобразуем в HSV для лучшего определения цветов
    hsv = cv2.cvtColor(board, cv2.COLOR_BGR2HSV)
    
    # Создаем маски для разных цветов
    white_lower = np.array([80, 10, 180])
    white_upper = np.array([120, 50, 255])
    white_mask = cv2.inRange(hsv, white_lower, white_upper)
    
    black_mask = cv2.inRange(hsv, np.array([0, 0, 0]), np.array([180, 255, 60]))
    
    # Создаем пустую доску 8x8
    board_state = [["empty" for _ in range(8)] for _ in range(8)]
    
    # Размер одной клетки
    height, width = board.shape[:2]
    cell_size = min(height, width) // 8
    
    # Анализируем каждую клетку
    for row in range(8):
        for col in range(8):
            # Координаты центра клетки
            center_x = int((col + 0.5) * cell_size)
            center_y = int((row + 0.5) * cell_size)
            
            # Область для анализа (25% от размера клетки)
            radius = int(cell_size * 0.25)
            x1 = max(0, center_x - radius)
            x2 = min(width, center_x + radius)
            y1 = max(0, center_y - radius)
            y2 = min(height, center_y + radius)
            
            # Подсчитываем пиксели каждого цвета в области
            white_pixels = cv2.countNonZero(white_mask[y1:y2, x1:x2])
            black_pixels = cv2.countNonZero(black_mask[y1:y2, x1:x2])
            
            # Определяем содержимое клетки
            total_area = (y2 - y1) * (x2 - x1)
            threshold = total_area * 0.2
            
            if white_pixels > threshold:
                board_state[row][col] = "white"
            elif black_pixels > threshold:
                board_state[row][col] = "black"
            else:
                board_state[row][col] = "empty"
    
    return board_state

def perform_click(x, y):
    """
    Выполняет клик по указанным координатам
    
    Args:
        x (int): X-координата
        y (int): Y-координата
        
    Returns:
        dict: Результат операции
    """
    try:
        # Перемещаем курсор и выполняем клик
        pyautogui.click(x, y)
        return {
            "success": True,
            "coordinates": {
                "x": x,
                "y": y
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def auto_play(window_info, delay=1.0):
    """
    Автоматически делает ход в игре Реверси
    Args:
        window_info (dict): Информация о положении окна игры
        delay (float): Задержка перед кликом в секундах
    Returns:
        dict: Результат операции
    """
    try:
        # Получаем координаты и размеры окна
        x = window_info['x']
        y = window_info['y']
        width = window_info['width']
        height = window_info['height']
        
        # Создаем объект логики игры, если он еще не существует
        global game_logic
        if 'game_logic' not in globals() or game_logic is None:
            game_logic = ReversiLogic()
        
        # Захватываем и анализируем экран
        result = capture_screen_region(x, y, width, height)
        
        # Проверяем результат анализа
        if not result['success']:
            return {
                "success": False,
                "error": result.get('error', 'Ошибка при анализе изображения')
            }
        
        # Если в прошлый раз у нас был ход, проверяем, сделал ли противник ход
        if hasattr(game_logic, 'last_board_state'):
            # Получаем текущее состояние доски
            current_board = result['board']
            
            # Ищем ход противника, сравнивая текущее состояние с предыдущим
            opponent_move = detect_opponent_move(game_logic.last_board_state, current_board, result['player_color'])
            
            # Если нашли ход противника, записываем его в лог
            if opponent_move:
                # Обновляем состояние доски в логике игры
                game_logic.board.set_board(current_board)
                
                # Получаем цвет противника
                opponent_color = "white" if result['player_color'] == "black" else "black"
                
                # Записываем ход противника в лог
                game_logic.log_move(
                    player=opponent_color,
                    move=opponent_move,
                    is_our_move=False
                )
        
        # Сохраняем текущее состояние доски для следующего хода
        game_logic.last_board_state = result['board']
        
        # Обновляем состояние доски в логике игры
        game_logic.board.set_board(result['board'])
        
        # Проверяем, есть ли возможный ход
        if not result.get('has_move', False):
            return {
                "success": True,
                "message": "Нет доступных ходов"
            }
        
        # Получаем координаты для клика
        move = result['move']
        
        # Релятивные координаты внутри области захвата
        click_x_rel = move['screen_coordinates']['x']
        click_y_rel = move['screen_coordinates']['y']
        
        # Добавляем отступы для получения абсолютных координат экрана
        click_x = x + click_x_rel
        click_y = y + click_y_rel
        
        # Записываем наш ход в лог
        game_logic.log_move(
            player=result['player_color'],
            move=(move['row'], move['col']),
            is_our_move=True
        )
        
        # Делаем паузу перед кликом
        time.sleep(delay)
        
        # Определяем, является ли это победным ходом
        game_logic.board.set_board(result['board'])
        # Применяем наш ход
        move_result = game_logic.board.make_move(move['row'], move['col'], result['player_color'])
        # Получаем обновленное состояние доски после хода
        new_board_state = game_logic.board.get_board()
        # Проверяем, заполнена ли доска или у обоих игроков нет ходов
        opponent_color = "white" if result['player_color'] == "black" else "black"
        empty_cells = sum(row.count("empty") for row in new_board_state)
        our_valid_moves_after = game_logic.get_valid_moves(result['player_color'], new_board_state)
        opponent_valid_moves_after = game_logic.get_valid_moves(opponent_color, new_board_state)
        
        # Подсчет фишек
        our_count = sum(row.count(result['player_color']) for row in new_board_state)
        opponent_count = sum(row.count(opponent_color) for row in new_board_state)
        
        game_end = empty_cells == 0 or (not our_valid_moves_after and not opponent_valid_moves_after)
        
        if game_end:
            # Определяем победителя
            result_message = ""
            if our_count > opponent_count:
                result_message = f"Игра завершена! Мы ({result['player_color']}) победили со счетом {our_count}:{opponent_count}"
            elif our_count < opponent_count:
                result_message = f"Игра завершена! Противник ({opponent_color}) победил со счетом {opponent_count}:{our_count}"
            else:
                result_message = f"Игра завершена! Ничья со счетом {our_count}:{opponent_count}"
            
            print(result_message)
            # Делаем паузу перед кликом
            time.sleep(delay)
            
            # Кликаем по координатам
            col_letter = chr(65 + move['col'])
            row_number = move['row'] + 1
            print(f"Победный ход {move_count+1}: {col_letter}{row_number} " + 
                f"({click_x}, {click_y}), " +
                f"оценка: {move['score']}")
            
            # Кликаем по координатам
            pyautogui.click(click_x, click_y)
            
            print("Завершаем игру после победного хода")
            return
        
        # Делаем паузу перед кликом
        time.sleep(delay)
        
        # Кликаем и возвращаем результат
        return perform_click(click_x, click_y)
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def detect_opponent_move(prev_board, curr_board, our_color):
    """
    Определяет ход противника, сравнивая предыдущее и текущее состояние доски
    
    Args:
        prev_board (list): Предыдущее состояние доски
        curr_board (list): Текущее состояние доски
        our_color (str): Наш цвет ('black' или 'white')
    
    Returns:
        dict: Информация о ходе противника {'row': int, 'col': int, 'score': 0} или None, если ход не обнаружен
    """
    opponent_color = "white" if our_color == "black" else "black"
    
    # Проверяем все клетки на доске
    changes = []
    for row in range(8):
        for col in range(8):
            # Если клетка была пустой, а стала занята противником
            if prev_board[row][col] == "empty" and curr_board[row][col] == opponent_color:
                changes.append((row, col))
    
    # Если нашли только одно изменение, это, вероятно, ход противника
    if len(changes) == 1:
        row, col = changes[0]
        print(f"Обнаружен ход противника ({opponent_color}): {chr(65 + col)}{row + 1}")
        return {
            "row": row,
            "col": col,
            "score": 0  # Не можем оценить ход противника
        }
    # Если изменений много, используем дополнительную логику
    elif len(changes) > 1:
        # Посчитаем разницу в количестве фишек
        prev_opponent_count = sum(row.count(opponent_color) for row in prev_board)
        curr_opponent_count = sum(row.count(opponent_color) for row in curr_board)
        
        # Если количество фишек увеличилось не на 1, это могло быть связано с перевернутыми фишками
        # В этом случае можно применить эвристику - выбрать позицию, в которой меньше всего перевернутых фишек вокруг
        for row, col in changes:
            # Для простоты предположим, что это был ход в первую измененную клетку
            print(f"Множественные изменения на доске, предполагаемый ход противника ({opponent_color}): {chr(65 + col)}{row + 1}")
            return {
                "row": row,
                "col": col,
                "score": 0
            }
    
    # Если изменений не найдено, возможно, был пропущен ход
    print("Ход противника не обнаружен")
    return None

def process_image(image_path):
    # Загружаем изображение
    image = cv2.imread(image_path)
    if image is None:
        raise Exception("Не удалось загрузить изображение")
    
    # Находим и выравниваем игровое поле
    board, board_rect = find_game_board(image)
    
    # Определяем цвет игрока, используя координаты доски
    player_color = detect_player_color(image, board_rect)
    
    # Сохраняем оригинал для отладки
    # cv2.imwrite('debug_original.png', board)
    
    # Преобразуем в HSV для лучшего определения цветов
    hsv = cv2.cvtColor(board, cv2.COLOR_BGR2HSV)
    
    # Создаем маски для разных цветов для отладки
    white_lower = np.array([80, 10, 180])
    white_upper = np.array([120, 50, 255])
    white_mask = cv2.inRange(hsv, white_lower, white_upper)
    black_mask = cv2.inRange(hsv, np.array([0, 0, 0]), np.array([180, 255, 60]))
    yellow_mask = cv2.inRange(hsv, np.array([25, 100, 100]), np.array([35, 255, 255]))
    
    # Сохраняем маски для отладки
    # cv2.imwrite('debug_white_mask.png', white_mask)
    # cv2.imwrite('debug_black_mask.png', black_mask)
    # cv2.imwrite('debug_yellow_mask.png', yellow_mask)
    
    # Анализируем состояние доски
    board_state = analyze_board_state(board)
    
    # Размер одной клетки для отладочной визуализации
    height, width = board.shape[:2]
    cell_size = min(height, width) // 8
    
    # Сохраняем визуализацию распознанного состояния
    debug_board = board.copy()
    for row in range(8):
        for col in range(8):
            center_x = int((col + 0.5) * cell_size)
            center_y = int((row + 0.5) * cell_size)
            color = (0, 0, 0)
            radius = int(cell_size * 0.25)
            if board_state[row][col] == "white":
                cv2.circle(debug_board, (center_x, center_y), radius, (0, 255, 0), 2)
            elif board_state[row][col] == "black":
                cv2.circle(debug_board, (center_x, center_y), radius, (0, 0, 255), 2)
            # Рисуем сетку
            cv2.rectangle(debug_board, 
                        (col * cell_size, row * cell_size), 
                        ((col + 1) * cell_size, (row + 1) * cell_size), 
                        color, 1)
    
    # cv2.imwrite('debug_recognition.png', debug_board)
    
    # Создаем результат, включающий состояние доски, цвет игрока и размеры экрана
    result = {
        "board": board_state,
        "player_color": player_color,
        "screen_size": {
            "width": image.shape[1],
            "height": image.shape[0]
        },
        "board_rect": {
            "top_left": board_rect[0].tolist(),
            "top_right": board_rect[1].tolist(),
            "bottom_right": board_rect[2].tolist(),
            "bottom_left": board_rect[3].tolist()
        }
    }
    
    # Выводим результат в JSON
    print(json.dumps(result))

def play_in_window(window_title, delay=0.5):
    """
    Полностью автономная функция для игры в Реверси
    Ищет окно по названию, анализирует игровое поле и делает ход
    Args:
        window_title (str): Название окна, в котором нужно играть
        delay (float): Задержка перед кликом в секундах
    Returns:
        dict: Результат операции
    """
    try:
        # Получаем информацию о окне
        window_result = get_window_info(window_title)
        
        if not window_result["success"]:
            return window_result
        
        # Получаем информацию о положении и размерах окна
        window_info = window_result["window_info"]
        
        # Выполняем автоматический ход
        return auto_play(window_info, delay)
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def play_in_window_with_interval(window_title, interval=3.0, delay=0.5, max_moves=None):
    """
    Автоматическая игра в Реверси с заданным интервалом
    Args:
        window_title (str): Название окна, в котором нужно играть
        interval (float): Интервал между ходами в секундах
        delay (float): Задержка перед кликом в секундах
        max_moves (int, optional): Максимальное количество ходов (None - без ограничений)
    """
    try:
        move_count = 0
        print(f"Начинаю автоматическую игру в окне '{window_title}'")
        print(f"Интервал между ходами: {interval} сек.")
        print("Нажмите Ctrl+C для остановки")
        
        while True:
            # Если задано максимальное количество ходов и оно достигнуто
            if max_moves is not None and move_count >= max_moves:
                print(f"Достигнуто максимальное количество ходов ({max_moves})")
                break
                
            # Делаем ход
            result = play_in_window(window_title, delay)
            
            # Если ход не удался
            if not result["success"]:
                print(f"Ошибка: {result.get('error', 'Неизвестная ошибка')}")
                # Подождем и попробуем снова
                time.sleep(interval)
                continue
                
            # Если есть сообщение
            if "message" in result:
                print(f"Сообщение: {result['message']}")
            
            # Если был сделан ход
            if "move" in result:
                move = result["move"]
                col_letter = chr(65 + int(move["col"]))
                row_number = int(move["row"]) + 1
                print(f"Ход {move_count+1}: {col_letter}{row_number} " + 
                      f"({move['coordinates']['x']}, {move['coordinates']['y']}), " +
                      f"оценка: {move['score']}")
                move_count += 1
            
            # Ждем указанное время перед следующим ходом
            time.sleep(interval)
            
    except KeyboardInterrupt:
        print("\nИгра остановлена пользователем")
    except Exception as e:
        print(f"Ошибка: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--get-window-info":
            if len(sys.argv) != 3:
                print("Использование: python process_image.py --get-window-info <название_окна>")
                sys.exit(1)
            
            try:
                window_title = sys.argv[2]
                result = get_window_info(window_title)
                print(json.dumps(result))
            except Exception as e:
                print(json.dumps({
                    "success": False,
                    "error": str(e)
                }))
                sys.exit(1)
        elif sys.argv[1] == "--play-in-window":
            if len(sys.argv) < 3:
                print("Использование: python process_image.py --play-in-window <название_окна> [delay] [border_top] [border_left] [border_bottom]")
                sys.exit(1)
            
            try:
                window_title = sys.argv[2]
                
                # Если указан аргумент задержки, используем его
                delay = 0.5
                if len(sys.argv) > 3:
                    delay = float(sys.argv[3])
                
                # Если указаны границы, используем их
                border_top = 45
                border_left = 10
                border_bottom = 70
                
                if len(sys.argv) > 4:
                    border_top = int(sys.argv[4])
                if len(sys.argv) > 5:
                    border_left = int(sys.argv[5])
                if len(sys.argv) > 6:
                    border_bottom = int(sys.argv[6])
                
                # Получаем информацию о окне с указанными границами
                window_result = get_window_info(window_title, border_top, border_left, border_bottom)
                
                if not window_result["success"]:
                    print(json.dumps(window_result))
                    sys.exit(1)
                
                # Выполняем автоматический ход в окне
                result = auto_play(window_result["window_info"], delay)
                
                # Выводим результат в JSON
                print(json.dumps(result))
                
            except Exception as e:
                print(json.dumps({
                    "success": False,
                    "error": str(e)
                }))
                sys.exit(1)
        elif sys.argv[1] == "--auto-play-interval":
            if len(sys.argv) < 3:
                print("Использование: python process_image.py --auto-play-interval <название_окна> [interval] [delay] [max_moves] [border_top] [border_left] [border_bottom]")
                sys.exit(1)
            
            try:
                window_title = sys.argv[2]
                
                # Интервал между ходами (в секундах)
                interval = 3.0
                if len(sys.argv) > 3:
                    interval = float(sys.argv[3])
                
                # Задержка перед кликом (в секундах)
                delay = 0.5
                if len(sys.argv) > 4:
                    delay = float(sys.argv[4])
                
                # Максимальное количество ходов
                max_moves = None
                if len(sys.argv) > 5:
                    max_moves_value = int(sys.argv[5])
                    # Если значение 0, то считаем, что ограничений нет
                    if max_moves_value > 0:
                        max_moves = max_moves_value
                
                # Границы окна
                border_top = 45
                border_left = 10
                border_bottom = 70
                
                if len(sys.argv) > 6:
                    border_top = int(sys.argv[6])
                if len(sys.argv) > 7:
                    border_left = int(sys.argv[7])
                if len(sys.argv) > 8:
                    border_bottom = int(sys.argv[8])
                
                # Модифицируем функцию play_in_window_with_interval для использования границ
                def play_with_borders():
                    try:
                        move_count = 0
                        # Флаг для отслеживания проверки первого хода
                        first_move_checked = False
                        
                        print(f"Начинаю автоматическую игру в окне '{window_title}'")
                        print(f"Интервал между ходами: {interval} сек.")
                        print(f"Границы окна: верх={border_top}, лево={border_left}, низ={border_bottom}")
                        print("Нажмите Ctrl+C для остановки")
                        
                        # Определяем цвет игрока один раз в начале игры
                        window_result = get_window_info(window_title, border_top, border_left, border_bottom)
                        if not window_result["success"]:
                            print(f"Ошибка: {window_result.get('error', 'Не удалось получить информацию об окне')}")
                            return

                        # Захватываем экран для определения цвета
                        initial_capture = capture_screen_region(
                            window_result["window_info"]['x'],
                            window_result["window_info"]['y'],
                            window_result["window_info"]['width'],
                            window_result["window_info"]['height']
                        )
                        
                        if not initial_capture["success"]:
                            print(f"Ошибка при начальном анализе: {initial_capture.get('error', 'Неизвестная ошибка')}")
                            return
                            
                        # Запоминаем цвет игрока
                        player_color = initial_capture["player_color"]
                        print(f"Определен цвет игрока: {player_color} (будет использоваться для всей игры)")
                        
                        # Создаем объект логики игры
                        global game_logic
                        if 'game_logic' not in globals() or game_logic is None:
                            game_logic = ReversiLogic()
                        
                        # Сохраняем текущее состояние доски
                        game_logic.last_board_state = initial_capture['board']
                        game_logic.board.set_board(initial_capture['board'])
                        
                        while True:
                            # Если задано максимальное количество ходов и оно достигнуто
                            if max_moves is not None and move_count >= max_moves:
                                print(f"Достигнуто максимальное количество ходов ({max_moves})")
                                break
                                
                            # Получаем информацию о окне с указанными границами
                            window_result = get_window_info(window_title, border_top, border_left, border_bottom)
                            
                            if not window_result["success"]:
                                print(f"Ошибка: {window_result.get('error', 'Не удалось получить информацию об окне')}")
                                time.sleep(interval)
                                continue
                            
                            # Захватываем и анализируем экран
                            x = window_result["window_info"]["x"]
                            y = window_result["window_info"]["y"]
                            width = window_result["window_info"]["width"]
                            height = window_result["window_info"]["height"]
                            
                            # Захватываем область экрана
                            screenshot = pyautogui.screenshot(region=(x, y, width, height))
                            image = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
                            
                            # Находим и выравниваем игровое поле
                            board, board_rect = find_game_board(image)
                            
                            # Анализируем состояние доски (используем ранее определенный цвет)
                            board_state = analyze_board_state(board)
                            
                            # Проверяем, сделал ли противник ход
                            opponent_move = detect_opponent_move(game_logic.last_board_state, board_state, player_color)
                            
                            # Если нашли ход противника, записываем его в лог и делаем свой ход
                            if opponent_move:
                                # Обновляем состояние доски в логике игры
                                game_logic.board.set_board(board_state)
                                
                                # Получаем цвет противника
                                opponent_color = "white" if player_color == "black" else "black"
                                
                                # Записываем ход противника в лог
                                game_logic.log_move(
                                    player=opponent_color,
                                    move=(opponent_move["row"], opponent_move["col"]),
                                    is_our_move=False
                                )
                                
                                # Сохраняем текущее состояние доски для следующего хода
                                game_logic.last_board_state = board_state
                                
                                # Обновляем состояние доски в логике игры
                                game_logic.board.set_board(board_state)
                                
                                # Находим лучший ход
                                best_move, score = game_logic.get_best_move(player_color)
                                
                                if best_move:
                                    row, col = best_move
                                    # Вычисляем координаты клика
                                    click_coords = calculate_click_coordinates(board_rect, row, col)
                                    
                                    # Записываем наш ход в лог
                                    game_logic.log_move(
                                        player=player_color,
                                        move=(row, col),
                                        is_our_move=True
                                    )
                                    
                                    # Абсолютные координаты для клика
                                    click_x = x + click_coords["x"]
                                    click_y = y + click_coords["y"]
                                    
                                    # Делаем паузу перед кликом
                                    time.sleep(delay)
                                    
                                    # Определяем, является ли это победным ходом
                                    game_logic.board.set_board(board_state)
                                    # Применяем наш ход
                                    move_result = game_logic.board.make_move(row, col, player_color)
                                    # Получаем обновленное состояние доски после хода
                                    new_board_state = game_logic.board.get_board()
                                    # Проверяем, заполнена ли доска или у обоих игроков нет ходов
                                    opponent_color = "white" if player_color == "black" else "black"
                                    empty_cells = sum(row.count("empty") for row in new_board_state)
                                    our_valid_moves_after = game_logic.get_valid_moves(player_color, new_board_state)
                                    opponent_valid_moves_after = game_logic.get_valid_moves(opponent_color, new_board_state)
                                    
                                    # Подсчет фишек
                                    our_count = sum(row.count(player_color) for row in new_board_state)
                                    opponent_count = sum(row.count(opponent_color) for row in new_board_state)
                                    
                                    game_end = empty_cells == 0 or (not our_valid_moves_after and not opponent_valid_moves_after)
                                    
                                    if game_end:
                                        # Определяем победителя
                                        result_message = ""
                                        if our_count > opponent_count:
                                            result_message = f"Игра завершена! Мы ({player_color}) победили со счетом {our_count}:{opponent_count}"
                                        elif our_count < opponent_count:
                                            result_message = f"Игра завершена! Противник ({opponent_color}) победил со счетом {opponent_count}:{our_count}"
                                        else:
                                            result_message = f"Игра завершена! Ничья со счетом {our_count}:{opponent_count}"
                                        
                                        print(result_message)
                                        # Делаем паузу перед кликом
                                        time.sleep(delay)
                                        
                                        # Кликаем по координатам
                                        col_letter = chr(65 + col)
                                        row_number = row + 1
                                        print(f"Победный ход {move_count+1}: {col_letter}{row_number} " + 
                                            f"({click_x}, {click_y}), " +
                                            f"оценка: {score}")
                                        
                                        # Кликаем по координатам
                                        pyautogui.click(click_x, click_y)
                                        
                                        print("Завершаем игру после победного хода")
                                        return
                                    
                                    # Делаем паузу перед кликом
                                    time.sleep(delay)
                                    
                                    # Кликаем по координатам
                                    pyautogui.click(click_x, click_y)
                                    
                                    move_count += 1
                                else:
                                    # Дополнительная проверка доступных ходов
                                    valid_moves = game_logic.get_valid_moves(player_color)
                                    if valid_moves:
                                        # Если есть доступные ходы, но алгоритм не смог найти лучший ход,
                                        # выбираем первый доступный ход
                                        row, col = valid_moves[0]
                                        click_coords = calculate_click_coordinates(board_rect, row, col)
                                        
                                        # Абсолютные координаты для клика
                                        click_x = x + click_coords["x"]
                                        click_y = y + click_coords["y"]
                                        
                                        # Записываем ход в лог
                                        game_logic.log_move(
                                            player=player_color,
                                            move=(row, col),
                                            is_our_move=True
                                        )
                                        
                                        # Делаем паузу перед кликом
                                        time.sleep(delay)
                                        
                                        # Выполняем клик
                                        col_letter = chr(65 + col)
                                        row_number = row + 1
                                        print(f"Запасной ход {move_count+1}: {col_letter}{row_number} " + 
                                            f"({click_x}, {click_y})")
                                        
                                        # Кликаем по координатам
                                        pyautogui.click(click_x, click_y)
                                        
                                        move_count += 1
                                        print(f"Применен запасной вариант: найдено {len(valid_moves)} доступных ходов, выбран ход ({row},{col})")
                                    else:
                                        print(f"Действительно нет доступных ходов для {player_color}")
                                        print("Сообщение: Нет доступных ходов")
                            else:
                                # Сравниваем доску с предыдущей для первого хода
                                if move_count == 0 and not first_move_checked and game_logic.last_board_state == board_state:
                                    # Если это первый ход и доска не изменилась, это значит, что мы ходим первыми
                                    print("Обнаружено, что мы ходим первыми")
                                    first_move_checked = True
                                    
                                    # Находим лучший ход
                                    best_move, score = game_logic.get_best_move(player_color)
                                    
                                    if best_move:
                                        row, col = best_move
                                        click_coords = calculate_click_coordinates(board_rect, row, col)
                                        
                                        # Записываем наш ход в лог
                                        game_logic.log_move(
                                            player=player_color,
                                            move=(row, col),
                                            is_our_move=True
                                        )
                                        
                                        # Абсолютные координаты для клика
                                        click_x = x + click_coords["x"]
                                        click_y = y + click_coords["y"]
                                        
                                        # Делаем паузу перед кликом
                                        time.sleep(delay)
                                        
                                        # Выполняем клик
                                        col_letter = chr(65 + col)
                                        row_number = row + 1
                                        print(f"Первый ход {move_count+1}: {col_letter}{row_number} " + 
                                            f"({click_x}, {click_y}), " +
                                            f"оценка: {score}")
                                        
                                        # Кликаем по координатам
                                        pyautogui.click(click_x, click_y)
                                        
                                        move_count += 1
                                        
                                        # Сохраняем текущее состояние доски
                                        game_logic.last_board_state = board_state
                                        game_logic.board.set_board(board_state)
                                    else:
                                        print("Не удалось найти ход, хотя мы должны ходить первыми")
                                else:
                                    # Если это не первый ход или мы уже проверили, устанавливаем флаг
                                    first_move_checked = True
                                    
                                    # Проверяем, может быть у противника нет ходов
                                    # Для этого проверим, есть ли ходы у противника на текущей доске
                                    opponent_color = "white" if player_color == "black" else "black"
                                    game_logic.board.set_board(board_state)
                                    opponent_valid_moves = game_logic.get_valid_moves(opponent_color)
                                    
                                    # Если у противника нет ходов, но у нас есть, значит мы должны ходить снова
                                    if not opponent_valid_moves:
                                        our_valid_moves = game_logic.get_valid_moves(player_color)
                                        if our_valid_moves:
                                            print(f"Обнаружено, что у противника ({opponent_color}) нет ходов, но у нас ({player_color}) ходы есть. Ходим снова.")
                                            
                                            # Находим лучший ход
                                            best_move, score = game_logic.get_best_move(player_color)
                                            
                                            if best_move:
                                                row, col = best_move
                                                click_coords = calculate_click_coordinates(board_rect, row, col)
                                                
                                                # Записываем наш ход в лог
                                                game_logic.log_move(
                                                    player=player_color,
                                                    move=(row, col),
                                                    is_our_move=True
                                                )
                                                
                                                # Абсолютные координаты для клика
                                                click_x = x + click_coords["x"]
                                                click_y = y + click_coords["y"]
                                                
                                                # Делаем паузу перед кликом
                                                time.sleep(delay)
                                                
                                                # Выполняем клик
                                                col_letter = chr(65 + col)
                                                row_number = row + 1
                                                print(f"Повторный ход {move_count+1}: {col_letter}{row_number} " + 
                                                    f"({click_x}, {click_y}), " +
                                                    f"оценка: {score}")
                                                
                                                # Кликаем по координатам
                                                pyautogui.click(click_x, click_y)
                                                
                                                move_count += 1
                                                
                                                # Сохраняем текущее состояние доски
                                                game_logic.last_board_state = board_state
                                            else:
                                                print("Странно: доступные ходы есть, но алгоритм не нашел лучший. Используем первый доступный.")
                                                row, col = our_valid_moves[0]
                                                click_coords = calculate_click_coordinates(board_rect, row, col)
                                                
                                                # Записываем наш ход в лог
                                                game_logic.log_move(
                                                    player=player_color,
                                                    move=(row, col),
                                                    is_our_move=True
                                                )
                                                
                                                # Абсолютные координаты для клика
                                                click_x = x + click_coords["x"]
                                                click_y = y + click_coords["y"]
                                                
                                                # Делаем паузу перед кликом
                                                time.sleep(delay)
                                                
                                                # Выполняем клик
                                                col_letter = chr(65 + col)
                                                row_number = row + 1
                                                print(f"Запасной повторный ход {move_count+1}: {col_letter}{row_number} " + 
                                                    f"({click_x}, {click_y})")
                                                
                                                # Кликаем по координатам
                                                pyautogui.click(click_x, click_y)
                                                
                                                move_count += 1
                                                
                                                # Сохраняем текущее состояние доски
                                                game_logic.last_board_state = board_state
                                        else:
                                            print(f"У противника ({opponent_color}) нет ходов, но и у нас ({player_color}) тоже нет. Игра близится к завершению.")
                                    else:
                                        # Ход противника не обнаружен - возможно, он еще ходит
                                        print("Ход противника не обнаружен, ждем следующего цикла")
                                        # Просто ждем до следующей проверки, ничего не делаем
                            
                            # Ждем указанное время перед следующим ходом
                            time.sleep(interval)
                            
                    except KeyboardInterrupt:
                        print("\nИгра остановлена пользователем")
                    except Exception as e:
                        print(f"Ошибка: {str(e)}")
                        import traceback
                        traceback.print_exc()
                
                # Запускаем игру с указанными границами
                play_with_borders()
                
            except Exception as e:
                print(f"Ошибка: {str(e)}")
                sys.exit(1)
        elif sys.argv[1] == "--capture":
            if len(sys.argv) != 6:
                print("Использование для захвата экрана: python process_image.py --capture <x> <y> <width> <height>")
                sys.exit(1)
            
            try:
                x = int(sys.argv[2])
                y = int(sys.argv[3])
                width = int(sys.argv[4])
                height = int(sys.argv[5])
                
                # Захватываем и анализируем экран
                result = capture_screen_region(x, y, width, height)
                
                # Выводим результат в JSON
                print(json.dumps(result))
                
            except Exception as e:
                print(f"Ошибка при захвате экрана: {str(e)}", file=sys.stderr)
                sys.exit(1)
        elif sys.argv[1] == "--click":
            if len(sys.argv) != 4:
                print("Использование для клика: python process_image.py --click <x> <y>")
                sys.exit(1)
            
            try:
                x = int(sys.argv[2])
                y = int(sys.argv[3])
                
                # Выполняем клик
                result = perform_click(x, y)
                
                # Выводим результат в JSON
                print(json.dumps(result))
                
            except Exception as e:
                print(f"Ошибка при выполнении клика: {str(e)}", file=sys.stderr)
                sys.exit(1)
        elif sys.argv[1] == "--auto-play":
            if len(sys.argv) < 6:
                print("Использование для автоматической игры: python process_image.py --auto-play <x> <y> <width> <height> [delay]")
                sys.exit(1)
            
            try:
                x = int(sys.argv[2])
                y = int(sys.argv[3])
                width = int(sys.argv[4])
                height = int(sys.argv[5])
                
                # Если указан аргумент задержки, используем его
                delay = 0.5
                if len(sys.argv) > 6:
                    delay = float(sys.argv[6])
                
                window_info = {
                    'x': x,
                    'y': y,
                    'width': width,
                    'height': height
                }
                
                # Выполняем автоматический ход
                result = auto_play(window_info, delay)
                
                # Выводим результат в JSON
                print(json.dumps(result))
                
            except Exception as e:
                print(f"Ошибка при автоматической игре: {str(e)}", file=sys.stderr)
                sys.exit(1)
    else:
        if len(sys.argv) != 2:
            print("Использование: python process_image.py <путь_к_изображению>")
            sys.exit(1)
        
        try:
            process_image(sys.argv[1])
        except Exception as e:
            print(f"Ошибка: {str(e)}", file=sys.stderr)
            sys.exit(1)
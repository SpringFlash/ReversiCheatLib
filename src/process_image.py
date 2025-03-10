import cv2
import numpy as np
import sys
import json

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
    score_x = int(top_right[0] - board_width * 0.27)  # Отступ 5% от правого края поля
    score_y = int(top_right[1] - board_width * 0.3)  # Центрируем по вертикали относительно верха поля
    
    # Проверяем границы изображения
    height, width = image.shape[:2]
    # score_x = min(score_x, width - score_width)
    # score_y = max(0, min(score_y, height - score_height))
    
    # Вырезаем область счета
    score_region = image[
        score_y:score_y + score_height,
        score_x:score_x + score_width
    ]
    
    # Сохраняем область для отладки
    cv2.imwrite('debug_score_region.png', score_region)
    
    # Преобразуем в HSV для определения цвета
    hsv = cv2.cvtColor(score_region, cv2.COLOR_BGR2HSV)
    
    # Маски для определения цвета фона счета
    white_mask = cv2.inRange(hsv, np.array([0, 0, 180]), np.array([180, 30, 255]))
    black_mask = cv2.inRange(hsv, np.array([0, 0, 0]), np.array([180, 255, 60]))
    
    cv2.imwrite('debug_white_mask_score.png', white_mask)
    cv2.imwrite('debug_black_mask_score.png', black_mask)
    
    # Подсчитываем пиксели каждого цвета
    white_pixels = cv2.countNonZero(white_mask)
    black_pixels = cv2.countNonZero(black_mask)
    
    # Определяем цвет игрока (противоположный цвету фона счета)
    total_pixels = score_region.shape[0] * score_region.shape[1]
    threshold = total_pixels * 0.3
    
    if white_pixels > threshold:
        return "white"  # Если фон белый, игрок играет черными
    elif black_pixels > threshold:
        return "black"  # Если фон темный, игрок играет белыми
    else:
        return None  # Не удалось определить

def find_game_board(image):
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
    
    # Ищем контуры
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Сохраняем для отладки
    debug_contours = image.copy()
    cv2.drawContours(debug_contours, contours, -1, (0, 255, 0), 2)
    cv2.imwrite('debug_contours.png', debug_contours)
    
    # Ищем самый большой прямоугольный контур
    max_area = 0
    game_board_rect = None
    
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 1000:  # Фильтруем маленькие контуры
            peri = cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
            
            # Ищем прямоугольник
            if len(approx) == 4 and area > max_area:
                max_area = area
                game_board_rect = approx
    
    if game_board_rect is None:
        raise Exception("Не удалось найти игровое поле")
    
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
    
    return warped, rect

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
    cv2.imwrite('debug_original.png', board)
    
    # Преобразуем в HSV для лучшего определения цветов
    hsv = cv2.cvtColor(board, cv2.COLOR_BGR2HSV)
    
    # Создаем маски для разных цветов
    # Белые фишки (светло-голубые)
    white_lower = np.array([80, 10, 180])
    white_upper = np.array([120, 50, 255])
    white_mask = cv2.inRange(hsv, white_lower, white_upper)
    
    # Черные фишки
    black_mask = cv2.inRange(hsv, np.array([0, 0, 0]), np.array([180, 255, 60]))
    
    # Желтая подсветка
    yellow_mask = cv2.inRange(hsv, np.array([25, 100, 100]), np.array([35, 255, 255]))
    
    # Сохраняем маски для отладки
    cv2.imwrite('debug_white_mask.png', white_mask)
    cv2.imwrite('debug_black_mask.png', black_mask)
    cv2.imwrite('debug_yellow_mask.png', yellow_mask)
    
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
            yellow_pixels = cv2.countNonZero(yellow_mask[y1:y2, x1:x2])
            
            # Определяем содержимое клетки
            total_area = (y2 - y1) * (x2 - x1)
            threshold = total_area * 0.2
            
            if white_pixels > threshold:
                board_state[row][col] = "white"
            elif black_pixels > threshold:
                board_state[row][col] = "black"
            else:
                board_state[row][col] = "empty"
    
    # Сохраняем визуализацию распознанного состояния
    debug_board = board.copy()
    for row in range(8):
        for col in range(8):
            center_x = int((col + 0.5) * cell_size)
            center_y = int((row + 0.5) * cell_size)
            color = (0, 0, 0)
            if board_state[row][col] == "white":
                cv2.circle(debug_board, (center_x, center_y), radius, (0, 255, 0), 2)
            elif board_state[row][col] == "black":
                cv2.circle(debug_board, (center_x, center_y), radius, (0, 0, 255), 2)
            # Рисуем сетку
            cv2.rectangle(debug_board, 
                        (col * cell_size, row * cell_size), 
                        ((col + 1) * cell_size, (row + 1) * cell_size), 
                        color, 1)
    
    cv2.imwrite('debug_recognition.png', debug_board)
    
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

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Использование: python process_image.py <путь_к_изображению>")
        sys.exit(1)
    
    try:
        process_image(sys.argv[1])
    except Exception as e:
        print(f"Ошибка: {str(e)}", file=sys.stderr)
        sys.exit(1)
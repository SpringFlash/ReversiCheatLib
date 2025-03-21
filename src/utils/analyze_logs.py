"""
Модуль для анализа логов игры Реверси и оценки эффективности алгоритмов
"""
import os
import json
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import MaxNLocator
from collections import defaultdict

def load_game_logs(logs_dir="logs"):
    """
    Загружает все логи игр из указанной директории
    
    Args:
        logs_dir (str): Путь к директории с логами
        
    Returns:
        list: Список логов игр
    """
    game_logs = []
    
    # Проверяем, существует ли директория с логами
    if not os.path.exists(logs_dir):
        print(f"Директория {logs_dir} не найдена")
        return game_logs
    
    # Получаем список файлов логов
    log_files = [f for f in os.listdir(logs_dir) if f.endswith('.json')]
    
    # Загружаем каждый файл
    for log_file in log_files:
        try:
            with open(os.path.join(logs_dir, log_file), 'r', encoding='utf-8') as f:
                game_log = json.load(f)
                game_logs.append({
                    'file': log_file,
                    'log': game_log
                })
        except Exception as e:
            print(f"Ошибка при загрузке файла {log_file}: {str(e)}")
    
    return game_logs

def analyze_algorithm_performance(game_logs):
    """
    Анализирует эффективность алгоритмов по логам игр
    
    Args:
        game_logs (list): Список логов игр
    
    Returns:
        dict: Статистика по алгоритмам
    """
    # Статистика по алгоритмам
    algorithm_stats = {
        'Minimax': {'total_moves': 0, 'total_score': 0, 'moves_by_phase': {'early': 0, 'middle': 0, 'late': 0}},
        'NegaScout': {'total_moves': 0, 'total_score': 0, 'moves_by_phase': {'early': 0, 'middle': 0, 'late': 0}},
        'MCTS': {'total_moves': 0, 'total_score': 0, 'moves_by_phase': {'early': 0, 'middle': 0, 'late': 0}}
    }
    
    # Для каждой игры
    for game in game_logs:
        # Для каждого хода в игре
        for move in game['log']:
            # Учитываем только наши ходы
            if move.get('is_our_move', True) and 'algorithm' in move and 'score' in move and move['score'] is not None:
                algorithm = move['algorithm']
                score = move['score']
                phase = move['game_phase']
                
                # Обновляем статистику
                algorithm_stats[algorithm]['total_moves'] += 1
                algorithm_stats[algorithm]['total_score'] += score
                algorithm_stats[algorithm]['moves_by_phase'][phase] += 1
    
    # Вычисляем средний счет для каждого алгоритма
    for algorithm in algorithm_stats:
        if algorithm_stats[algorithm]['total_moves'] > 0:
            algorithm_stats[algorithm]['average_score'] = algorithm_stats[algorithm]['total_score'] / algorithm_stats[algorithm]['total_moves']
        else:
            algorithm_stats[algorithm]['average_score'] = 0
    
    return algorithm_stats

def analyze_game_progress(game_logs):
    """
    Анализирует прогресс игры по соотношению фишек
    
    Args:
        game_logs (list): Список логов игр
    
    Returns:
        list: Статистика по играм
    """
    game_progress = []
    
    # Для каждой игры
    for game in game_logs:
        game_data = {
            'file': game['file'],
            'moves': [],
            'our_pieces': [],
            'opponent_pieces': [],
            'our_color': None
        }
        
        # Определяем наш цвет из первого хода
        for move in game['log']:
            if move.get('is_our_move', True):
                game_data['our_color'] = move['player']
                break
        
        # Если не нашли наш цвет, пропускаем игру
        if game_data['our_color'] is None:
            continue
        
        # Цвет противника
        opponent_color = 'white' if game_data['our_color'] == 'black' else 'black'
        
        # Для каждого хода в игре
        for move in game['log']:
            if 'pieces' in move and 'move_number' in move:
                game_data['moves'].append(move['move_number'])
                game_data['our_pieces'].append(move['pieces'].get(game_data['our_color'], 0))
                game_data['opponent_pieces'].append(move['pieces'].get(opponent_color, 0))
        
        game_progress.append(game_data)
    
    return game_progress

def generate_performance_plots(algorithm_stats, game_progress):
    """
    Генерирует графики для анализа производительности алгоритмов
    
    Args:
        algorithm_stats (dict): Статистика по алгоритмам
        game_progress (list): Статистика по прогрессу игр
    """
    # График средней оценки по алгоритмам
    plt.figure(figsize=(10, 6))
    algorithms = []
    avg_scores = []
    
    for algorithm, stats in algorithm_stats.items():
        if stats['total_moves'] > 0:
            algorithms.append(algorithm)
            avg_scores.append(stats['average_score'])
    
    plt.bar(algorithms, avg_scores)
    plt.title('Средняя оценка хода по алгоритмам')
    plt.ylabel('Средняя оценка')
    plt.xlabel('Алгоритм')
    plt.savefig('algorithm_avg_score.png')
    plt.close()
    
    # График использования алгоритмов по фазам игры
    plt.figure(figsize=(12, 8))
    
    phases = ['early', 'middle', 'late']
    x = np.arange(len(phases))
    width = 0.25
    
    # Для каждого алгоритма
    for i, (algorithm, stats) in enumerate(algorithm_stats.items()):
        moves_by_phase = [stats['moves_by_phase'][phase] for phase in phases]
        plt.bar(x + i*width, moves_by_phase, width, label=algorithm)
    
    plt.title('Использование алгоритмов по фазам игры')
    plt.ylabel('Количество ходов')
    plt.xlabel('Фаза игры')
    plt.xticks(x + width, phases)
    plt.legend()
    plt.savefig('algorithm_usage_by_phase.png')
    plt.close()
    
    # График прогресса игры (соотношение фишек)
    for i, game in enumerate(game_progress):
        plt.figure(figsize=(12, 6))
        plt.plot(game['moves'], game['our_pieces'], 'b-', label='Наши фишки')
        plt.plot(game['moves'], game['opponent_pieces'], 'r-', label='Фишки противника')
        plt.title(f'Прогресс игры {game["file"]}')
        plt.ylabel('Количество фишек')
        plt.xlabel('Номер хода')
        plt.grid(True)
        plt.legend()
        plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))
        plt.savefig(f'game_progress_{i+1}.png')
        plt.close()

def main():
    """
    Основная функция для анализа логов
    """
    # Загружаем логи игр
    game_logs = load_game_logs()
    
    # Если логов нет, выходим
    if not game_logs:
        print("Логи игр не найдены")
        return
    
    print(f"Загружено {len(game_logs)} игр")
    
    # Анализируем производительность алгоритмов
    algorithm_stats = analyze_algorithm_performance(game_logs)
    
    # Анализируем прогресс игр
    game_progress = analyze_game_progress(game_logs)
    
    # Выводим статистику по алгоритмам
    print("\nСтатистика по алгоритмам:")
    for algorithm, stats in algorithm_stats.items():
        print(f"\n{algorithm}:")
        print(f"  Всего ходов: {stats['total_moves']}")
        print(f"  Средняя оценка: {stats.get('average_score', 0):.2f}")
        print("  Ходы по фазам игры:")
        for phase, count in stats['moves_by_phase'].items():
            print(f"    {phase}: {count}")
    
    # Генерируем графики
    generate_performance_plots(algorithm_stats, game_progress)
    print("\nГрафики сохранены в текущей директории")

if __name__ == "__main__":
    main() 
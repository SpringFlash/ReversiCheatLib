#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Главный файл запуска игры Реверси.
Запустите этот файл для старта игры:
python src/run.py
"""

import sys
import os

# Добавляем корневую директорию проекта в путь поиска модулей
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# Импортируем необходимые модули
from src.ui.play_reversi import main as play_reversi

if __name__ == "__main__":
    # Запускаем приложение
    play_reversi() 
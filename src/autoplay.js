#!/usr/bin/env node

/**
 * Автоматизация игры в реверси
 * Этот скрипт делает следующее:
 * 1. Делает скриншот активного окна
 * 2. Анализирует скриншот с помощью ReversiBot
 * 3. Выполняет клик по координатам лучшего хода
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const screenshot = require('screenshot-desktop');
let activeWin;
const ReversiBot = require('./ReversiBot');

// Создаем директорию для временных файлов
const tempDir = path.join(__dirname, '..', 'temp');
if (!fs.existsSync(tempDir)) {
  fs.mkdirSync(tempDir, { recursive: true });
}

// Инициализируем бота
const bot = new ReversiBot();

/**
 * Делает скриншот активного окна
 * @returns {Promise<string>} Путь к файлу скриншота
 */
async function captureActiveWindow() {
  try {
    // Проверяем, загружен ли модуль activeWin
    if (!activeWin) {
      const module = await import('active-win');
      activeWin = module.default;
    }
    
    // Получаем информацию об активном окне
    const activeWindow = await activeWin();
    if (!activeWindow) {
      throw new Error('Не удалось получить информацию об активном окне');
    }

    console.log(`Активное окно: ${activeWindow.title}`);
    
    // Делаем скриншот всего экрана
    const screenshotPath = path.join(tempDir, `screenshot_${Date.now()}.png`);
    await screenshot({ filename: screenshotPath });
    
    console.log(`Скриншот сохранен: ${screenshotPath}`);
    return screenshotPath;
  } catch (error) {
    console.error('Ошибка при создании скриншота:', error);
    throw error;
  }
}

/**
 * Выполняет клик по указанным координатам в активном окне
 * @param {number} x X-координата
 * @param {number} y Y-координата
 */
function clickAt(x, y) {
  try {
    console.log(`Выполняю клик по координатам: ${x}, ${y}`);
    
    // Используем xdotool для клика
    execSync(`xdotool mousemove ${x} ${y} click 1`);
    
    console.log('Клик выполнен успешно');
  } catch (error) {
    console.error('Ошибка при выполнении клика:', error);
    throw error;
  }
}

/**
 * Основная функция автоматизации
 */
async function autoplay() {
  try {
    // Делаем скриншот активного окна
    const screenshotPath = await captureActiveWindow();
    
    // Анализируем скриншот
    console.log('Анализирую скриншот...');
    const result = await bot.analyzeScreenshotForAPI(screenshotPath);
    
    // Проверяем результат анализа
    if (!result.success) {
      console.error('Ошибка при анализе скриншота:', result.error);
      return;
    }
    
    if (!result.hasMove) {
      console.log('Нет доступных ходов');
      return;
    }
    
    // Получаем координаты лучшего хода
    const { x, y } = result.move.screen_coordinates;
    console.log(`Лучший ход: ${result.move.row}${result.move.col} (${x}, ${y})`);
    
    // Выполняем клик
    clickAt(Math.round(x), Math.round(y));
    
    // Удаляем временный файл скриншота
    fs.unlinkSync(screenshotPath);
    console.log('Временный файл удален');
  } catch (error) {
    console.error('Ошибка при автоматизации:', error);
  }
}

// Запускаем автоматизацию, если скрипт запущен напрямую
if (require.main === module) {
  autoplay();
}

module.exports = {
  autoplay,
  captureActiveWindow,
  clickAt
}; 
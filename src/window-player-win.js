#!/usr/bin/env node

/**
 * Автоматический игрок в реверси для Windows
 * Позволяет указать имя окна, в котором нужно делать ходы
 */

const fs = require('fs');
const path = require('path');
const screenshot = require('screenshot-desktop');
const robot = require('robotjs');
const readline = require('readline');
const { exec } = require('child_process');
const ReversiBot = require('./ReversiBot');

// Создаем интерфейс для чтения с консоли
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

// Создаем директорию для временных файлов
const tempDir = path.join(__dirname, '..', 'temp');
if (!fs.existsSync(tempDir)) {
  fs.mkdirSync(tempDir, { recursive: true });
}

// Настройки по умолчанию
let targetWindowTitle = '';
let interval = 3000; // Интервал между ходами в миллисекундах
let isRunning = false;
let intervalId = null;
let lastCapturedWindowInfo = null; // Информация о последнем захваченном окне

// Инициализируем бота
const bot = new ReversiBot();

/**
 * Получает список всех окон
 * @returns {Promise<Array<{title: string, handle: string}>>} Массив объектов с названиями и хендлами окон
 */
function getAllWindows() {
  return new Promise((resolve, reject) => {
    // Используем PowerShell для получения списка окон
    const command = `powershell -command "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.Screen]::AllScreens | ForEach-Object { $_.Bounds } | Format-Table -AutoSize"`;
    
    exec(command, (error, stdout, stderr) => {
      if (error) {
        console.error(`Ошибка при получении списка окон: ${error.message}`);
        resolve([]);
        return;
      }
      
      if (stderr) {
        console.error(`Ошибка при получении списка окон: ${stderr}`);
        resolve([]);
        return;
      }
      
      // Для Windows мы просто получаем размеры экранов, так как нет простого способа получить список окон
      // Вместо этого мы будем использовать полноэкранный скриншот
      const screens = stdout.trim().split('\n').slice(2).map(line => {
        const parts = line.trim().split(/\s+/);
        return {
          title: `Screen ${parts[0]}x${parts[1]}`,
          handle: `${parts[0]},${parts[1]},${parts[2]},${parts[3]}`
        };
      });
      
      resolve(screens);
    });
  });
}

/**
 * Выводит список всех экранов
 */
async function listAllScreens() {
  const screens = await getAllWindows();
  
  if (screens.length === 0) {
    console.log('Не найдено ни одного экрана');
    return;
  }
  
  console.log('\nСписок доступных экранов:');
  console.log('Название\t\tРазмеры');
  console.log('--------------------------------------------------');
  
  screens.forEach(screen => {
    console.log(`${screen.title}\t\t${screen.handle}`);
  });
  
  console.log('--------------------------------------------------');
  console.log(`Всего экранов: ${screens.length}`);
  console.log('Для выбора экрана введите: screen <номер экрана>\n');
}

/**
 * Делает скриншот экрана
 * @returns {Promise<string>} Путь к файлу скриншота
 */
async function captureScreen() {
  try {
    // Создаем путь для скриншота
    const screenshotPath = path.join(tempDir, `screenshot_${Date.now()}.png`);
    
    // Делаем скриншот всего экрана
    await screenshot({ filename: screenshotPath });
    console.log(`Скриншот экрана сохранен: ${screenshotPath}`);
    
    // Получаем размер экрана
    const screenSize = robot.getScreenSize();
    lastCapturedWindowInfo = {
      x: 0,
      y: 0,
      width: screenSize.width,
      height: screenSize.height
    };
    
    return screenshotPath;
  } catch (error) {
    console.error('Ошибка при создании скриншота:', error);
    throw error;
  }
}

/**
 * Выполняет клик по указанным координатам
 * @param {number} x X-координата относительно экрана
 * @param {number} y Y-координата относительно экрана
 */
function clickAt(x, y) {
  try {
    console.log(`Выполняю клик по координатам: ${x}, ${y}`);
    
    // Перемещаем мышь и выполняем клик
    robot.moveMouse(Math.round(x), Math.round(y));
    robot.mouseClick();
    
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
    // Делаем скриншот экрана
    const screenshotPath = await captureScreen();
    
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

/**
 * Запускает автоматическую игру с заданным интервалом
 */
function startAutoplay() {
  if (isRunning) {
    console.log('Автоматическая игра уже запущена');
    return;
  }
  
  isRunning = true;
  console.log(`Запускаю автоматическую игру с интервалом ${interval / 1000} секунд`);
  
  // Сразу делаем первый ход
  autoplay().catch(error => console.error('Ошибка при автоматизации:', error));
  
  // Запускаем интервал для последующих ходов
  intervalId = setInterval(() => {
    if (isRunning) {
      autoplay().catch(error => console.error('Ошибка при автоматизации:', error));
    }
  }, interval);
}

/**
 * Останавливает автоматическую игру
 */
function stopAutoplay() {
  if (!isRunning) {
    console.log('Автоматическая игра не запущена');
    return;
  }
  
  isRunning = false;
  if (intervalId) {
    clearInterval(intervalId);
    intervalId = null;
  }
  
  console.log('Автоматическая игра остановлена');
}

/**
 * Изменяет интервал между ходами
 * @param {number} newInterval Новый интервал в секундах
 */
function changeInterval(newInterval) {
  const newIntervalMs = newInterval * 1000;
  interval = newIntervalMs;
  console.log(`Интервал изменен на ${newInterval} секунд`);
  
  // Если автоматическая игра запущена, перезапускаем ее с новым интервалом
  if (isRunning) {
    stopAutoplay();
    startAutoplay();
  }
}

/**
 * Выводит справку по командам
 */
function showHelp() {
  console.log('\nДоступные команды:');
  console.log('list, list-screens - Показать список всех экранов');
  console.log('start - Запустить автоматическую игру');
  console.log('stop - Остановить автоматическую игру');
  console.log('interval <seconds> - Изменить интервал между ходами (в секундах)');
  console.log('once - Сделать один ход');
  console.log('status - Показать текущий статус');
  console.log('help - Показать эту справку');
  console.log('exit - Выйти из программы\n');
}

/**
 * Показывает текущий статус
 */
function showStatus() {
  console.log('\nТекущий статус:');
  console.log(`Автоматическая игра: ${isRunning ? 'запущена' : 'остановлена'}`);
  console.log(`Интервал между ходами: ${interval / 1000} секунд\n`);
}

// Обработка команд пользователя
function processCommand(command) {
  const parts = command.trim().split(' ');
  const mainCommand = parts[0].toLowerCase();
  
  switch (mainCommand) {
    case 'list':
    case 'list-screens':
      listAllScreens();
      break;
    case 'start':
      startAutoplay();
      break;
    case 'stop':
      stopAutoplay();
      break;
    case 'interval':
      if (parts.length < 2) {
        console.log('Ошибка: укажите интервал в секундах');
      } else {
        const newInterval = parseFloat(parts[1]);
        if (isNaN(newInterval) || newInterval <= 0) {
          console.log('Ошибка: интервал должен быть положительным числом');
        } else {
          changeInterval(newInterval);
        }
      }
      break;
    case 'once':
      console.log('Выполняю один ход...');
      autoplay().catch(error => console.error('Ошибка при автоматизации:', error));
      break;
    case 'status':
      showStatus();
      break;
    case 'help':
      showHelp();
      break;
    case 'exit':
      console.log('Выход из программы...');
      stopAutoplay();
      rl.close();
      break;
    default:
      console.log(`Неизвестная команда: ${mainCommand}`);
      showHelp();
      break;
  }
}

// Основная функция
function main() {
  console.log('=== Автоматический игрок в реверси для Windows ===');
  console.log('Введите "help" для получения списка команд');
  
  rl.on('line', (input) => {
    processCommand(input);
  });
  
  rl.on('close', () => {
    process.exit(0);
  });
  
  // Показываем начальный статус
  showStatus();
}

// Запускаем программу
main(); 
#!/usr/bin/env node

/**
 * Автоматический игрок в реверси для конкретного окна
 * Позволяет указать имя окна, в котором нужно делать ходы
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const screenshot = require('screenshot-desktop');
const ReversiBot = require('./ReversiBot');
const readline = require('readline');

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
let targetWindowName = '';
let interval = 3000; // Интервал между ходами в миллисекундах
let isRunning = false;
let intervalId = null;
let lastCapturedWindowInfo = null; // Информация о последнем захваченном окне

// Инициализируем бота
const bot = new ReversiBot();

/**
 * Получает ID окна по его имени
 * @param {string} windowName Имя окна
 * @returns {string|null} ID окна или null, если окно не найдено
 */
function getWindowIdByName(windowName) {
  try {
    // Используем xdotool для поиска окна по имени
    const output = execSync(`xdotool search --name "${windowName}"`).toString().trim();
    const windowIds = output.split('\n').filter(Boolean);
    
    if (windowIds.length === 0) {
      console.log(`Окно с именем "${windowName}" не найдено`);
      return null;
    }
    
    // Возвращаем первое найденное окно
    return windowIds[0];
  } catch (error) {
    console.error('Ошибка при поиске окна:', error);
    return null;
  }
}

/**
 * Делает скриншот указанного окна
 * @param {string} windowId ID окна
 * @returns {Promise<string>} Путь к файлу скриншота
 */
async function captureWindow(windowId) {
  try {
    // Получаем информацию о размере и позиции окна
    const windowInfoOutput = execSync(`xdotool getwindowgeometry ${windowId}`).toString();
    const positionMatch = windowInfoOutput.match(/Position: (\d+),(\d+)/);
    const sizeMatch = windowInfoOutput.match(/Geometry: (\d+)x(\d+)/);
    
    if (!positionMatch || !sizeMatch) {
      throw new Error('Не удалось получить информацию о размере и позиции окна');
    }
    
    const x = parseInt(positionMatch[1]);
    const y = parseInt(positionMatch[2]);
    const width = parseInt(sizeMatch[1]);
    const height = parseInt(sizeMatch[2]);
    
    console.log(`Окно: позиция (${x}, ${y}), размер ${width}x${height}`);
    
    // Создаем путь для скриншота
    const screenshotPath = path.join(tempDir, `screenshot_${Date.now()}.png`);
    
    // Делаем скриншот только указанного окна
    try {
      // Активируем окно перед скриншотом
      execSync(`xdotool windowactivate ${windowId}`);
      
      // Небольшая пауза, чтобы окно успело активироваться
      execSync('sleep 0.5');
      
      // Пробуем разные методы создания скриншота
      let screenshotSuccess = false;
      
      // Метод 1: xwd + convert
      if (!screenshotSuccess) {
        try {
          const tempXwdPath = path.join(tempDir, `temp_${Date.now()}.xwd`);
          execSync(`xwd -id ${windowId} -out "${tempXwdPath}"`);
          execSync(`convert "${tempXwdPath}" "${screenshotPath}"`);
          fs.unlinkSync(tempXwdPath); // Удаляем временный файл
          console.log(`Скриншот окна сохранен с помощью xwd + convert: ${screenshotPath}`);
          screenshotSuccess = true;
        } catch (error) {
          console.error('Ошибка при использовании xwd + convert:', error.message);
        }
      }
      
      // Метод 3: import из ImageMagick
      if (!screenshotSuccess) {
        try {
          execSync(`import -window ${windowId} "${screenshotPath}"`);
          console.log(`Скриншот окна сохранен с помощью import: ${screenshotPath}`);
          screenshotSuccess = true;
        } catch (error) {
          console.error('Ошибка при использовании import:', error.message);
        }
      }
      
      // Если все методы не сработали, выбрасываем ошибку
      if (!screenshotSuccess) {
        throw new Error('Все методы создания скриншота окна не сработали');
      }
    } catch (error) {
      console.error('Ошибка при создании скриншота окна:', error);
      console.log('Пробуем сделать скриншот всего экрана...');
      
      // Если не удалось сделать скриншот окна, делаем скриншот всего экрана
      await screenshot({ filename: screenshotPath });
      console.log(`Скриншот всего экрана сохранен: ${screenshotPath}`);
    }
    
    // Сохраняем информацию о позиции окна для корректировки координат клика
    lastCapturedWindowInfo = {
      x,
      y,
      width,
      height
    };
    
    return screenshotPath;
  } catch (error) {
    console.error('Ошибка при создании скриншота:', error);
    throw error;
  }
}

/**
 * Выполняет клик по указанным координатам в окне
 * @param {string} windowId ID окна
 * @param {number} x X-координата относительно экрана
 * @param {number} y Y-координата относительно экрана
 */
function clickAtInWindow(windowId, x, y) {
  try {
    // Если у нас есть информация о позиции окна, используем её для корректировки координат
    if (lastCapturedWindowInfo) {
      // Координаты уже относительно всего экрана, не нужно добавлять смещение окна
      console.log(`Выполняю клик по координатам: ${x}, ${y} в окне ${windowId}`);
    } else {
      console.log(`Выполняю клик по координатам: ${x}, ${y} в окне ${windowId} (без корректировки)`);
    }
    
    // Активируем окно и выполняем клик
    execSync(`xdotool windowactivate ${windowId}`);
    
    // Небольшая пауза, чтобы окно успело активироваться
    execSync('sleep 0.5');
    
    // Выполняем клик
    execSync(`xdotool mousemove ${Math.round(x)} ${Math.round(y)} click 1`);
    
    console.log('Клик выполнен успешно');
  } catch (error) {
    console.error('Ошибка при выполнении клика:', error);
    throw error;
  }
}

/**
 * Основная функция автоматизации для конкретного окна
 */
async function autoplayInWindow() {
  try {
    if (!targetWindowName) {
      console.log('Ошибка: не указано имя целевого окна');
      return;
    }
    
    // Получаем ID окна
    const windowId = getWindowIdByName(targetWindowName);
    if (!windowId) {
      return;
    }
    
    // Делаем скриншот окна
    const screenshotPath = await captureWindow(windowId);
    
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
    clickAtInWindow(windowId, Math.round(x), Math.round(y));
    
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
  
  if (!targetWindowName) {
    console.log('Ошибка: не указано имя целевого окна');
    return;
  }
  
  isRunning = true;
  console.log(`Запускаю автоматическую игру для окна "${targetWindowName}" с интервалом ${interval / 1000} секунд`);
  
  // Сразу делаем первый ход
  autoplayInWindow().catch(error => console.error('Ошибка при автоматизации:', error));
  
  // Запускаем интервал для последующих ходов
  intervalId = setInterval(() => {
    if (isRunning) {
      autoplayInWindow().catch(error => console.error('Ошибка при автоматизации:', error));
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
 * Получает список всех окон
 * @returns {Array<{id: string, title: string}>} Массив объектов с ID и названиями окон
 */
function getAllWindows() {
  try {
    // Получаем список всех окон
    const windowIdsOutput = execSync('xdotool search --all --onlyvisible ""').toString().trim();
    const windowIds = windowIdsOutput.split('\n').filter(Boolean);
    
    const windows = [];
    
    for (const id of windowIds) {
      try {
        // Получаем название окна
        const windowName = execSync(`xdotool getwindowname ${id}`).toString().trim();
        if (windowName) {
          windows.push({ id, title: windowName });
        }
      } catch (error) {
        // Игнорируем ошибки для отдельных окон
      }
    }
    
    return windows;
  } catch (error) {
    console.error('Ошибка при получении списка окон:', error);
    return [];
  }
}

/**
 * Выводит список всех окон
 */
function listAllWindows() {
  const windows = getAllWindows();
  
  if (windows.length === 0) {
    console.log('Не найдено ни одного окна');
    return;
  }
  
  console.log('\nСписок доступных окон:');
  console.log('ID\t\tНазвание');
  console.log('--------------------------------------------------');
  
  windows.forEach(window => {
    console.log(`${window.id}\t${window.title}`);
  });
  
  console.log('--------------------------------------------------');
  console.log(`Всего окон: ${windows.length}`);
  console.log('Для выбора окна введите: window <название или часть названия>\n');
}

/**
 * Устанавливает имя целевого окна
 * @param {string} windowName Имя окна
 */
function setTargetWindow(windowName) {
  targetWindowName = windowName;
  console.log(`Целевое окно установлено: "${windowName}"`);
  
  // Проверяем, существует ли окно
  const windowId = getWindowIdByName(targetWindowName);
  if (windowId) {
    try {
      // Получаем полное название окна
      const fullWindowName = execSync(`xdotool getwindowname ${windowId}`).toString().trim();
      
      // Получаем информацию о размере и позиции окна
      const windowInfoOutput = execSync(`xdotool getwindowgeometry ${windowId}`).toString();
      const positionMatch = windowInfoOutput.match(/Position: (\d+),(\d+)/);
      const sizeMatch = windowInfoOutput.match(/Geometry: (\d+)x(\d+)/);
      
      if (positionMatch && sizeMatch) {
        const x = parseInt(positionMatch[1]);
        const y = parseInt(positionMatch[2]);
        const width = parseInt(sizeMatch[1]);
        const height = parseInt(sizeMatch[2]);
        
        console.log(`Окно найдено:`);
        console.log(`- ID: ${windowId}`);
        console.log(`- Полное название: ${fullWindowName}`);
        console.log(`- Позиция: (${x}, ${y})`);
        console.log(`- Размер: ${width}x${height}`);
        
        // Подсветим окно, чтобы пользователь мог его увидеть
        try {
          execSync(`xdotool windowactivate ${windowId}`);
          console.log('Окно активировано для наглядности');
        } catch (error) {
          // Игнорируем ошибку активации
        }
      }
    } catch (error) {
      console.error('Ошибка при получении информации об окне:', error);
    }
  }
}

/**
 * Выводит справку по командам
 */
function showHelp() {
  console.log('\nДоступные команды:');
  console.log('list, list-windows - Показать список всех окон');
  console.log('window <name> - Установить имя целевого окна');
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
  console.log(`Целевое окно: ${targetWindowName || 'не установлено'}`);
  console.log(`Автоматическая игра: ${isRunning ? 'запущена' : 'остановлена'}`);
  console.log(`Интервал между ходами: ${interval / 1000} секунд\n`);
}

// Обработка команд пользователя
function processCommand(command) {
  const parts = command.trim().split(' ');
  const mainCommand = parts[0].toLowerCase();
  
  switch (mainCommand) {
    case 'window':
      if (parts.length < 2) {
        console.log('Ошибка: укажите имя окна');
      } else {
        const windowName = parts.slice(1).join(' ');
        setTargetWindow(windowName);
      }
      break;
    case 'list':
    case 'list-windows':
      listAllWindows();
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
      autoplayInWindow().catch(error => console.error('Ошибка при автоматизации:', error));
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
  console.log('=== Автоматический игрок в реверси для конкретного окна ===');
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
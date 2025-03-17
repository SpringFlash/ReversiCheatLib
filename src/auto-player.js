#!/usr/bin/env node

/**
 * Автоматический игрок в реверси
 * Запускает автоматизацию с заданным интервалом
 */

const { autoplay } = require('./autoplay');
const readline = require('readline');

// Создаем интерфейс для чтения с консоли
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

// Настройки по умолчанию
let interval = 3000; // Интервал между ходами в миллисекундах
let isRunning = false;
let intervalId = null;

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
  console.log('=== Автоматический игрок в реверси ===');
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
# Reversi Bot

Библиотека для анализа игры в реверси (Othello) по скриншотам игрового поля. Поддерживает использование как CLI-утилиты, REST API сервера и библиотеки для мобильных приложений.

## Требования

- Node.js 18+
- Python 3.x
- OpenCV (opencv-python)
- NumPy

## Установка

### Как библиотеку

```bash
npm install @reversi/bot
# или
yarn add @reversi/bot
```

### Как локальный проект

1. Установите системные зависимости:

```bash
pip3 install opencv-python numpy
```

2. Клонируйте репозиторий:

```bash
git clone [url-репозитория]
cd reversi-bot
```

3. Установите зависимости:

```bash
npm install
```

## Использование

### Как библиотеку в React Native

См. [примеры использования в React Native](examples/ReactNative.md)

### Как CLI-утилиту

```bash
npm run cli path/to/screenshot.png
```

### Как REST API сервер

1. Запустите сервер:

```bash
npm start
# или в режиме разработки:
npm run dev
```

2. Отправьте POST запрос на `/analyze` с файлом скриншота:

```bash
curl -X POST -F "screenshot=@path/to/screenshot.png" http://localhost:3000/analyze
```

## API

### REST API

#### POST /analyze

Анализирует скриншот игры и возвращает рекомендуемый ход.

**Request:**

- Content-Type: multipart/form-data
- Body:
  - screenshot: файл изображения (PNG, JPEG)

**Response:**

```json
{
  "success": true,
  "hasMove": true,
  "move": {
    "row": 3,
    "col": "E",
    "score": 10,
    "screen_coordinates": {
      "x": 500,
      "y": 300
    }
  },
  "board": {
    "state": [...],
    "playerColor": "black",
    "rect": {
      "top_left": [x, y],
      "top_right": [x, y],
      "bottom_right": [x, y],
      "bottom_left": [x, y]
    }
  },
  "screen_size": {
    "width": 1080,
    "height": 1920
  }
}
```

### TypeScript/JavaScript API

```typescript
import { ReversiBot } from "@reversi/bot";

const bot = new ReversiBot();
const result = await bot.analyzeScreenshot("path/to/screenshot.png");
```

См. [полную документацию TypeScript API](examples/ReactNative.md#api)

## Формат вывода CLI

- Столбцы обозначаются буквами от A до H
- Строки нумеруются от 1 до 8
- ● - черная фишка
- ○ - белая фишка
- - - пустая клетка
- - - рекомендуемый ход

## Особенности

- Автоматическое определение цвета игрока
- Использует OpenCV для распознавания состояния игрового поля
- Возвращает точные координаты для клика на экране
- Использует эвристическую оценку ходов, учитывая:
  - Захват углов (наивысший приоритет)
  - Захват краев
  - Количество переворачиваемых фишек

## Разработка

1. Установите зависимости для разработки:

```bash
npm install
```

2. Запустите тесты:

```bash
npm test
```

3. Соберите проект:

```bash
npm run build
```

## Лицензия

MIT

# Reversi Bot Native

Нативная библиотека для анализа игры в реверси (Othello) по скриншотам игрового поля. Использует OpenCV для обработки изображений прямо на устройстве, без необходимости отправки данных на сервер.

## Особенности

- 🚀 Полностью нативная обработка изображений
- 🔒 Работает локально, без отправки данных на сервер
- 📱 Поддержка iOS и Android
- 🎯 Точное определение позиций для клика
- 🎮 Автоматическое определение цвета игрока
- 🧠 Встроенный ИИ для выбора лучшего хода

## Требования

- React Native >= 0.60.0
- iOS:
  - iOS 11.0 или выше
  - Xcode 12.0 или выше
  - CocoaPods
- Android:
  - minSdkVersion 21
  - compileSdkVersion 31
  - NDK

## Установка

```bash
# Установка через npm
npm install @reversi/bot-native

# Установка через yarn
yarn add @reversi/bot-native
```

### iOS

1. Добавьте OpenCV в ваш `Podfile`:

```ruby
pod 'OpenCV', '~> 4.7.0'
```

2. Установите зависимости:

```bash
cd ios && pod install
```

3. Добавьте разрешения в `Info.plist`:

```xml
<key>NSCameraUsageDescription</key>
<string>Для анализа игрового поля</string>
<key>NSPhotoLibraryUsageDescription</key>
<string>Для анализа скриншотов игры</string>
```

### Android

1. Добавьте OpenCV в `android/app/build.gradle`:

```gradle
android {
    defaultConfig {
        // ...
        ndk {
            abiFilters "armeabi-v7a", "arm64-v8a", "x86", "x86_64"
        }
    }
}

dependencies {
    implementation 'org.opencv:opencv-android:4.7.0'
}
```

2. Добавьте разрешения в `AndroidManifest.xml`:

```xml
<uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" />
<uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" />
```

## Использование

```typescript
import { ReversiClient } from "@reversi/bot-native";
import { captureScreen } from "react-native-view-shot";

const analyzeGame = async () => {
  try {
    // Делаем скриншот
    const uri = await captureScreen({
      format: "jpg",
      quality: 0.8,
    });

    // Создаем экземпляр клиента
    const client = new ReversiClient();

    // Анализируем скриншот
    const result = await client.analyzeScreenshot(uri);

    if (result.success && result.hasMove) {
      const { x, y } = result.move.screen_coordinates;
      const { row, col, score } = result.move;

      console.log(`Рекомендуемый ход: ${col}${row} (оценка: ${score})`);
      console.log(`Координаты для клика: (${x}, ${y})`);
    }
  } catch (error) {
    console.error("Ошибка анализа:", error);
  }
};
```

## API

### ReversiClient

#### Methods

```typescript
analyzeScreenshot(imageUri: string): Promise<AnalysisResult>
```

#### Types

```typescript
interface AnalysisResult {
  success: boolean;
  hasMove: boolean;
  message?: string;
  move?: {
    row: number;
    col: string;
    score: number;
    screen_coordinates: {
      x: number;
      y: number;
    };
  };
  board?: {
    state: BoardState;
    playerColor: "black" | "white";
  };
}

interface BoardState {
  [key: number]: {
    [key: number]: "black" | "white" | "empty";
  };
}
```

## Рекомендации по использованию

1. **Качество изображения**

   - Используйте высокое качество скриншотов (рекомендуется quality >= 0.8)
   - Убедитесь, что игровое поле полностью видно
   - Избегайте бликов и теней на экране

2. **Производительность**

   - Добавьте индикатор загрузки во время анализа
   - Кэшируйте результаты для одинаковых состояний доски
   - Анализируйте только когда это действительно необходимо

3. **Обработка ошибок**

   - Всегда оборачивайте вызовы в try-catch
   - Проверяйте result.success перед использованием результата
   - Добавьте повторные попытки для случаев неудачного распознавания

4. **Разрешения**
   - Запрашивайте разрешения на доступ к хранилищу при первом запуске
   - Обрабатывайте случаи отказа в разрешениях
   - Предоставьте пользователю понятное объяснение, зачем нужны разрешения

## Отладка

Библиотека создает отладочные изображения в директории приложения:

- `debug_original.png` - исходное изображение
- `debug_gray.png` - изображение в оттенках серого
- `debug_thresh.png` - результат пороговой обработки
- `debug_board.png` - найденное игровое поле с разметкой

## Известные проблемы

1. На некоторых устройствах может потребоваться дополнительная настройка параметров распознавания
2. При очень ярком освещении возможны ложные срабатывания
3. На устройствах с маленьким экраном может потребоваться корректировка размера области анализа

## Лицензия

MIT

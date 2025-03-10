# Использование в React Native

## Установка

```bash
npm install @reversi/bot
# или
yarn add @reversi/bot
```

## Пример использования

```typescript
import { ReversiBot } from "@reversi/bot";
import { captureScreen } from "react-native-view-shot";
import { TouchableOpacity, Image } from "react-native";

const GameAnalyzer = () => {
  const analyzeGame = async () => {
    try {
      // Делаем скриншот
      const uri = await captureScreen({
        format: "jpg",
        quality: 0.8,
      });

      // Создаем экземпляр бота
      const bot = new ReversiBot();

      // Анализируем скриншот
      const result = await bot.analyzeScreenshot(uri);

      if (result.success && result.hasMove) {
        const { x, y } = result.move.screen_coordinates;

        // Создаем и запускаем анимацию подсказки
        showHint(x, y);

        // Или выполняем автоматический клик
        simulateClick(x, y);
      }
    } catch (error) {
      console.error("Ошибка анализа:", error);
    }
  };

  return (
    <TouchableOpacity onPress={analyzeGame}>
      <Image source={require("./analyze_button.png")} />
    </TouchableOpacity>
  );
};

export default GameAnalyzer;
```

## Особенности реализации

1. Убедитесь, что у вас установлен Python 3 и OpenCV:

```bash
pip3 install opencv-python numpy
```

2. Для Android добавьте в `android/app/build.gradle`:

```gradle
android {
    defaultConfig {
        // ...
        ndk {
            abiFilters "armeabi-v7a", "arm64-v8a", "x86", "x86_64"
        }
    }
}
```

3. Для iOS добавьте в `Podfile`:

```ruby
pod 'OpenCV', '~> 4.3.0'
```

4. Настройте права на использование скриншотов:

### Android (`android/app/src/main/AndroidManifest.xml`):

```xml
<uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" />
<uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" />
```

### iOS (`ios/YourApp/Info.plist`):

```xml
<key>NSPhotoLibraryUsageDescription</key>
<string>Для анализа игрового поля</string>
```

## API

### ReversiBot

#### Constructor

```typescript
constructor(pythonPath?: string)
```

#### Methods

```typescript
async analyzeScreenshot(imagePath: string): Promise<AnalysisResult>
```

### Interfaces

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
    rect: BoardRect;
  };
  screen_size: {
    width: number;
    height: number;
  };
}
```

## Рекомендации по использованию

1. Используйте высокое качество скриншотов для лучшего распознавания
2. Добавьте индикатор загрузки во время анализа
3. Реализуйте кэширование результатов для одинаковых состояний доски
4. Добавьте обработку ошибок и повторные попытки при неудачном распознавании

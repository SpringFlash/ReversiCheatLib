# Примеры использования Reversi Bot Native

## Базовый пример

```typescript
import { ReversiClient } from "@reversi/bot-native";
import { captureScreen } from "react-native-view-shot";
import { TouchableOpacity, Image, Alert } from "react-native";

const GameAnalyzer = () => {
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

        // Показываем информацию о ходе
        Alert.alert(
          "Рекомендуемый ход",
          `Строка: ${row}\nСтолбец: ${col}\nОценка: ${score}`
        );

        // Создаем и запускаем анимацию подсказки
        showHint(x, y);
      }
    } catch (error) {
      Alert.alert(
        "Ошибка",
        `Не удалось проанализировать ход: ${error.message}`
      );
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

## Пример с индикатором загрузки

```typescript
import { ReversiClient } from "@reversi/bot-native";
import { captureScreen } from "react-native-view-shot";
import { ActivityIndicator, TouchableOpacity, View } from "react-native";
import { useState } from "react";

const GameAnalyzer = () => {
  const [analyzing, setAnalyzing] = useState(false);

  const analyzeGame = async () => {
    if (analyzing) return;

    setAnalyzing(true);
    try {
      const uri = await captureScreen({
        format: "jpg",
        quality: 0.8,
      });

      const client = new ReversiClient();
      const result = await client.analyzeScreenshot(uri);

      if (result.success && result.hasMove) {
        showHint(result.move.screen_coordinates);
      }
    } catch (error) {
      Alert.alert("Ошибка", error.message);
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <TouchableOpacity onPress={analyzeGame} disabled={analyzing}>
      {analyzing ? (
        <ActivityIndicator size="large" color="#0000ff" />
      ) : (
        <Image source={require("./analyze_button.png")} />
      )}
    </TouchableOpacity>
  );
};
```

## Пример с кэшированием

```typescript
import { ReversiClient } from "@reversi/bot-native";
import { captureScreen } from "react-native-view-shot";
import AsyncStorage from "@react-native-async-storage/async-storage";

const GameAnalyzer = () => {
  const analyzeGame = async () => {
    try {
      const uri = await captureScreen({
        format: "jpg",
        quality: 0.8,
      });

      // Проверяем кэш
      const cacheKey = await calculateImageHash(uri);
      const cachedResult = await AsyncStorage.getItem(cacheKey);

      if (cachedResult) {
        const result = JSON.parse(cachedResult);
        showHint(result.move.screen_coordinates);
        return;
      }

      // Анализируем новый скриншот
      const client = new ReversiClient();
      const result = await client.analyzeScreenshot(uri);

      if (result.success && result.hasMove) {
        // Сохраняем в кэш
        await AsyncStorage.setItem(cacheKey, JSON.stringify(result));
        showHint(result.move.screen_coordinates);
      }
    } catch (error) {
      Alert.alert("Ошибка", error.message);
    }
  };
};
```

## Пример с запросом разрешений

```typescript
import { ReversiClient } from "@reversi/bot-native";
import { captureScreen } from "react-native-view-shot";
import { PermissionsAndroid, Platform } from "react-native";

const GameAnalyzer = () => {
  const requestPermissions = async () => {
    if (Platform.OS === "android") {
      const granted = await PermissionsAndroid.requestMultiple([
        PermissionsAndroid.PERMISSIONS.READ_EXTERNAL_STORAGE,
        PermissionsAndroid.PERMISSIONS.WRITE_EXTERNAL_STORAGE,
      ]);

      return Object.values(granted).every(
        (permission) => permission === PermissionsAndroid.RESULTS.GRANTED
      );
    }
    return true;
  };

  const analyzeGame = async () => {
    try {
      const hasPermissions = await requestPermissions();
      if (!hasPermissions) {
        Alert.alert(
          "Ошибка",
          "Для работы приложения необходимы разрешения на доступ к хранилищу"
        );
        return;
      }

      const uri = await captureScreen({
        format: "jpg",
        quality: 0.8,
      });

      const client = new ReversiClient();
      const result = await client.analyzeScreenshot(uri);

      if (result.success && result.hasMove) {
        showHint(result.move.screen_coordinates);
      }
    } catch (error) {
      Alert.alert("Ошибка", error.message);
    }
  };
};
```

## Пример с повторными попытками

```typescript
import { ReversiClient } from "@reversi/bot-native";
import { captureScreen } from "react-native-view-shot";

const GameAnalyzer = () => {
  const analyzeWithRetry = async (
    uri: string,
    retries = 3
  ): Promise<AnalysisResult> => {
    try {
      const client = new ReversiClient();
      const result = await client.analyzeScreenshot(uri);

      if (!result.success && retries > 0) {
        // Ждем немного перед повторной попыткой
        await new Promise((resolve) => setTimeout(resolve, 500));
        return analyzeWithRetry(uri, retries - 1);
      }

      return result;
    } catch (error) {
      if (retries > 0) {
        await new Promise((resolve) => setTimeout(resolve, 500));
        return analyzeWithRetry(uri, retries - 1);
      }
      throw error;
    }
  };

  const analyzeGame = async () => {
    try {
      const uri = await captureScreen({
        format: "jpg",
        quality: 0.8,
      });

      const result = await analyzeWithRetry(uri);

      if (result.success && result.hasMove) {
        showHint(result.move.screen_coordinates);
      }
    } catch (error) {
      Alert.alert("Ошибка", error.message);
    }
  };
};
```

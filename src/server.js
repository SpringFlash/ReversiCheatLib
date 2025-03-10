const express = require("express");
const multer = require("multer");
const cors = require("cors");
const path = require("path");
const fs = require("fs").promises;
const ReversiBot = require("./index");

const app = express();
const port = process.env.PORT || 3000;

// Настраиваем CORS
app.use(cors());

// Настраиваем multer для загрузки файлов
const storage = multer.diskStorage({
  destination: async function (req, file, cb) {
    const uploadDir = path.join(__dirname, "..", "uploads");
    try {
      await fs.mkdir(uploadDir, { recursive: true });
      cb(null, uploadDir);
    } catch (error) {
      cb(error);
    }
  },
  filename: function (req, file, cb) {
    // Генерируем уникальное имя файла
    const uniqueSuffix = Date.now() + "-" + Math.round(Math.random() * 1e9);
    cb(null, uniqueSuffix + path.extname(file.originalname));
  },
});

const upload = multer({
  storage: storage,
  limits: {
    fileSize: 5 * 1024 * 1024, // Ограничение размера файла (5MB)
  },
  fileFilter: (req, file, cb) => {
    // Проверяем тип файла
    if (file.mimetype.startsWith("image/")) {
      cb(null, true);
    } else {
      cb(new Error("Поддерживаются только изображения"));
    }
  },
});

// Инициализируем бота
const bot = new ReversiBot();

// Эндпоинт для анализа скриншота
app.post("/analyze", upload.single("screenshot"), async (req, res) => {
  try {
    console.log("Запрос на анализ скриншота");
    if (!req.file) {
      return res.status(400).json({ error: "Файл не загружен" });
    }

    // Анализируем скриншот
    const result = await bot.analyzeScreenshotForAPI(req.file.path);
    console.log("Результат анализа:", result);

    // Удаляем временный файл
    await fs.unlink(req.file.path);

    res.json(result);
  } catch (error) {
    console.error("Ошибка при обработке скриншота:", error);
    res.status(500).json({ error: "Ошибка при обработке скриншота" });
  }
});

// Обработка ошибок
app.use((err, req, res, next) => {
  if (err instanceof multer.MulterError) {
    if (err.code === "LIMIT_FILE_SIZE") {
      return res.status(400).json({ error: "Файл слишком большой" });
    }
  }
  console.error(err);
  res.status(500).json({ error: "Внутренняя ошибка сервера" });
});

app.listen(port, () => {
  console.log(`Сервер запущен на порту ${port}`);
});

const ImageProcessor = require("./imageProcessor");
const GameLogic = require("./gameLogic");

class ReversiBot {
  constructor() {
    this.imageProcessor = new ImageProcessor();
    this.gameLogic = new GameLogic();
    this.columnLetters = ["A", "B", "C", "D", "E", "F", "G", "H"];
  }

  async analyzeScreenshot(screenshotPath) {
    try {
      // Получаем состояние доски и цвет игрока из скриншота
      const result = await this.imageProcessor.processScreenshot(
        screenshotPath
      );
      const boardState = result.board;
      const playerColor = result.player_color || "black"; // По умолчанию черные

      console.log("Распознанное состояние доски:");
      this.printBoard(boardState);
      console.log(
        `Вы играете за: ${playerColor === "black" ? "черных" : "белых"}`
      );

      // Находим лучший ход для текущего игрока
      const bestMove = this.gameLogic.getBestMove(boardState, playerColor);

      if (bestMove) {
        console.log("\nРекомендуемый ход:");
        console.log(`Строка: ${bestMove.row + 1}`);
        console.log(`Столбец: ${this.columnLetters[bestMove.col]}`);
        console.log(`Оценка хода: ${bestMove.score}`);

        this.printBoard(boardState, bestMove);
      } else {
        console.log("Нет доступных ходов");
      }
    } catch (error) {
      console.error("Ошибка при анализе скриншота:", error);
    }
  }

  async analyzeScreenshotForAPI(screenshotPath) {
    try {
      // Получаем состояние доски и цвет игрока из скриншота
      const result = await this.imageProcessor.processScreenshot(
        screenshotPath
      );
      const boardState = result.board;
      const playerColor = result.player_color || "black";

      // Находим лучший ход
      const bestMove = this.gameLogic.getBestMove(boardState, playerColor);

      if (!bestMove) {
        return {
          success: true,
          hasMove: false,
          message: "Нет доступных ходов",
          screen_size: result.screen_size,
        };
      }

      // Формируем ответ для API
      return {
        success: true,
        hasMove: true,
        move: {
          row: bestMove.row + 1,
          col: this.columnLetters[bestMove.col],
          score: bestMove.score,
          screen_coordinates: {
            x:
              result.board_rect.top_left[0] +
              ((result.board_rect.top_right[0] -
                result.board_rect.top_left[0]) *
                (bestMove.col + 0.5)) /
                8 +
              ((result.board_rect.bottom_left[0] -
                result.board_rect.top_left[0]) *
                (bestMove.row + 0.5)) /
                8,
            y:
              result.board_rect.top_left[1] +
              ((result.board_rect.top_right[1] -
                result.board_rect.top_left[1]) *
                (bestMove.col + 0.5)) /
                8 +
              ((result.board_rect.bottom_left[1] -
                result.board_rect.top_left[1]) *
                (bestMove.row + 0.5)) /
                8,
          },
        },
        board: {
          state: boardState,
          playerColor: playerColor,
          rect: result.board_rect,
        },
        screen_size: result.screen_size,
      };
    } catch (error) {
      console.error("Ошибка при анализе скриншота:", error);
      return {
        success: false,
        error: "Ошибка при анализе скриншота",
      };
    }
  }

  printBoard(board, move = null) {
    console.log("\nТекущее состояние доски:");
    console.log("  A B C D E F G H");
    for (let i = 0; i < 8; i++) {
      let row = `${i + 1} `;
      for (let j = 0; j < 8; j++) {
        if (move && move.row === i && move.col === j) {
          row += "* ";
        } else {
          switch (board[i][j]) {
            case "black":
              row += "● ";
              break;
            case "white":
              row += "○ ";
              break;
            case "empty":
              row += "- ";
              break;
          }
        }
      }
      console.log(row);
    }
    console.log();
  }
}

// Пример использования из командной строки
if (require.main === module) {
  const bot = new ReversiBot();
  const screenshotPath = process.argv[2];

  if (!screenshotPath) {
    console.error("Пожалуйста, укажите путь к скриншоту");
    process.exit(1);
  }

  bot.analyzeScreenshot(screenshotPath);
}

module.exports = ReversiBot;

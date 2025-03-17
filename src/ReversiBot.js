const { spawn } = require("child_process");
const path = require("path");
const GameLogic = require("./gameLogic");

class ReversiBot {
  constructor(pythonPath) {
    this.columnLetters = ["A", "B", "C", "D", "E", "F", "G", "H"];
    this.pythonPath = pythonPath || "python3";
    this.gameLogic = new GameLogic();
  }

  async analyzeScreenshot(imagePath) {
    return new Promise((resolve, reject) => {
      const pythonScript = path.join(__dirname, "process_image.py");
      const process = spawn(this.pythonPath, [pythonScript, imagePath]);

      let output = "";
      let error = "";

      process.stdout.on("data", (data) => {
        output += data.toString();
      });

      process.stderr.on("data", (data) => {
        error += data.toString();
      });

      process.on("close", (code) => {
        if (code !== 0) {
          reject(new Error(`Python script failed: ${error}`));
          return;
        }

        try {
          const result = JSON.parse(output);
          resolve(this.processAnalysisResult(result));
        } catch (err) {
          const errorMessage = err instanceof Error ? err.message : String(err);
          reject(new Error(`Failed to parse Python output: ${errorMessage}`));
        }
      });
    });
  }

  async analyzeScreenshotForAPI(screenshotPath) {
    try {
      // Получаем состояние доски и цвет игрока из скриншота
      const result = await this.analyzeScreenshot(screenshotPath);
      return result;
    } catch (error) {
      console.error("Ошибка при анализе скриншота:", error);
      return {
        success: false,
        error: "Ошибка при анализе скриншота",
      };
    }
  }

  processAnalysisResult(pythonResult) {
    const {
      board: boardState,
      player_color: playerColor,
      board_rect: boardRect,
      screen_size: screenSize,
    } = pythonResult;

    // Находим лучший ход
    const bestMove = this.gameLogic.getBestMove(boardState, playerColor);

    if (!bestMove) {
      return {
        success: true,
        hasMove: false,
        message: "Нет доступных ходов",
        screen_size: screenSize,
      };
    }

    return {
      success: true,
      hasMove: true,
      move: {
        row: bestMove.row + 1,
        col: this.columnLetters[bestMove.col],
        score: bestMove.score,
        screen_coordinates: this.calculateScreenCoordinates(
          boardRect,
          bestMove.row,
          bestMove.col
        ),
      },
      board: {
        state: boardState,
        playerColor,
        rect: boardRect,
      },
      screen_size: screenSize,
    };
  }

  calculateScreenCoordinates(boardRect, row, col) {
    const { top_left, top_right, bottom_left } = boardRect;

    return {
      x: Math.round(
        top_left[0] +
          ((top_right[0] - top_left[0]) * (col + 0.5)) / 8 +
          ((bottom_left[0] - top_left[0]) * (row + 0.5)) / 8
      ),
      y: Math.round(
        top_left[1] +
          ((top_right[1] - top_left[1]) * (col + 0.5)) / 8 +
          ((bottom_left[1] - top_left[1]) * (row + 0.5)) / 8
      ),
    };
  }
}

module.exports = ReversiBot; 
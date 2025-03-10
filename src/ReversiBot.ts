import { spawn } from "child_process";
import path from "path";

export interface BoardState {
  [key: number]: {
    [key: number]: "black" | "white" | "empty";
  };
}

export interface ScreenCoordinates {
  x: number;
  y: number;
}

export interface BoardRect {
  top_left: [number, number];
  top_right: [number, number];
  bottom_right: [number, number];
  bottom_left: [number, number];
}

export interface ScreenSize {
  width: number;
  height: number;
}

export interface Move {
  row: number;
  col: string;
  score: number;
  screen_coordinates: ScreenCoordinates;
}

export interface AnalysisResult {
  success: boolean;
  hasMove: boolean;
  message?: string;
  move?: Move;
  board?: {
    state: BoardState;
    playerColor: "black" | "white";
    rect: BoardRect;
  };
  screen_size: ScreenSize;
}

export class ReversiBot {
  private readonly columnLetters: string[] = [
    "A",
    "B",
    "C",
    "D",
    "E",
    "F",
    "G",
    "H",
  ];
  private pythonPath: string = "python3";

  constructor(pythonPath?: string) {
    if (pythonPath) {
      this.pythonPath = pythonPath;
    }
  }

  public async analyzeScreenshot(imagePath: string): Promise<AnalysisResult> {
    return new Promise((resolve, reject) => {
      const pythonScript = path.join(
        __dirname,
        "..",
        "src",
        "process_image.py"
      );
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

  private processAnalysisResult(pythonResult: any): AnalysisResult {
    const {
      board: boardState,
      player_color: playerColor,
      board_rect: boardRect,
      screen_size: screenSize,
    } = pythonResult;

    // Находим лучший ход
    const bestMove = this.getBestMove(boardState, playerColor);

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

  private getBestMove(
    board: BoardState,
    playerColor: "black" | "white"
  ): { row: number; col: number; score: number } | null {
    // Реализация логики поиска лучшего хода
    // TODO: Перенести логику из gameLogic.js
    return null;
  }

  private calculateScreenCoordinates(
    boardRect: BoardRect,
    row: number,
    col: number
  ): ScreenCoordinates {
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

import ReversiAnalyzer from "../NativeReversiAnalyzer";

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

export interface BoardState {
  [key: number]: {
    [key: number]: "black" | "white" | "empty";
  };
}

interface ImageUpload {
  uri: string;
  type: string;
  name: string;
}

export class ReversiClient {
  public async analyzeScreenshot(imageUri: string): Promise<AnalysisResult> {
    try {
      // Используем нативный модуль для анализа изображения
      const result = await ReversiAnalyzer.analyzeImage(imageUri);

      if (!result.success) {
        throw new Error("Failed to analyze image");
      }

      // Преобразуем результат в нужный формат
      return {
        success: true,
        hasMove: !!result.move,
        move: result.move,
        board: {
          state: this.convertBoardState(result.board),
          playerColor: result.playerColor || "black",
          rect: {
            // В нативной реализации мы можем не возвращать rect,
            // так как координаты клика вычисляются на нативной стороне
            top_left: [0, 0],
            top_right: [0, 0],
            bottom_right: [0, 0],
            bottom_left: [0, 0],
          },
        },
        screen_size: {
          width: 0,
          height: 0,
        },
      };
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : String(error);
      throw new Error(`Failed to analyze screenshot: ${errorMessage}`);
    }
  }

  private convertBoardState(
    board: Array<Array<"black" | "white" | "empty">>
  ): BoardState {
    const result: BoardState = {};
    board.forEach((row, i) => {
      result[i] = {};
      row.forEach((cell, j) => {
        result[i][j] = cell;
      });
    });
    return result;
  }
}

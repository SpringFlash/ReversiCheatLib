"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.ReversiBot = void 0;
const child_process_1 = require("child_process");
const path_1 = __importDefault(require("path"));
class ReversiBot {
    constructor(pythonPath) {
        this.columnLetters = [
            "A",
            "B",
            "C",
            "D",
            "E",
            "F",
            "G",
            "H",
        ];
        this.pythonPath = "python3";
        if (pythonPath) {
            this.pythonPath = pythonPath;
        }
    }
    async analyzeScreenshot(imagePath) {
        return new Promise((resolve, reject) => {
            const pythonScript = path_1.default.join(__dirname, "..", "src", "process_image.py");
            const process = (0, child_process_1.spawn)(this.pythonPath, [pythonScript, imagePath]);
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
                }
                catch (err) {
                    const errorMessage = err instanceof Error ? err.message : String(err);
                    reject(new Error(`Failed to parse Python output: ${errorMessage}`));
                }
            });
        });
    }
    processAnalysisResult(pythonResult) {
        const { board: boardState, player_color: playerColor, board_rect: boardRect, screen_size: screenSize, } = pythonResult;
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
                screen_coordinates: this.calculateScreenCoordinates(boardRect, bestMove.row, bestMove.col),
            },
            board: {
                state: boardState,
                playerColor,
                rect: boardRect,
            },
            screen_size: screenSize,
        };
    }
    getBestMove(board, playerColor) {
        // Реализация логики поиска лучшего хода
        // TODO: Перенести логику из gameLogic.js
        return null;
    }
    calculateScreenCoordinates(boardRect, row, col) {
        const { top_left, top_right, bottom_left } = boardRect;
        return {
            x: Math.round(top_left[0] +
                ((top_right[0] - top_left[0]) * (col + 0.5)) / 8 +
                ((bottom_left[0] - top_left[0]) * (row + 0.5)) / 8),
            y: Math.round(top_left[1] +
                ((top_right[1] - top_left[1]) * (col + 0.5)) / 8 +
                ((bottom_left[1] - top_left[1]) * (row + 0.5)) / 8),
        };
    }
}
exports.ReversiBot = ReversiBot;

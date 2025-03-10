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
export declare class ReversiBot {
    private readonly columnLetters;
    private pythonPath;
    constructor(pythonPath?: string);
    analyzeScreenshot(imagePath: string): Promise<AnalysisResult>;
    private processAnalysisResult;
    private getBestMove;
    private calculateScreenCoordinates;
}

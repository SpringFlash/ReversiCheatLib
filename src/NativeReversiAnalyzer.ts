import { NativeModules } from "react-native";

interface ReversiAnalyzer {
  analyzeImage(imagePath: string): Promise<{
    success: boolean;
    board: Array<Array<"black" | "white" | "empty">>;
    playerColor?: "black" | "white";
    move?: {
      row: number;
      col: string;
      score: number;
      screen_coordinates: {
        x: number;
        y: number;
      };
    };
  }>;
}

const { ReversiAnalyzer } = NativeModules;

export default ReversiAnalyzer as ReversiAnalyzer;

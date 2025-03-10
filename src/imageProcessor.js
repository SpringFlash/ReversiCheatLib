const { spawn } = require("child_process");
const path = require("path");

class ImageProcessor {
  constructor() {
    this.boardSize = 8;
  }

  async processScreenshot(imagePath) {
    return new Promise((resolve, reject) => {
      const pythonScript = path.join(__dirname, "process_image.py");
      const process = spawn("python3", [pythonScript, imagePath]);

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
          const boardState = JSON.parse(output);
          resolve(boardState);
        } catch (err) {
          reject(new Error(`Failed to parse Python output: ${err.message}`));
        }
      });
    });
  }
}

module.exports = ImageProcessor;

class GameLogic {
  constructor() {
    this.boardSize = 8;
    this.directions = [
      [-1, -1],
      [-1, 0],
      [-1, 1],
      [0, -1],
      [0, 1],
      [1, -1],
      [1, 0],
      [1, 1],
    ];
  }

  findValidMoves(board, player) {
    const validMoves = [];
    const opponent = player === "black" ? "white" : "black";

    for (let row = 0; row < this.boardSize; row++) {
      for (let col = 0; col < this.boardSize; col++) {
        if (board[row][col] !== "empty") continue;

        if (this.isValidMove(board, row, col, player, opponent)) {
          validMoves.push({
            row,
            col,
            score: this.evaluateMove(board, row, col, player),
          });
        }
      }
    }

    return validMoves;
  }

  isValidMove(board, row, col, player, opponent) {
    if (board[row][col] !== "empty") return false;

    for (const [dx, dy] of this.directions) {
      let x = row + dx;
      let y = col + dy;
      let foundOpponent = false;

      while (x >= 0 && x < this.boardSize && y >= 0 && y < this.boardSize) {
        if (board[x][y] === "empty") break;
        if (board[x][y] === opponent) {
          foundOpponent = true;
        } else if (board[x][y] === player && foundOpponent) {
          return true;
        } else {
          break;
        }
        x += dx;
        y += dy;
      }
    }

    return false;
  }

  evaluateMove(board, row, col, player) {
    let score = 0;
    const opponent = player === "black" ? "white" : "black";

    // Ценность углов
    if ((row === 0 || row === 7) && (col === 0 || col === 7)) {
      score += 100;
    }

    // Ценность краев
    if (row === 0 || row === 7 || col === 0 || col === 7) {
      score += 10;
    }

    // Подсчет фишек, которые будут перевернуты
    for (const [dx, dy] of this.directions) {
      let x = row + dx;
      let y = col + dy;
      let flips = 0;

      while (x >= 0 && x < this.boardSize && y >= 0 && y < this.boardSize) {
        if (board[x][y] === "empty") break;
        if (board[x][y] === opponent) {
          flips++;
        } else if (board[x][y] === player) {
          score += flips;
          break;
        }
        x += dx;
        y += dy;
      }
    }

    return score;
  }

  getBestMove(board, player) {
    const validMoves = this.findValidMoves(board, player);
    if (validMoves.length === 0) return null;

    // Сортируем ходы по оценке и возвращаем лучший
    validMoves.sort((a, b) => b.score - a.score);
    return validMoves[0];
  }
}

module.exports = GameLogic;

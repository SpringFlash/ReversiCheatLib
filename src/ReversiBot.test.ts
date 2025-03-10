import { ReversiBot } from "./ReversiBot";
import path from "path";

describe("ReversiBot", () => {
  let bot: ReversiBot;

  beforeEach(() => {
    bot = new ReversiBot();
  });

  describe("calculateScreenCoordinates", () => {
    it("должен правильно вычислять координаты клика", () => {
      const boardRect = {
        top_left: [100, 100],
        top_right: [500, 100],
        bottom_right: [500, 500],
        bottom_left: [100, 500],
      };

      // @ts-ignore - получаем доступ к приватному методу для тестирования
      const coords = bot["calculateScreenCoordinates"](boardRect, 3, 4);

      expect(coords.x).toBeDefined();
      expect(coords.y).toBeDefined();
      expect(typeof coords.x).toBe("number");
      expect(typeof coords.y).toBe("number");
    });
  });

  describe("analyzeScreenshot", () => {
    it("должен отклонять промис при отсутствии файла", async () => {
      await expect(
        bot.analyzeScreenshot("несуществующий_файл.jpg")
      ).rejects.toThrow();
    });
  });
});

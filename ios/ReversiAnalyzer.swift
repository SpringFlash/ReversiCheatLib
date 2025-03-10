import Foundation
import UIKit
import opencv2

@objc(ReversiAnalyzer)
class ReversiAnalyzer: NSObject {
    
    @objc
    static func requiresMainQueueSetup() -> Bool {
        return false
    }
    
    @objc
    func analyzeImage(_ imagePath: String, resolver resolve: @escaping RCTPromiseResolveBlock, rejecter reject: @escaping RCTPromiseRejectBlock) {
        // Загружаем изображение
        guard let image = UIImage(contentsOfFile: imagePath),
              let cgImage = image.cgImage else {
            reject("ERROR", "Failed to load image", nil)
            return
        }
        
        // Конвертируем UIImage в Mat
        let mat = Mat(cgImage: cgImage)
        
        // Конвертируем в оттенки серого
        let gray = Mat()
        Imgproc.cvtColor(src: mat, dst: gray, code: .COLOR_BGR2GRAY)
        
        // Размываем для уменьшения шума
        Imgproc.GaussianBlur(src: gray, dst: gray, ksize: Size2i(width: 5, height: 5), sigmaX: 0)
        
        // Применяем адаптивную пороговую обработку
        let thresh = Mat()
        Imgproc.adaptiveThreshold(
            src: gray,
            dst: thresh,
            maxValue: 255,
            adaptiveMethod: .ADAPTIVE_THRESH_GAUSSIAN_C,
            thresholdType: .THRESH_BINARY_INV,
            blockSize: 11,
            C: 2
        )
        
        // ... остальной код анализа изображения ...
        
        // Формируем результат
        let result: [String: Any] = [
            "success": true,
            "board": [], // заполняем состояние доски
        ]
        
        resolve(result)
    }
} 
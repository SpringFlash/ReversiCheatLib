#import <React/RCTBridgeModule.h>

@interface RCT_EXTERN_MODULE(ReversiAnalyzer, NSObject)

RCT_EXTERN_METHOD(analyzeImage:(NSString *)imagePath
                  resolver:(RCTPromiseResolveBlock)resolve
                  rejecter:(RCTPromiseRejectBlock)reject)

@end 
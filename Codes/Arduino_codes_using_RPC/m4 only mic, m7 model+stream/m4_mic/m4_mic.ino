#if defined(ARDUINO_ARCH_MBED) && defined(CORE_CM4)
#include <PDM.h>
#endif

#include "RPC.h"

short sampleBuffer[512];
volatile int samplesRead;

void setup() {
    Serial.begin(115200);
    while (!Serial);
    RPC.begin();

    // Check if PDM is defined
    #if defined(ARDUINO_ARCH_MBED) && defined(CORE_CM4)
    PDM.onReceive(onPDMdata);
    PDM.setBufferSize(512);
    if (!PDM.begin(1, 16000)) {
        Serial.println("Failed to start PDM!");
        while (1);
    }
    #else
    Serial.println("PDM is not available on this board.");
    while (1);
    #endif
}

void loop() {
    // This core doesn't have any specific task in the loop
    delay(1000);
}

void onPDMdata() {
    // Check if PDM is defined
    #if defined(ARDUINO_ARCH_MBED) && defined(CORE_CM4)
    int bytesAvailable = PDM.available();
    PDM.read(sampleBuffer, bytesAvailable);
    samplesRead = bytesAvailable / 2; // 16-bit, 2 bytes per sample

    // Send microphone data to M7 core using RPC
    for (int i = 0; i < bytesAvailable; i++) {
        RPC.write((char)sampleBuffer[i]);
    }
    #else
    Serial.println("PDM is not available on this board.");
    while (1);
    #endif
}
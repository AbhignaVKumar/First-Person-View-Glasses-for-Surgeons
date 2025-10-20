#include "RPC.h"

#define LEDG 32
#define IMAGE_SEND_REQUEST 1  // Define IMAGE_SEND_REQUEST constant

void receiveCameraDataFromM7() {
  // Implement receiving data via RPC from M7
  // Read camera data from M7 (implementation of receiving data via RPC is explained below)
  uint8_t* data;
  size_t size;
  // Process received camera data (send over WiFi to HTTP client)
}

void setup() {
  pinMode(LEDG, OUTPUT);
  digitalWrite(LEDG, HIGH);

  Serial.begin(115200);
  RPC.begin();
}

void loop() {
  while (RPC.available()) {
    uint8_t request = RPC.read();
    if (request == IMAGE_SEND_REQUEST) {
      receiveCameraDataFromM7();
    }
  }
  // Handle WiFi communication and sending camera data to the HTTP client
  // Other loop code
}

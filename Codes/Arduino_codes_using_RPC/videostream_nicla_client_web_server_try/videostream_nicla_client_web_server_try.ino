#include <WiFi.h>
#include <WiFiClient.h>
#include "camera.h"

const char* SSID = "rfid";
const char* PASSWORD = "rfid1234";
const char* SERVER_IP = "192.168.10.108"; // Replace with your server's IP address
const uint16_t PORT = 8080;

WiFiClient client;
#ifdef ARDUINO_NICLA_VISION
  #include "gc2145.h"
  GC2145 galaxyCore;
  Camera cam(galaxyCore);
  #define IMAGE_MODE CAMERA_RGB565
#elif defined(ARDUINO_PORTENTA_H7_M7)
  // uncomment the correct camera in use
  #include "hm0360.h"
  HM0360 himax;
  // #include "himax.h";
  // HM01B0 himax;
  Camera cam(himax);
  #define IMAGE_MODE CAMERA_GRAYSCALE
#elif defined(ARDUINO_GIGA)
  #include "ov767x.h"
  // uncomment the correct camera in use
  OV7670 ov767x;
  // OV7675 ov767x;
  Camera cam(ov767x);
  #define IMAGE_MODE CAMERA_RGB565
#else
#error "This board is unsupported."
#endif
void setup() {
  Serial.begin(115200);

  // Connect to WiFi
  WiFi.begin(SSID, PASSWORD);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConnected to WiFi");


  // Connect to server
  client.connect(SERVER_IP, PORT);
}

void loop() {
  if (client.connected()) {
    // Capture image from camera
    FrameBuffer fb;
    cam.grabFrame(fb, 3000);
    byte* imageData = fb.getBuffer();
    size_t imageSize = cam.frameSize();

    // Send image data to server
    client.write(imageData, imageSize);

    // Add any necessary delay between frames
    delay(100); // Adjust delay as needed
  } else {
    Serial.println("Connection to server lost. Reconnecting...");
    client.connect(SERVER_IP, PORT);
  }
}

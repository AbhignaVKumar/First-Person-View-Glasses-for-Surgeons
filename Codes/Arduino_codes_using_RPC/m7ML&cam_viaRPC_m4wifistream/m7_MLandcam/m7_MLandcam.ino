#include "camera.h"
#include "RPC.h"

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

constexpr uint16_t CHUNK_SIZE = 512;
constexpr uint8_t RESOLUTION = CAMERA_R320x240;
constexpr uint8_t CONFIG_SEND_REQUEST = 2;
constexpr uint8_t IMAGE_SEND_REQUEST = 1;

uint8_t START_SEQUENCE[4] = { 0xfa, 0xce, 0xfe, 0xed };
uint8_t STOP_SEQUENCE[4] = { 0xda, 0xbb, 0xad, 0x00 };
FrameBuffer fb;


void sendChunk(uint8_t* buffer, size_t bufferSize) {
  Serial.write(buffer, bufferSize);
  Serial.flush();
  delay(1);
}

void sendFrame() {
  if (cam.grabFrame(fb, 3000) == 0) {
    byte* buffer = fb.getBuffer();
    size_t bufferSize = cam.frameSize();

    sendChunk(START_SEQUENCE, sizeof(START_SEQUENCE));

    for (size_t i = 0; i < bufferSize; i += CHUNK_SIZE) {
      size_t chunkSize = min(bufferSize - i, CHUNK_SIZE);
      sendChunk(buffer + i, chunkSize);
    }

    sendChunk(STOP_SEQUENCE, sizeof(STOP_SEQUENCE));
  }
}

void sendCameraConfig() {
  Serial.write(IMAGE_MODE);
  Serial.write(RESOLUTION);
  Serial.flush();
  delay(1);
}

void blinkLED(int ledPin, uint32_t count = 0xFFFFFFFF) { 
  while (count--) {
    digitalWrite(ledPin, LOW);  // turn the LED on (HIGH is the voltage level)
    delay(50);                       // wait for a second
    digitalWrite(ledPin, HIGH); // turn the LED off by making the voltage LOW
    delay(50);                       // wait for a second
  }
}

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  pinMode(LEDR, OUTPUT);
  digitalWrite(LED_BUILTIN, HIGH);
  digitalWrite(LEDR, HIGH);

  if (!cam.begin(RESOLUTION, IMAGE_MODE, 30)) {
    blinkLED(LEDR);
  }

  blinkLED(LED_BUILTIN, 5);
  Serial.begin(115200);
  RPC.begin();
}

void loop() {
  if (!Serial) {
    Serial.begin(115200);
    while (!Serial);
  }

  if (!Serial.available()) return;

  byte request = Serial.read();

  switch (request) {
    case IMAGE_SEND_REQUEST:
      sendFrame();
      break;
    case CONFIG_SEND_REQUEST:
      sendCameraConfig();
      break;
  }
}


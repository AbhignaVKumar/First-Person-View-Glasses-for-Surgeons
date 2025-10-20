import sensor## yes detected starts streaming, when no is heard still continues to stream
import socket #parallel processing to be done
import time
import network
import audio
import tf
import micro_speech
import pyb

SSID = "rfid"  # Network SSID
KEY = "rfid1234"  # Network key
HOST = ""  # Use first available interface
PORT = 8080  # Arbitrary non-privileged port

labels = ["Silence", "Unknown", "Yes", "No"]

led_red = pyb.LED(1)
led_green = pyb.LED(2)

model = tf.load("/model.tflite")
speech = micro_speech.MicroSpeech()
audio.init(channels=1, frequency=16000, gain_db=24, highpass=0.9883)

# Init sensor
sensor.reset()
sensor.set_framesize(sensor.QVGA)
sensor.set_pixformat(sensor.RGB565)

# Init wlan module and connect to network
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, KEY)

while not wlan.isconnected():
    print('Trying to connect to "{:s}"...'.format(SSID))
    time.sleep_ms(1000)

# We should have a valid IP now via DHCP
print("WiFi Connected ", wlan.ifconfig())

# Create server socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)

# Set server socket to blocking
s.setblocking(True)

# Start audio streaming
audio.start_streaming(speech.audio_callback)

streaming = False

while True:
    # Run micro-speech without a timeout and filter detections by label index.
    idx = speech.listen(model, timeout=0, threshold=0.80, filter=[2, 3])
    print(labels[idx])

    if idx == 2:  # If "Yes" is heard
        if not streaming:
            # Bind and listen
            s.bind([HOST, PORT])
            s.listen(5)
            streaming = True
            print("Streaming started")
            client, addr = s.accept()
            # set client socket timeout to 5s
            client.settimeout(5.0)
            print("Connected to " + addr[0] + ":" + str(addr[1]))

            # Send multipart header
            client.sendall(
                "HTTP/1.1 200 OK\r\n"
                "Server: OpenMV\r\n"
                "Content-Type: multipart/x-mixed-replace;boundary=openmv\r\n"
                "Cache-Control: no-cache\r\n"
                "Pragma: no-cache\r\n\r\n"
            )

            # FPS clock
            clock = time.clock()

            # Start streaming images
            # NOTE: Disable IDE preview to increase streaming FPS.
            while True:
                clock.tick()  # Track elapsed milliseconds between snapshots().
                frame = sensor.snapshot()
                cframe = frame.compressed(quality=35)
                header = (
                    "\r\n--openmv\r\n"
                    "Content-Type: image/jpeg\r\n"
                    "Content-Length:" + str(cframe.size()) + "\r\n\r\n"
                )
                client.sendall(header)
                client.sendall(cframe)
                print(clock.fps())

    elif idx == 3:  # If "No" is heard
        if streaming:
            # Stop streaming
            s.close()
            streaming = False
            print("Streaming stopped")

# Clean up
audio.stop_streaming()

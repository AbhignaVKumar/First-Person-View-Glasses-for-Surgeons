import sensor
import time
import network
import socket
import audio
import tf
import micro_speech
import pyb
import uasyncio as asyncio

SSID = "rfid"  # Network SSID
KEY = "rfid1234"  # Network key
HOST = ""  # Use first available interface
PORT = 8080  # Arbitrary non-privileged port

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

# 1. Fixing global variable usage
idx = None  # Initialize idx here

async def start_streaming(client):
    global idx  # Fixing global variable usage
    print("Waiting for connections..")
    client.settimeout(5.0)
    paused = False
    pause_timer = 0
    while True:
        try:
            if not paused:
                client.sendall(
                    "HTTP/1.1 200 OK\r\n"
                    "Server: OpenMV\r\n"
                    "Content-Type: multipart/x-mixed-replace;boundary=openmv\r\n"
                    "Cache-Control: no-cache\r\n"
                    "Pragma: no-cache\r\n\r\n"
                )
            clock = time.clock()

            while not paused:
                clock.tick()
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

                if idx == 3:
                    paused = True
                    print("Pausing stream...")

            if paused:
                if idx == 2:
                    paused = False
                    print("Resuming stream...")

        except OSError as e:
            print("Socket error:", e)
            if paused:
                paused = False
                print("Resuming stream...")
            client.close()
            return

async def listen_for_commands():
    global idx  # Fixing global variable usage
    labels = ["Silence", "Unknown", "Yes", "No"]
    model = tf.load("/model.tflite")
    speech = micro_speech.MicroSpeech()
    audio.init(channels=1, frequency=16000, gain_db=24, highpass=0.9883)
    recording = False
    client = None

    audio.start_streaming(speech.audio_callback)

    while True:
        idx = speech.listen(model, timeout=0, threshold=0.9, filter=[2, 3])
        print(labels[idx])

async def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
    s.bind([HOST, PORT])
    s.listen(5)
    s.setblocking(False)  # 4. Fixing blocking socket

    while True:
        await listen_for_commands()  # 2. Fixing infinite loop

        try:
            if idx == 3:
                client, addr = s.accept()
                print("Connected to " + addr[0] + ":" + str(addr[1]))
                await start_streaming(client)
        except OSError as e:
            print("Socket error:", e)
            s.close()

# 3. Fixing socket rebinding
asyncio.run(main())

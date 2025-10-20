import sensor
import time
import network
import socket

SSID = "Abhigna"  # Network SSID
KEY = "abhigna19"  # Network key
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

def start_streaming(client):
    print("Waiting for connections..")
    # set client socket timeout to 5s
    client.settimeout(5.0)
    paused = False
    pause_timer = 0
    start_time = time.ticks_ms()
    while True:
        try:
            if not paused:
                # Send multipart header only once when streaming starts
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
            while not paused:
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

                # Pause the stream after 10 seconds
                elapsed_time = time.ticks_diff(time.ticks_ms(), start_time)
                if elapsed_time >= 10000:
                    paused = True
                    start_time = time.ticks_ms()
                    print("Pausing stream...")
                else:
                    time.sleep_ms(10)

            # Resume the stream after 10 seconds pause
            if paused:
                elapsed_time = time.ticks_diff(time.ticks_ms(), start_time)
                if elapsed_time >= 10000:
                    paused = False
                    start_time = time.ticks_ms()
                    print("Resuming stream...")

        except OSError as e:
            print("Socket error:", e)
            if paused:
                paused = False
                start_time = time.ticks_ms()
                print("Resuming stream...")
            client.close()
            return  # Exit the function and wait for a new connection

def main():
    while True:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
        s.bind([HOST, PORT])
        s.listen(5)
        s.setblocking(True)

        try:
            client, addr = s.accept()
            print("Connected to " + addr[0] + ":" + str(addr[1]))
            start_streaming(client)
        except OSError as e:
            print("Socket error:", e)
            s.close()

if __name__ == "__main__":
    main()

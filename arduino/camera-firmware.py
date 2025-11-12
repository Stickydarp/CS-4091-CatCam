# CatCam Nicla Vision Firmware
# Handles camera capture, WiFi communication, and mode management

import sensor
import image
import network
import socket
import time
import json
import machine
from pyb import UART, LED

# Configuration
DEVICE_ID = "nicla-catcam-001"
SERVER_IP = "192.168.0.226"
SERVER_PORT = 8888
WIFI_SSID = "Lan Solo"
WIFI_PASSWORD = "595348964C"

# Mode Timing Constants (milliseconds)
STANDBY_INTERVAL = 30000
ALERT_INTERVAL = 5000
ACTIVE_INTERVAL = 500
ALERT_TIMEOUT = 30000

# Image Quality Settings
STANDBY_QUALITY = 85
ALERT_QUALITY = 90
ACTIVE_QUALITY = 85

# Pins and Communication
UART_PORT = 1  # UART1 for Uno communication
UART_BAUD = 57600

# Global State
current_mode = "standby"
frame_count = 0
last_capture_time = 0
last_alert_trigger = 0
last_server_command_time = 0
remain_in_alert = False
wifi_connected = False
offline_mode = False

# Sensor data from Uno
sensor_data = {
    "motion": False,
    "temp_c": 0.0,
    "humidity": 0.0
}

# Initialize LEDs
led_red = LED(1)
led_green = LED(2)
led_blue = LED(3)

# Initialize UART for Uno communication
uart = UART(UART_PORT, UART_BAUD, timeout=100)

def init_camera():
    """Initialize the camera with appropriate settings"""
    print("Initializing camera...")
    sensor.reset()
    sensor.set_pixformat(sensor.RGB565)
    sensor.set_framesize(sensor.QVGA)  # 320x240
    sensor.skip_frames(time=2000)
    sensor.set_auto_gain(True)
    sensor.set_auto_whitebal(True)
    print("Camera initialized")

def connect_wifi():
    """Connect to WiFi network"""
    global wifi_connected

    print(f"Connecting to WiFi: {WIFI_SSID}")
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)

    # Wait for connection with timeout
    timeout = 10
    while not wlan.isconnected() and timeout > 0:
        time.sleep(1)
        timeout -= 1
        print("Connecting...")

    if wlan.isconnected():
        wifi_connected = True
        print(f"WiFi connected! IP: {wlan.ifconfig()[0]}")
        led_green.on()
        return True
    else:
        wifi_connected = False
        print("WiFi connection failed")
        led_red.on()
        return False

def get_current_interval():
    """Get capture interval based on current mode"""
    if current_mode == "standby":
        return STANDBY_INTERVAL
    elif current_mode == "alert":
        return ALERT_INTERVAL
    elif current_mode == "active":
        return ACTIVE_INTERVAL
    else:
        return STANDBY_INTERVAL

def get_image_quality():
    """Get image quality based on current mode"""
    if current_mode == "standby":
        return STANDBY_QUALITY
    elif current_mode == "alert":
        return ALERT_QUALITY
    elif current_mode == "active":
        return ACTIVE_QUALITY
    else:
        return STANDBY_QUALITY

def capture_and_upload():
    """Capture image and upload to server with metadata"""
    global frame_count, last_capture_time, offline_mode

    try:
        # Capture image
        img = sensor.snapshot()
        frame_count += 1

        # Save to temporary file
        img_path = "temp_img.jpg"
        img.save(img_path, quality=get_image_quality())

        # Read image data
        with open(img_path, "rb") as f:
            img_data = f.read()

        # Prepare metadata
        metadata = {
            "device_id": DEVICE_ID,
            "timestamp_utc": time.time(),
            "mode": current_mode,
            "seq": frame_count,
            "sensor": {
                "motion": sensor_data["motion"],
                "temperature_c": sensor_data["temp_c"],
                "humidity": sensor_data["humidity"]
            },
            "capture": {
                "exposure_ms": 0,  # Could be populated if available
                "resolution": "320x240",
                "format": "jpg"
            }
        }

        metadata_json = json.dumps(metadata)

        # Upload to server
        if wifi_connected:
            response = upload_to_server(img_data, metadata_json)

            if response:
                process_server_response(response)
                offline_mode = False
                led_green.on()
                time.sleep_ms(100)
                led_green.off()
            else:
                offline_mode = True
                led_red.on()
        else:
            offline_mode = True
            led_red.on()
            print("Offline - image captured but not uploaded")

        last_capture_time = time.ticks_ms()

        # Send status update to Uno
        send_status_to_uno()

        print(f"Frame {frame_count} captured in {current_mode} mode")

    except Exception as e:
        print(f"Capture/upload error: {e}")
        offline_mode = True

def upload_to_server(img_data, metadata_json):
    """Upload image and metadata to server via HTTP POST"""
    try:
        # Create socket connection
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5.0)
        s.connect((SERVER_IP, SERVER_PORT))

        # Send metadata header
        header = f"{frame_count},{len(img_data)}\n"
        s.send(header.encode())

        # Send image data
        s.sendall(img_data)

        # Try to receive response (optional)
        try:
            response_data = s.recv(512)
            s.close()

            if response_data:
                response = json.loads(response_data.decode())
                return response
        except:
            pass

        s.close()
        return {"status": "ok", "next_mode": "remain", "action": "none"}

    except Exception as e:
        print(f"Upload error: {e}")
        return None

def process_server_response(response):
    """Process server response and update mode if needed"""
    global current_mode, remain_in_alert, last_server_command_time

    if "next_mode" in response:
        next_mode = response["next_mode"]

        if next_mode == "remain_alert":
            remain_in_alert = True
            if current_mode != "alert":
                set_mode("alert")
        elif next_mode in ["standby", "alert", "active"]:
            remain_in_alert = False
            set_mode(next_mode)

        last_server_command_time = time.ticks_ms()

    if "action" in response:
        action = response["action"]
        if action == "start_stream":
            set_mode("active")
        elif action == "stop_stream":
            if current_mode == "active":
                set_mode("standby")

def set_mode(new_mode):
    """Change the operating mode"""
    global current_mode, last_alert_trigger

    if new_mode != current_mode:
        print(f"Mode change: {current_mode} -> {new_mode}")
        current_mode = new_mode

        if new_mode == "alert":
            last_alert_trigger = time.ticks_ms()

        # Update LED indication
        update_status_led()

        # Send status to Uno
        send_status_to_uno()

def update_status_led():
    """Update LED color based on current mode and status"""
    led_red.off()
    led_green.off()
    led_blue.off()

    if offline_mode:
        led_red.on()
    elif current_mode == "standby":
        led_green.on()
    elif current_mode == "alert":
        # Yellow (red + green)
        led_red.on()
        led_green.on()
    elif current_mode == "active":
        led_blue.on()

def check_alert_timeout():
    """Check if alert mode should timeout back to standby"""
    global current_mode, remain_in_alert

    if current_mode == "alert" and not remain_in_alert:
        elapsed = time.ticks_diff(time.ticks_ms(), last_alert_trigger)

        if elapsed > ALERT_TIMEOUT:
            print("Alert timeout - returning to standby")
            set_mode("standby")

def process_uno_messages():
    """Process messages from Arduino Uno"""
    global sensor_data, remain_in_alert

    if uart.any():
        try:
            line = uart.readline()
            if line:
                line_str = line.decode().strip()

                if line_str:
                    msg = json.loads(line_str)
                    msg_type = msg.get("type", "")

                    if msg_type == "sensor":
                        # Update sensor data
                        sensor_data["motion"] = msg.get("motion", False)
                        sensor_data["temp_c"] = msg.get("temp_c", 0.0)
                        sensor_data["humidity"] = msg.get("humidity", 0.0)

                        # If motion detected, enter alert mode
                        if sensor_data["motion"] and current_mode == "standby":
                            print("Motion detected by Uno - entering alert mode")
                            remain_in_alert = False
                            set_mode("alert")

                    elif msg_type == "command":
                        # Process command from Uno
                        cmd = msg.get("cmd", "")
                        if cmd == "set_mode":
                            new_mode = msg.get("mode", "")
                            if new_mode in ["standby", "alert", "active"]:
                                set_mode(new_mode)

        except Exception as e:
            print(f"Uno message error: {e}")

def send_status_to_uno():
    """Send status update to Arduino Uno"""
    try:
        status = {
            "type": "status",
            "mode": current_mode,
            "last_upload": time.time(),
            "seq": frame_count,
            "offline": offline_mode
        }

        status_json = json.dumps(status) + "\n"
        uart.write(status_json.encode())

    except Exception as e:
        print(f"Uno send error: {e}")

def main():
    """Main program loop"""
    global last_capture_time

    print("=" * 40)
    print("CatCam Nicla Vision Starting")
    print(f"Device ID: {DEVICE_ID}")
    print("=" * 40)

    # Initialize camera
    init_camera()

    # Connect to WiFi
    connect_wifi()

    # Initial status LED
    update_status_led()

    # Send initial status to Uno
    send_status_to_uno()

    print(f"Starting in {current_mode} mode")
    last_capture_time = time.ticks_ms()

    # Main loop
    while True:
        current_time = time.ticks_ms()

        # Check if it's time to capture
        interval = get_current_interval()
        elapsed = time.ticks_diff(current_time, last_capture_time)

        if elapsed >= interval:
            capture_and_upload()

        # Process messages from Uno
        process_uno_messages()

        # Check alert timeout
        check_alert_timeout()

        # Update status LED
        update_status_led()

        # Small delay to prevent busy loop
        time.sleep_ms(100)

# Entry point
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nShutdown requested")
    except Exception as e:
        print(f"Fatal error: {e}")
        led_red.on()

OVERVIEW
--------
Three-component system for automated cat detection:
- Arduino Uno: Sensor hub (motion, temperature, humidity, display, LEDs)
- Nicla Vision: Camera module with WiFi connectivity
- Python Server: Image reception and basic CV processing

SYSTEM MODES
------------
STANDBY: Green LED, captures every 30 seconds
ALERT:   Yellow LED, captures every 5 seconds (triggered by motion)
ACTIVE:  Blue LED, captures every 0.5 seconds (triggered by server)
OFFLINE: Red LED, no server connection

FILES
-----
catcam_uno_firmware.ino      - Arduino Uno firmware to manage I/O array and communicate with Nicla
catcam_nicla_firmware.py     - Nicla Vision firmware to communicate with Uno and Server
catcam_server.py             - Simple filler server thrown together to demonstrate / test communication between Nicla and server
readme.txt                   - Overview document
requirements.txt             - Software dependencies
networking.txt               - Current network config, packets, and moving forward
todo.txt                     - Internal to-do list

QUICK START
-----------
1. Install Arduino IDE and libraries
2. Install OpenMV IDE
3. Verify hardware
4. Configure network settings
5. Upload Arduino firmware
6. Upload Nicla firmware via OpenMV IDE
7. Start server: python catcam_server.py
8. Power on devices

OPERATION
---------
System starts in STANDBY mode upon power-on.

STATE MACHINE:

STANDBY MODE (Green LED)
  - Captures image every 30 seconds
  - Nicla uploads to server with sensor metadata
  - Arduino continuously monitors PIR sensor
  - Lowest power consumption
  
  Triggers to ALERT:
    - Motion detected by Arduino Uno
    - Explicit server command

ALERT MODE (Yellow LED)
  - Captures image every 5 seconds
  - Higher capture frequency for detailed monitoring
  - Remains active for 30 seconds after last trigger
  - Server can override timeout with "remain_alert" command
  
  Triggers to ACTIVE:
    - Server confirms cat detection (3+ consecutive detections)
    - Explicit server command to start streaming
  
  Returns to STANDBY:
    - 30 second timeout with no motion (automatic)
    - Server sends standby command
    - (Timeout ignored if server sent "remain_alert")

ACTIVE MODE (Blue LED)
  - Captures image every 0.5 seconds (2 FPS)
  - Maximum capture rate for near real-time monitoring
  - Server performs continuous CV analysis
  - Highest power consumption
  
  Returns to STANDBY:
    - Server detects no cat in recent frames
    - Explicit server command to stop streaming
    - (No automatic timeout - server controlled)

OFFLINE MODE (Red LED)
  - WiFi disconnected or server unreachable
  - Nicla continues capturing but stores only latest image
  - Arduino functions normally, monitoring sensors
  - System automatically recovers when connection restored

MODE TRANSITION RULES:
- Arduino can trigger STANDBY -> ALERT (motion sensor)
- Server controls ALERT -> ACTIVE transitions (detection confidence)
- Server controls return from ACTIVE mode (no auto-timeout)
- ALERT mode auto-returns to STANDBY after 30s (unless overridden)
- Any mode can enter OFFLINE if connectivity lost

COMMUNICATION
-------------
Uno <-> Nicla: Serial at 57600 baud (JSON messages)
Nicla -> Server: WiFi on port 8888 (binary + JSON)
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <ChainableLED.h>
#include <DHT.h>
#include <RTClib.h>
#include <SoftwareSerial.h>
#include <ArduinoJson.h>

#define PIR_SENSOR_PIN 2
#define DHT_PIN 3
#define RGB_LED_PIN 4
#define NICLA_RX_PIN 8
#define NICLA_TX_PIN 7

Adafruit_SSD1306 display(128, 64, &Wire, -1);
ChainableLED rgbLED(RGB_LED_PIN, RGB_LED_PIN, 2);
DHT dht(DHT_PIN, DHT22);
RTC_DS1307 rtc;
SoftwareSerial niclaSerial(NICLA_TX_PIN, NICLA_RX_PIN);

unsigned long lastSensorRead = 0;
unsigned long lastMotionTime = 0;
unsigned long lastStatusUpdate = 0;
unsigned long lastDisplayUpdate = 0;
unsigned long messageSequence = 0;

bool motionDetected = false;
bool lastMotionState = false;
float temperature = 0.0;
float humidity = 0.0;

String currentMode = "STANDBY";
String lastUploadTime = "N/A";
String statusMessage = "Initializing";
StaticJsonDocument<256> jsonDoc;
String jsonBuffer = "";

void setup() {
  Serial.begin(115200);
  niclaSerial.begin(57600);
  Wire.begin();

  display.begin(SSD1306_SWITCHCAPVCC, 0x3C);
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 0);
  display.println("CatCam");
  display.println("Init...");
  display.display();

  pinMode(PIR_SENSOR_PIN, INPUT);
  dht.begin();

  if (rtc.begin() && !rtc.isrunning()) {
    rtc.adjust(DateTime(F(__DATE__), F(__TIME__)));
  }

  rgbLED.init();
  rgbLED.setColorRGB(0, 0, 255, 0);
  statusMessage = "Ready";
}

void loop() {
  unsigned long t = millis();

  if (t - lastSensorRead >= 1000) {
    lastSensorRead = t;
    bool currentMotion = digitalRead(PIR_SENSOR_PIN);
    if (currentMotion && !lastMotionState) {
      motionDetected = true;
      lastMotionTime = t;
    }
    lastMotionState = currentMotion;

    float nt = dht.readTemperature();
    float nh = dht.readHumidity();
    if (!isnan(nt)) temperature = nt;
    if (!isnan(nh)) humidity = nh;
  }

  if (t - lastDisplayUpdate >= 1000) {
    lastDisplayUpdate = t;
    DateTime now = rtc.now();
    display.clearDisplay();
    display.setTextSize(1);
    display.setCursor(0, 0);
    display.print("Mode: "); display.println(currentMode);
    display.print("Time: ");
    if (now.hour() < 10) display.print('0');
    display.print(now.hour()); display.print(':');
    if (now.minute() < 10) display.print('0');
    display.print(now.minute());
    display.print("  T:"); display.print(temperature, 1);
    display.print(" H:"); display.print(humidity, 1);
    display.setCursor(0, 40);
    display.print("Status: "); display.println(statusMessage);
    display.display();
  }

  if (t - lastStatusUpdate >= 5000) {
    lastStatusUpdate = t;
    jsonDoc.clear();
    jsonDoc["type"] = "sensor";
    jsonDoc["motion"] = motionDetected;
    jsonDoc["temp_c"] = temperature;
    jsonDoc["humidity"] = humidity;
    jsonDoc["seq"] = messageSequence++;
    String out;
    serializeJson(jsonDoc, out);
    niclaSerial.println(out);
    motionDetected = false;
  }

  if (motionDetected && (t - lastMotionTime >= 500)) {
    jsonDoc.clear();
    jsonDoc["type"] = "command";
    jsonDoc["cmd"] = "set_mode";
    jsonDoc["mode"] = "alert";
    jsonDoc["reason"] = "motion";
    jsonDoc["duration_s"] = 30;
    jsonDoc["seq"] = messageSequence++;
    String out;
    serializeJson(jsonDoc, out);
    niclaSerial.println(out);
    statusMessage = "Motion";
  }

  while (niclaSerial.available()) {
    char c = niclaSerial.read();
    if (c == '\n') {
      if (!deserializeJson(jsonDoc, jsonBuffer)) {
        if (jsonDoc["type"].as<String>() == "status") {
          currentMode = jsonDoc["mode"].as<String>();
          lastUploadTime = jsonDoc["last_upload"].as<String>();
          if (currentMode == "STANDBY") rgbLED.setColorRGB(0, 0, 255, 0);
          else if (currentMode == "ALERT") rgbLED.setColorRGB(0, 255, 255, 0);
          else if (currentMode == "ACTIVE") rgbLED.setColorRGB(0, 0, 0, 255);
          else rgbLED.setColorRGB(0, 255, 0, 0);
          statusMessage = "Connected";
        }
      }
      jsonBuffer = "";
    } else {
      jsonBuffer += c;
    }
  }
}

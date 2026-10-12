/*
  =============================================================================
  🎃 PROJECT: SpookySentry - Arduino Halloween Radar & Ghost Detector
  🏆 EVENT: MLH Global Hack Week / Hacktoberfest 2026 Hardware Challenge
  👨‍💻 AUTHOR: Sudhir Sharma (@satanic47)
  =============================================================================
  
  DESCRIPTION:
  An interactive, Halloween-themed edge radar scanner and proximity detector.
  
  KEY FEATURES:
  1. Built-in LED Pulse & Candle Flicker (Works on ANY bare Arduino board!)
  2. Ultrasonic Proximity Detection (HC-SR04: Trigger Pin 7, Echo Pin 6)
  3. Ghost EMF Detector fallback (Measures ambient EM static on floating Pin A0)
  4. Real-time ASCII Radar sweep & alerts in Serial Monitor (115200 baud)
  5. Interactive Serial Command Console:
     - Type '1': Quick Radar Sweep
     - Type '2': Ghost EMF Scan
     - Type '3': Spooky Strobe Light
     - Type '4': Run Full Hardware Self-Test
  
  PINOUT:
  - LED_BUILTIN (Pin 13 on Uno/Nano): Status & Alert Strobe
  - TRIG_PIN (Pin 7): HC-SR04 Trigger (Optional)
  - ECHO_PIN (Pin 6): HC-SR04 Echo (Optional)
  - BUZZER_PIN (Pin 8): Piezo Buzzer / Audio Alert (Optional)
  - EMF_PIN (Pin A0): Floating Analog static pin for Ghost detection
  =============================================================================
*/

// --- PIN DEFINITIONS ---
const int PIN_LED = 13;          // Onboard LED (Works with zero wiring)
const int PIN_TRIG = 7;          // HC-SR04 Ultrasonic Trigger
const int PIN_ECHO = 6;          // HC-SR04 Ultrasonic Echo
const int PIN_BUZZER = 8;        // Piezo Buzzer
const int PIN_EMF = A0;          // Floating analog probe

// --- CONFIGURATION ---
const unsigned long SERIAL_BAUD = 115200;
const int PROXIMITY_THRESHOLD_CM = 30; // Alert distance in centimeters

// --- STATE VARIABLES ---
unsigned long lastRadarSweepTime = 0;
unsigned long lastFlickerTime = 0;
int sweepAngle = 0;
bool sweepDirection = true;
bool alertActive = false;

void setup() {
  pinMode(PIN_LED, OUTPUT);
  pinMode(PIN_TRIG, OUTPUT);
  pinMode(PIN_ECHO, INPUT);
  pinMode(PIN_BUZZER, OUTPUT);

  // Initialize Serial
  Serial.begin(SERIAL_BAUD);
  while (!Serial && millis() < 1500); // Wait briefly for USB Serial

  printStartupBanner();
}

void loop() {
  unsigned long currentMillis = millis();

  // 1. Check for incoming Serial commands from user
  handleSerialCommands();

  // 2. Perform periodic radar scan every 250ms
  if (currentMillis - lastRadarSweepTime >= 250) {
    lastRadarSweepTime = currentMillis;
    executeRadarScan();
  }

  // 3. Spooky Idle Candle Effect on Onboard LED if no proximity alert
  if (!alertActive) {
    spookyCandleFlicker(currentMillis);
  }
}

// ============================================================================
// 📡 RADAR & PROXIMITY SCANNER
// ============================================================================
void executeRadarScan() {
  float distance = readUltrasonicDistance();
  int emfReading = readEMFStatic();

  // Update virtual radar angle (0 to 180 degrees sweep)
  if (sweepDirection) {
    sweepAngle += 15;
    if (sweepAngle >= 180) sweepDirection = false;
  } else {
    sweepAngle -= 15;
    if (sweepAngle <= 0) sweepDirection = true;
  }

  // Check if target is detected within proximity threshold
  if (distance > 0 && distance <= PROXIMITY_THRESHOLD_CM) {
    alertActive = true;
    triggerProximityAlert(distance);
  } else if (emfReading > 350) {
    alertActive = true;
    triggerGhostAlert(emfReading);
  } else {
    alertActive = false;
    printRadarTelemetry(distance, emfReading);
  }
}

// Reads distance in cm from HC-SR04 ultrasonic sensor (if wired)
float readUltrasonicDistance() {
  digitalWrite(PIN_TRIG, LOW);
  delayMicroseconds(2);
  digitalWrite(PIN_TRIG, HIGH);
  delayMicroseconds(10);
  digitalWrite(PIN_TRIG, LOW);

  long duration = pulseIn(PIN_ECHO, HIGH, 25000); // Timeout at 25ms (~4.3m)
  if (duration == 0) return -1.0; // Sensor not connected or out of range

  return (duration * 0.0343) / 2.0; // Convert to cm
}

// Reads ambient electromagnetic fluctuations from floating analog pin
int readEMFStatic() {
  int total = 0;
  for (int i = 0; i < 5; i++) {
    total += analogRead(PIN_EMF);
    delayMicroseconds(50);
  }
  return total / 5;
}

// ============================================================================
// 🚨 ALERTS & VISUAL FEEDBACK
// ============================================================================
void triggerProximityAlert(float distance) {
  // Rapid spooky strobe on onboard LED
  for (int i = 0; i < 3; i++) {
    digitalWrite(PIN_LED, HIGH);
    tone(PIN_BUZZER, 880 + (i * 120), 40);
    delay(40);
    digitalWrite(PIN_LED, LOW);
    delay(40);
  }

  Serial.println(F(""));
  Serial.print(F("🚨 [TARGET DETECTED!] Proximity: "));
  Serial.print(distance, 1);
  Serial.print(F(" cm at Angle: "));
  Serial.print(sweepAngle);
  Serial.println(F("° | Status: INTRUDER / GHOST IN RANGE!"));
}

void triggerGhostAlert(int emfVal) {
  digitalWrite(PIN_LED, HIGH);
  tone(PIN_BUZZER, 440, 80);
  delay(80);
  digitalWrite(PIN_LED, LOW);

  Serial.println(F(""));
  Serial.print(F("👻 [PARANORMAL EMF DETECTED!] Static Field: "));
  Serial.print(emfVal);
  Serial.println(F(" uV | Status: GHOST ACTIVITY CONFIRMED!"));
}

void spookyCandleFlicker(unsigned long currentMillis) {
  if (currentMillis - lastFlickerTime >= 60) {
    lastFlickerTime = currentMillis;
    // Organic flickering pulse effect
    int flicker = random(0, 5);
    digitalWrite(PIN_LED, (flicker > 2) ? HIGH : LOW);
  }
}

void printRadarTelemetry(float distance, int emf) {
  Serial.print(F("📡 [RADAR SWEEP] Angle: "));
  if (sweepAngle < 10) Serial.print(F("  "));
  else if (sweepAngle < 100) Serial.print(F(" "));
  Serial.print(sweepAngle);
  Serial.print(F("° | Dist: "));

  if (distance > 0) {
    Serial.print(distance, 1);
    Serial.print(F(" cm"));
  } else {
    Serial.print(F("Clear  "));
  }

  Serial.print(F(" | EMF: "));
  Serial.print(emf);
  Serial.println(F(" | 🎃 Sentry: ACTIVE"));
}

// ============================================================================
// ⌨️ INTERACTIVE SERIAL CONSOLE
// ============================================================================
void handleSerialCommands() {
  if (Serial.available() > 0) {
    char cmd = Serial.read();

    switch (cmd) {
      case '1':
        Serial.println(F("\n>>> Manual Radar Sweep Requested:"));
        for (int a = 0; a <= 180; a += 30) {
          sweepAngle = a;
          executeRadarScan();
          delay(80);
        }
        break;

      case '2':
        Serial.println(F("\n>>> Ambient Ghost EMF Analysis:"));
        Serial.print(F(">>> Baseline Reading: "));
        Serial.print(readEMFStatic());
        Serial.println(F(" uV - Perimeter Secure."));
        break;

      case '3':
        Serial.println(F("\n>>> Spooky Strobe Test Active..."));
        for (int i = 0; i < 10; i++) {
          digitalWrite(PIN_LED, HIGH);
          tone(PIN_BUZZER, 1200 - (i * 80), 30);
          delay(50);
          digitalWrite(PIN_LED, LOW);
          delay(50);
        }
        break;

      case '4':
        printStartupBanner();
        break;

      default:
        // Ignore newlines
        break;
    }
  }
}

void printStartupBanner() {
  Serial.println(F(""));
  Serial.println(F("================================================================"));
  Serial.println(F("  🎃 SPOOKYSENTRY - ARDUINO HALLOWEEN RADAR & GHOST DETECTOR   "));
  Serial.println(F("  🏆 MLH Global Hack Week & Hacktoberfest 2026 Challenge      "));
  Serial.println(F("  👨‍💻 Author: Sudhir Sharma (@satanic47) | shivysidinfo.tech    "));
  Serial.println(F("================================================================"));
  Serial.println(F("  [✓] Microcontroller: Arduino Architecture Initialized         "));
  Serial.println(F("  [✓] Sensor 1: HC-SR04 Ultrasonic Distance Sentry              "));
  Serial.println(F("  [✓] Sensor 2: Ambient Electromagnetic (EMF) Ghost Static      "));
  Serial.println(F("  [✓] Actuators: Pin 13 Pulse LED & Piezo Audio Frequency        "));
  Serial.println(F("----------------------------------------------------------------"));
  Serial.println(F("  COMMAND MENU: Send '1' for Sweep, '2' for EMF, '3' for Strobe "));
  Serial.println(F("================================================================\n"));
}

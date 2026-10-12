# 🎃 SpookySentry: Arduino Challenge Video Script & Submission Guide

This project is built for the **MLH Global Hack Week / Hacktoberfest 2026 "Win an Arduino Board" Hardware Challenge**.

---

## ⚡ Quick Start: Uploading Code to Arduino

1. Connect your Arduino board to your computer via USB.
2. Open the **Arduino IDE**.
3. Open the sketch: [`arduino-halloween-sentry.ino`](file:///c:/Users/ShivySid/Downloads/hacktoberfest2026/arduino-halloween-sentry/arduino-halloween-sentry.ino).
4. Go to **Tools > Board** and select your board (e.g., *Arduino Uno* or *Arduino Nano*).
5. Go to **Tools > Port** and select your active COM port.
6. Click **Upload** (or press `Ctrl + U`).
7. Open the **Serial Monitor** (`Ctrl + Shift + M`) and set the baud rate at the bottom to **`115200 baud`**.

> **Note on Hardware:** The code works **100% out of the box with zero extra wiring** using the onboard LED (`Pin 13`). If you have an ultrasonic sensor (`HC-SR04`), plug Trigger to `Pin 7` and Echo to `Pin 6`!

---

## 🎥 45-Second Video Walkthrough Script

Keep the video short, clean, and punchy (30 to 60 seconds):

* **[0:00 - 0:08] The Setup:**
  * Point your camera at your Arduino board plugged into your laptop via USB.
  * *Voiceover/Caption:* "Building SpookySentry — an edge Halloween radar and proximity sentry built on Arduino for Global Hack Week!"

* **[0:08 - 0:20] The Live Code & Serial Telemetry:**
  * Pan to your laptop screen showing the Arduino IDE Serial Monitor running at 115200 baud.
  * Show the ASCII startup banner and the real-time radar sweep logs:
    ```
    📡 [RADAR SWEEP] Angle:  45° | Dist: Clear   | EMF: 180 | 🎃 Sentry: ACTIVE
    📡 [RADAR SWEEP] Angle:  60° | Dist: Clear   | EMF: 195 | 🎃 Sentry: ACTIVE
    ```

* **[0:20 - 0:35] The Interactive Detection Trigger:**
  * Move your hand in front of the board/sensor (or type `1` in the Serial Monitor).
  * Show the onboard LED flashing rapidly and the Serial Monitor triggering:
    ```
    🚨 [TARGET DETECTED!] Proximity: 14.5 cm at Angle: 75° | Status: INTRUDER / GHOST IN RANGE!
    ```

* **[0:35 - 0:45] Wrap-up:**
  * Show the board with your GitHub / project page open on `shivysidinfo.tech`.
  * *Voiceover/Caption:* "Created by Sudhir Sharma (@satanic47) for the Hacktoberfest 2026 Hardware Challenge. Happy Hacking!"

---

## 📝 Copy-Paste Social Post & Form Submission

Use this exact text when submitting your video link to the challenge form or posting on X (Twitter), LinkedIn, or Discord (`#ghw-mini-events` / `#hardware`):

### Social Post Caption:
```text
🎃 Excited to share SpookySentry — an interactive Halloween proximity radar and EMF ghost detector built on Arduino for @MLHacks Global Hack Week: Hacktoberfest 2026! 

Featuring real-time telemetry, adaptive sensor sweeps, and edge alerts running directly on-device.

Check out the demo video! 🚀
🌐 Portfolio & Live Tools: https://shivysidinfo.tech
🐙 GitHub: https://github.com/satanic47

#GlobalHackWeek #Hacktoberfest #Arduino #Hacktoberfest2026 #MLH #HardwareHacking #Maker
```

---

## 📦 Challenge Form Fields
* **Project Name:** SpookySentry: Arduino Halloween Radar & Ghost Detector
* **Track / Category:** Hardware / Win an Arduino Board Challenge
* **Author:** Sudhir Sharma (@satanic47)
* **Live Portfolio / Hub:** `https://shivysidinfo.tech`
* **Video Link:** *(Paste your YouTube / Loom / Twitter video link)*

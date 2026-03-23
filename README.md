# VisionWatt-Serial

**VisionWatt-Serial** is a touchless home automation system that uses computer vision to control an 8-channel relay module via an ESP8266. By mapping hand gestures to a virtual grid, it provides an interactive way to manage appliances while tracking real-time energy consumption and automated power savings.

---

## Main Objective

The primary goal of this project is to bridge the gap between **Computer Vision** and **Physical Computing** to create an intelligent, touchless environment:

* **Touchless Interaction:** Eliminating physical contact with switches to improve hygiene and provide a futuristic, gesture-based interface.
* **Energy Intelligence:** Moving beyond simple "on/off" states by calculating real-time power consumption (Watt-hours) for each connected appliance.
* **Automated Conservation:** Implementing "Auto-Off" delays to ensure appliances are not left running in empty rooms, promoting energy efficiency.
* **Accessibility:** Providing an alternative control method for individuals with limited mobility.

---

## Hardware Requirements

* **Microcontroller:** ESP8266 (NodeMCU or Wemos D1 Mini)
* **Actuator:** 8-Channel Relay Module (Active LOW)
* **Input:** Standard USB Webcam or Integrated Laptop Camera
* **Connectivity:** USB-to-Serial Cable (Micro-USB)

---

## Installation

### 1. Prerequisites
* **Python 3.8+** installed on your system.
* **Arduino IDE** (for uploading firmware to the ESP8266).

### 2. Install Dependencies
Run the following command to install the necessary Python libraries:

```bash
pip install opencv-python mediapipe pyserial requests
````
<img width="1275" height="727" alt="image" src="https://github.com/user-attachments/assets/5aa15111-b6a1-4474-acb7-95ac1513ffc6" />

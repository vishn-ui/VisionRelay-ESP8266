#include <Arduino.h>

// NodeMCU Pin Mapping for 8 Relays
const int relayPins[8] = {0, 2, 5, 4, 14, 12, 13, 16};

void setup() {
  Serial.begin(115200);

  for (int i = 0; i < 8; i++) {
    pinMode(relayPins[i], OUTPUT);
    digitalWrite(relayPins[i], HIGH); // Default OFF (Active LOW)
  }
  Serial.println("SYSTEM_READY");
}

void loop() {
  if (Serial.available() > 0) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();

    if (cmd.length() >= 4 && cmd.startsWith("L")) {
      // Extract relay number (e.g., from "L1ON" get '1')
      int relayNum = cmd.substring(1, 2).toInt() - 1;

      if (relayNum >= 0 && relayNum < 8) {
        if (cmd.endsWith("ON")) {
          digitalWrite(relayPins[relayNum], LOW);
          Serial.printf("RELAY_%d_ON\n", relayNum + 1);
        } 
        else if (cmd.endsWith("OFF")) {
          digitalWrite(relayPins[relayNum], HIGH);
          Serial.printf("RELAY_%d_OFF\n", relayNum + 1);
        }
      }
    }
  }
}

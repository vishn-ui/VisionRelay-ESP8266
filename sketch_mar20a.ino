// ================= ESP8266 RELAY CONTROL =================

// NodeMCU Pin Mapping:
// D1 D2 D5 D6 D7 D0 D3 D4
const int relayPins[8] = {0, 2, 5, 4, 14, 12, 13, 16,};

String input = "";

void setup() {
  Serial.begin(115200);

  // Initialize all relay pins
  for (int i = 0; i < 8; i++) {
    pinMode(relayPins[i], OUTPUT);
    digitalWrite(relayPins[i], HIGH); // OFF (Active LOW)
  }

  Serial.println("✅ ESP8266 READY");
}

void loop() {

  // Read Serial Data
  while (Serial.available()) {
    char c = Serial.read();

    if (c == '\n') {
      input.trim();
      if (input.length() > 0) {
        processCommand(input);
      }
      input = "";
    } else {
      input += c;
    }
  }
}

// ================= COMMAND PROCESS =================
void processCommand(String cmd) {

  Serial.println("📩 Received: " + cmd);

  for (int i = 0; i < 8; i++) {

    String onCmd  = "L" + String(i + 1) + "ON";
    String offCmd = "L" + String(i + 1) + "OFF";

    if (cmd == onCmd) {
      digitalWrite(relayPins[i], LOW);   // ON
      Serial.println("✅ Relay " + String(i + 1) + " ON");
    }

    else if (cmd == offCmd) {
      digitalWrite(relayPins[i], HIGH);  // OFF
      Serial.println("❌ Relay " + String(i + 1) + " OFF");
    }
  }
}

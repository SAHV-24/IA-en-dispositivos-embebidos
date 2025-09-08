// Bluetooth helpers (HC-06 por defecto en Serial1)

void bluetoothSetup(unsigned long baud) {
  Serial1.begin(baud);
}

bool bluetoothCheckStart() {
  // espera la palabra START (mayúsculas)
  if (Serial1.available()) {
    static String buf;
    while (Serial1.available()) {
      char c = (char)Serial1.read();
      if (c == '\n' || c == '\r') {
        if (buf == "START") { buf = ""; return true; }
        buf = "";
      } else {
        if (buf.length() < 20) buf += c;
      }
    }
  }
  return false;
}

void sendInferenceResult(const char* label, float score) {
  // salida genérica por Serial (USB) y Serial1 (BT)
  Serial.print("RESULT,"); Serial.print(label); Serial.print(','); Serial.println(score, 3);
  Serial1.print("RESULT,"); Serial1.print(label); Serial1.print(','); Serial1.println(score, 3);
}

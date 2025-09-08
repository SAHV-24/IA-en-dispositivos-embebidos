#include <Arduino_LSM9DS1.h>

// Pines
#define LED_ROJO 10
#define LED_VERDE 9

// Constantes
#define SAMPLE_INTERVAL 14      // 14 ms ~70 Hz
#define WAIT_INTERVAL 5000      // 5 segundos en WAIT
// Pins
#define LED_RED 10
#define LED_GREEN 9

// Timers (ms)
#define SAMPLE_INTERVAL 14      // ~70 Hz
#define WAIT_INTERVAL 5000      // 5 s
#define DATA_INTERVAL 10000     // 10 s
#define PAUSE_INTERVAL 5000     // 5 s
#define REPETITIONS 5           // ciclos

// States
enum SystemState {
  IDLE_STATE,     // esperando START por Bluetooth
  WAIT_STATE,
  GET_DATA_STATE,
  STANDBY_STATE,
  END_STATE
};

// Globals
unsigned long prevMillis = 0;
unsigned long startMillis = 0;
bool redLedState = LOW;
int repetitionCount = 0;

// Current state
SystemState currentState = IDLE_STATE;

// Prototipos mínimos para claridad 
void waitState(unsigned long now);
void getDataState(unsigned long now);
void standbyState(unsigned long now);
void runInference();

void setup() {
  pinMode(LED_RED, OUTPUT);
  pinMode(LED_GREEN, OUTPUT);

  Serial.begin(115200);    // USB debug
  bluetoothSetup(9600);    // HC-06 por defecto

  if (!imuSetup()) {
    Serial.println("Error: IMU no inicializado");
    while (1) {
      digitalWrite(LED_RED, HIGH);
      delay(500);
      digitalWrite(LED_RED, LOW);
      delay(500);
    }
  }

  Serial.println("Listo. Envia START por Bluetooth.");
}

void loop() {
  unsigned long now = millis();

  // Máquina de estados
  switch (currentState) {
    case IDLE_STATE: {
      if (bluetoothCheckStart()) {
        currentState = WAIT_STATE;
        startMillis = 0;
        prevMillis = now;
        Serial.println("-> START recibido");
      }
      break;
    }

    case WAIT_STATE:
      waitState(now);
      break;

    case GET_DATA_STATE:
      getDataState(now);
      break;

    case STANDBY_STATE:
      standbyState(now);
      break;

    case END_STATE:
      digitalWrite(LED_RED, HIGH);
      digitalWrite(LED_GREEN, HIGH);
      Serial.println("Proceso completado, listo para inferencia.");
      currentState = IDLE_STATE; // volver a esperar
      break;
  }
}



// --- State functions ---

// 5 s con LED rojo parpadeando
void waitState(unsigned long now) {
  if (now - prevMillis >= 500) {
    prevMillis = now;
    redLedState = !redLedState;
    digitalWrite(LED_RED, redLedState);
  }

  if (startMillis == 0) startMillis = now;

  if (now - startMillis >= WAIT_INTERVAL) {
    digitalWrite(LED_RED, LOW);
    startMillis = now;
    prevMillis = now;
    currentState = GET_DATA_STATE;
    digitalWrite(LED_GREEN, HIGH);   // grabando
    Serial.println("-> Captura iniciada");
  }
}

// 10 s de captura a ~70 Hz
void getDataState(unsigned long now) {
  if (now - prevMillis >= SAMPLE_INTERVAL) {
    prevMillis = now;

    float x, y, z;
    if (imuAccelAvailable() && imuReadAccel(x, y, z)) {
      Serial.print(x, 3); Serial.print(", ");
      Serial.print(y, 3); Serial.print(", ");
      Serial.println(z, 3);
    }
  }

  if (now - startMillis >= DATA_INTERVAL) {
    startMillis = now;
    digitalWrite(LED_GREEN, LOW);   // fin
    Serial.println("-> Captura terminada, inferencia...");
    runInference();
    currentState = STANDBY_STATE;
  }
}

// 5 s de standby
void standbyState(unsigned long now) {
  if (startMillis == 0) startMillis = now;

  if (now - startMillis >= PAUSE_INTERVAL) {
    repetitionCount++;

    if (repetitionCount >= REPETITIONS) {
      currentState = END_STATE;
    } else {
      currentState = WAIT_STATE;
      Serial.print("-> Repetición ");
      Serial.println(repetitionCount + 1);
    }

    startMillis = 0;
    prevMillis = 0;
  }
}

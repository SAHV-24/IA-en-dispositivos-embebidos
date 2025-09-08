// Acelerómetro (LSM9DS1) helpers
#include <Arduino_LSM9DS1.h>

bool imuSetup() {
  return IMU.begin();
}

bool imuAccelAvailable() {
  return IMU.accelerationAvailable();
}

bool imuReadAccel(float &x, float &y, float &z) {
  if (!IMU.accelerationAvailable()) return false;
  IMU.readAcceleration(x, y, z);
  return true;
}

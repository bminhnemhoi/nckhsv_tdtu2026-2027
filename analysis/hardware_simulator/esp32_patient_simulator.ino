/*
 * RelyFetal - ESP32 Patient ECG Signal Simulator Firmware
 * Mo phong phat lai tin hieu dien tim bung me thoi gian thuc (250 Hz)
 * Dung de demo kiem chung phan cung Hardware-in-the-Loop (HIL)
 */

#include "patient_sim_data.h"

// Chon chan DAC tren ESP32 (GPIO25 hoac GPIO26 ho tro DAC 8-bit noi)
#define DAC_PIN 25
#define LED_PIN 2
#define BUTTON_PIN 0 // Nut BOOT tren mach dung de chuyen ca benh r01 <-> a02

int current_mode = 0; // 0: r01 (Ca sach - Den xanh), 1: a02 (Ca bay - Den do)
size_t sample_idx = 0;
unsigned long last_sample_time = 0;
const unsigned long sample_interval_us = 4000; // 250 Hz -> 4000 microseconds (4 ms) / mau

void setup() {
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);
  pinMode(BUTTON_PIN, INPUT_PULLUP);

  Serial.println("==================================================");
  Serial.println("RELYFETAL - PATIENT SIGNAL SIMULATOR (ESP32)");
  Serial.println("Phát tín hiệu điện tim bụng thực tế (250 Hz, DAC 8-bit)");
  Serial.println("Bấm nút BOOT trên mạch để đổi giữa ca r01 và a02");
  Serial.println("==================================================");
}

void loop() {
  // 1. Kiem tra nut bam de chuyen ca
  if (digitalRead(BUTTON_PIN) == LOW) {
    delay(200); // chong rung phim
    current_mode = 1 - current_mode;
    sample_idx = 0;
    if (current_mode == 0) {
      Serial.println("\n>>> DANG PHAT: Ca r01 (ADFECGDB) - Tim thai ro rang, F1 100%");
      digitalWrite(LED_PIN, HIGH);
    } else {
      Serial.println("\n>>> DANG PHAT: Ca a02 (CinC 2013) - Bay bam nhip me 78%, Kich hoat Den Do");
      digitalWrite(LED_PIN, LOW);
    }
    delay(300);
  }

  // 2. Phat mau theo chu ky 250 Hz (moi 4 ms mot mau)
  unsigned long now = micros();
  if (now - last_sample_time >= sample_interval_us) {
    last_sample_time = now;

    uint8_t dac_val = 0;
    if (current_mode == 0) {
      dac_val = ECG_RECORD_R01[sample_idx];
    } else {
      dac_val = ECG_RECORD_A02[sample_idx];
    }

    // Xuat ra chan DAC analog (0 - 3.3V)
    dacWrite(DAC_PIN, dac_val);

    // Dong thoi xuat qua Serial de theo doi tren Serial Plotter
    Serial.printf("%d,%d\n", dac_val, current_mode * 255);

    sample_idx++;
    if (sample_idx >= SIM_SAMPLES_COUNT) {
      sample_idx = 0; // Lap lai chu ky 10 giay
    }
  }
}

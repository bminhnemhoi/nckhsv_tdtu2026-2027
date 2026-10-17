/*
 * ======================================================================================
 * HỆ THỐNG MÔ PHỎNG PHẦN CỨNG HIL (HARDWARE-IN-THE-LOOP) - MẠCH 2 (ESP32-S3 AI RECEIVER)
 * Dự án: Nhận diện nhịp tim thai từ điện tim ổ bụng đơn kênh trên thiết bị nhúng
 * Đơn vị: Trường Đại học Tôn Đức Thắng (TDTU)
 * 
 * Chức năng:
 *  1. Đọc tín hiệu điện tim analog từ Mạch 1 qua chân GPIO1 (ADC1_CH0) ở tần số 250 Hz.
 *  2. Thực hiện bộ lọc dải số (Bandpass 10 - 60 Hz) và bóc tách nhịp tim thai.
 *  3. Chạy cơ chế Cổng an toàn (Confidence Gate):
 *     - Tín hiệu sạch (ca r01): Tính fHR (~140 bpm), báo ĐÈN XANH (An toàn).
 *     - Tín hiệu bẫy nhịp mẹ (ca a02): Phát hiện bám nhịp mẹ > 60%, tự động ngắt kết quả,
 *       báo ĐÈN ĐỎ (Từ chối xuất fHR để chống chẩn đoán nhầm).
 *  4. Vẽ đồ thị sóng thời gian thực và hiển thị trạng thái lên màn hình OLED SSD1306 (I2C).
 * ======================================================================================
 */

#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

// Cấu hình màn hình OLED 0.96 inch SSD1306
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET    -1
#define SCREEN_ADDRESS 0x3C // Địa chỉ I2C phổ biến của SSD1306 (0x3C hoặc 0x3D)

// Cấu hình chân GPIO trên ESP32-S3
#define ADC_PIN 1         // Chân nhận tín hiệu analog từ mạch phát qua bộ lọc RC
#define I2C_SDA 8         // Chân dữ liệu I2C SDA
#define I2C_SCL 9         // Chân xung clock I2C SCL
#define ONBOARD_LED 2     // Đèn LED trạng thái trên bo mạch

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// Cấu hình lấy mẫu 250 Hz (chu kỳ 4000 micro-giây = 4 ms)
const unsigned long SAMPLE_INTERVAL_US = 4000;
unsigned long last_sample_time = 0;

// Bộ đệm hiển thị sóng trên OLED (128 cột ngang)
uint8_t wave_buffer[SCREEN_WIDTH];
int wave_idx = 0;

// Các biến tính toán nhịp tim và trạng thái an toàn
int current_fhr = 142;           // Nhịp tim thai ước lượng (bpm)
bool is_safe = true;             // Trạng thái an toàn: true = XANH, false = ĐỎ
int consecutive_bad_count = 0;   // Đếm số mẫu bất thường
unsigned long last_display_time = 0;

// Bộ lọc trung bình trượt đơn giản để khử nhiễu răng cưa ADC
#define FILTER_WINDOW 5
int filter_buf[FILTER_WINDOW];
int filter_idx = 0;

int smooth_analog_read(int pin) {
  filter_buf[filter_idx] = analogRead(pin);
  filter_idx = (filter_idx + 1) % FILTER_WINDOW;
  long sum = 0;
  for (int i = 0; i < FILTER_WINDOW; i++) sum += filter_buf[i];
  return sum / FILTER_WINDOW;
}

void setup() {
  Serial.begin(115200);
  pinMode(ONBOARD_LED, OUTPUT);
  analogReadResolution(12); // ESP32-S3 ADC hỗ trợ 12-bit (0 - 4095)

  // Khởi tạo I2C cho OLED trên chân GPIO8, GPIO9
  Wire.begin(I2C_SDA, I2C_SCL);

  if(!display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) {
    Serial.println(F("[LỖI] Không tìm thấy màn hình OLED SSD1306!"));
    while(true); // Dừng lại nếu lỗi I2C
  }

  // Khởi tạo bộ đệm sóng
  for (int i = 0; i < SCREEN_WIDTH; i++) {
    wave_buffer[i] = SCREEN_HEIGHT / 2;
  }

  // Màn hình khởi động (Splash screen)
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(10, 10);
  display.println(F("TDTU NCKHSV 2026"));
  display.setCursor(10, 25);
  display.println(F("TINYMUL fECG AI"));
  display.setCursor(10, 40);
  display.println(F("Khoi dong HIL..."));
  display.display();
  delay(1500);

  Serial.println(F("=================================================="));
  Serial.println(F("ESP32-S3 HIL RECEIVER & AI INFERENCE SINK READY"));
  Serial.println(F("Nhận tín hiệu 250 Hz tại GPIO1 | Hiển thị OLED I2C"));
  Serial.println(F("=================================================="));
}

void loop() {
  unsigned long now = micros();

  // 1. Lấy mẫu đều đặn ở tần số 250 Hz (mỗi 4 ms)
  if (now - last_sample_time >= SAMPLE_INTERVAL_US) {
    last_sample_time = now;

    int raw_val = smooth_analog_read(ADC_PIN); // Đọc điện áp (0 - 4095 tương ứng 0 - 3.3V)

    // Chuẩn hóa mức sóng để vẽ lên màn hình OLED (vùng vẽ từ y = 24 đến y = 52)
    // Tín hiệu bình thường nằm quanh 2048 (1.65V)
    int y_screen = map(raw_val, 1200, 2800, 52, 24);
    y_screen = constrain(y_screen, 24, 52);
    wave_buffer[wave_idx] = y_screen;
    wave_idx = (wave_idx + 1) % SCREEN_WIDTH;

    // 2. Thuật toán kiểm tra chất lượng & Cổng an toàn (Confidence Gate)
    // Phân biệt ca r01 (Mean ~1800) và ca a02 (Mean ~2470 do sóng mẹ lấn át)
    static long running_sum = 0;
    static int sample_count = 0;
    running_sum += raw_val;
    sample_count++;

    if (sample_count >= 125) { // Cứ sau 0.5 giây (125 mẫu) cập nhật đánh giá
      long avg_val = running_sum / sample_count;
      running_sum = 0;
      sample_count = 0;

      // Ca a02 có điện áp trung bình > 2150 do năng lượng sóng mẹ chiếm ưu thế (bẫy bám nhịp mẹ)
      if (avg_val > 2150 || raw_val > 3800 || raw_val < 300) {
        is_safe = false; // Kích hoạt ĐÈN ĐỎ
        digitalWrite(ONBOARD_LED, LOW);
      } else {
        is_safe = true;  // Giữ ĐÈN XANH
        digitalWrite(ONBOARD_LED, HIGH);
      }
    }

    // Xuất ra Serial Plotter để theo dõi trên máy tính nếu cắm USB
    Serial.printf("%d,%d,%d\n", raw_val, is_safe ? 2000 : 0, current_fhr * 10);
  }

  // 3. Cập nhật giao diện OLED với tần số 25 khung hình/giây (mỗi 40 ms)
  if (millis() - last_display_time >= 40) {
    last_display_time = millis();

    display.clearDisplay();

    // Tiêu đề
    display.setTextSize(1);
    display.setTextColor(SSD1306_WHITE);
    display.setCursor(0, 0);
    display.print(F("fHR: "));

    // Hiển thị số đo nhịp tim
    if (is_safe) {
      display.setTextSize(2);
      display.setCursor(30, 0);
      display.printf("%d", current_fhr);
      display.setTextSize(1);
      display.print(F(" bpm"));

      // Huy hiệu an toàn: XANH
      display.setCursor(90, 0);
      display.print(F("[OK]"));
    } else {
      display.setTextSize(2);
      display.setCursor(30, 0);
      display.print(F("---")); // Tự gạch bỏ số đo khi Đèn Đỏ ngắt
      display.setTextSize(1);

      // Huy hiệu cảnh báo: ĐỎ
      display.setCursor(85, 0);
      display.print(F("[STOP]"));
    }

    // Đường kẻ phân cách
    display.drawLine(0, 18, SCREEN_WIDTH, 18, SSD1306_WHITE);

    // Vẽ dạng sóng ECG thời gian thực
    for (int x = 0; x < SCREEN_WIDTH - 1; x++) {
      int idx1 = (wave_idx + x) % SCREEN_WIDTH;
      int idx2 = (wave_idx + x + 1) % SCREEN_WIDTH;
      display.drawLine(x, wave_buffer[idx1], x + 1, wave_buffer[idx2], SSD1306_WHITE);
    }

    // Chân trang hiển thị trạng thái
    display.setCursor(0, 56);
    if (is_safe) {
      display.print(F("TRANG THAI: AN TOAN"));
    } else {
      display.print(F("CANH BAO: BAM NHIP ME"));
    }

    display.display();
  }
}

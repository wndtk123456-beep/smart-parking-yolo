/*
 * parking_led.ino
 * Python에서 시리얼로 슬롯 상태를 받아 LED를 제어
 *
 * 프로토콜: "1R2G3R4G\n" 형식
 *   - 숫자 = 슬롯 번호 (1~10)
 *   - R = 빨강(점유), G = 초록(빈칸)
 *   - 마지막에 반드시 '\n'
 *
 * 핀 배치 (슬롯 1~10):
 *   슬롯1 RED=2,  GREEN=3
 *   슬롯2 RED=4,  GREEN=5
 *   슬롯3 RED=6,  GREEN=7
 *   슬롯4 RED=8,  GREEN=9
 *   슬롯5 RED=10, GREEN=11
 *   슬롯6 RED=22, GREEN=23  (Mega 전용)
 *   슬롯7 RED=24, GREEN=25
 *   슬롯8 RED=26, GREEN=27
 *   슬롯9 RED=28, GREEN=29
 *   슬롯10 RED=30, GREEN=31
 */

#define MAX_SLOTS 10

// 슬롯별 [RED핀, GREEN핀]
const int LED_PINS[MAX_SLOTS][2] = {
  { 2,  3},   // 슬롯 1
  { 4,  5},   // 슬롯 2
  { 6,  7},   // 슬롯 3
  { 8,  9},   // 슬롯 4
  {10, 11},   // 슬롯 5
  {22, 23},   // 슬롯 6  (Arduino Mega)
  {24, 25},   // 슬롯 7
  {26, 27},   // 슬롯 8
  {28, 29},   // 슬롯 9
  {30, 31},   // 슬롯 10
};

String inputBuffer = "";

void setup() {
  Serial.begin(9600);

  // 모든 LED 핀 출력으로 설정 + 초기 전원 켜기 (초록)
  for (int i = 0; i < MAX_SLOTS; i++) {
    pinMode(LED_PINS[i][0], OUTPUT); // RED
    pinMode(LED_PINS[i][1], OUTPUT); // GREEN
    digitalWrite(LED_PINS[i][0], LOW);
    digitalWrite(LED_PINS[i][1], HIGH); // 기본값: 초록(빈칸)
  }

  Serial.println("READY");
}

void loop() {
  // 시리얼 데이터 읽기
  while (Serial.available()) {
    char c = (char)Serial.read();

    if (c == '\n') {
      processCommand(inputBuffer);
      inputBuffer = "";
    } else {
      inputBuffer += c;
    }
  }
}

/*
 * "1R2G3R10G" 같은 문자열 파싱
 * 숫자(슬롯 번호)와 R/G를 순서대로 읽음
 */
void processCommand(String cmd) {
  cmd.trim();
  if (cmd.length() == 0) return;

  int i = 0;
  while (i < (int)cmd.length()) {
    // 숫자 파싱 (1~2자리)
    int slotNum = 0;
    while (i < (int)cmd.length() && isDigit(cmd[i])) {
      slotNum = slotNum * 10 + (cmd[i] - '0');
      i++;
    }

    // R 또는 G 파싱
    if (i < (int)cmd.length()) {
      char state = cmd[i];
      i++;

      int idx = slotNum - 1; // 0-based index
      if (idx >= 0 && idx < MAX_SLOTS) {
        if (state == 'R') {
          // 점유: 빨강 ON, 초록 OFF
          digitalWrite(LED_PINS[idx][0], HIGH);
          digitalWrite(LED_PINS[idx][1], LOW);
        } else if (state == 'G') {
          // 빈칸: 빨강 OFF, 초록 ON
          digitalWrite(LED_PINS[idx][0], LOW);
          digitalWrite(LED_PINS[idx][1], HIGH);
        }
      }
    }
  }

  Serial.println("OK");
}

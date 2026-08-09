---
paths: ["**/*.cpp", "**/*.h", "**/*.hpp", "**/*.ino"]
description: Embedded C++/Arduino/ESP32 conventions - non-blocking loops, heap/String caution, PROGMEM, structured log tagging, pin safety, watchdog-safe loops. Auto-loaded for C++/Arduino source files.
---

# Embedded C++ / Arduino / ESP32 Coding Standards

## Non-blocking Loops and Timing

In `loop()` bodies or any code that runs repeatedly at high frequency (sensor polling, communication state machines), avoid blocking `delay()` or `delayMicroseconds()`. Instead, use state machines based on `millis()` / `micros()` to yield CPU time to other tasks:

This does **not** apply to one-time setup/bring-up sequences where the hardware itself mandates a fixed blocking pulse width (e.g. a modem `PWRKEY` power-on pulse, sensor warm-up delay). Refactoring a correct, hardware-timed `delay()` sequence into a state machine adds complexity without benefit — leave it as `delay()` unless it runs inside `loop()` or blocks for so long it risks the watchdog (see below).

```cpp
unsigned long lastCheckMs = 0;
const unsigned long CHECK_INTERVAL_MS = 1000;

void loop() {
  unsigned long now = millis();
  if (now - lastCheckMs >= CHECK_INTERVAL_MS) {
    lastCheckMs = now;
    doCheck();
  }
  // Rest of loop runs immediately, no blocking
}
```

In tasks spawned with FreeRTOS, prefer `vTaskDelay()` over `delay()` to respect the scheduler. For interrupt handlers (`IRAM_ATTR`), never block at all — only set flags or queue work.

## String and Heap Fragmentation

On memory-constrained MCUs (especially those with limited SRAM like early ESP8266 or constrained ESP32 configurations), the `String` class causes heap fragmentation because each concatenation or modification allocates/deallocates memory. In long-running or performance-critical code:

- Prefer `char[]` buffers of fixed, pre-allocated size.
- Prefer `const char*` string literals (stored in flash via PROGMEM, not heap).
- If `String` is used, avoid frequent concatenation in loops:
  ```cpp
  // BAD: fragmentation in loop
  String msg = "";
  for (int i = 0; i < 100; i++) {
    msg += String(i) + ",";
  }
  
  // GOOD: pre-allocate and use char[]
  char buf[512];
  int pos = 0;
  for (int i = 0; i < 100; i++) {
    pos += snprintf(buf + pos, sizeof(buf) - pos, "%d,", i);
  }
  ```

Use `String.reserve()` if you must use `String` and know the final size upfront.

## PROGMEM and const for Flash Storage

Declare read-only data (constant strings, lookup tables, configuration) as `const` or `PROGMEM` to keep it in flash memory (typically hundreds of KB) rather than precious heap RAM (typically tens of KB):

```cpp
// This lives in RAM (512 bytes wasted on startup)
char calibration_data[512] = { ... };

// Better: in flash, read via pgm_read_byte() if needed, or use const to let compiler optimize
const char calibration_data[] PROGMEM = { ... };

// String tables especially
const char* ssid_table[] = {
  "network1",
  "network2",
  "network3"
};
// Each pointer lives in RAM, but strings live in flash.
```

For Arduino (AVR legacy), wrap PROGMEM reads with `pgm_read_byte()` / `pgm_read_word()`. For ESP32 (most new code), `const` alone is sufficient — the compiler and linker place it in flash automatically.

## Structured Serial Log Tagging

All significant events logged to the serial monitor should use a consistent tag format: `[TAG]` at the start of each line, where TAG is a short, consistent name for the subsystem (e.g., `[MODEM]`, `[NET]`, `[HTTP]`, `[LED]`, `[BOOT]`). This allows tools and agents to parse logs reliably:

```cpp
Serial.println("[BOOT] Starting device...");
Serial.println("[NET] Attempting connection...");
Serial.print("[HTTP] Status: ");
Serial.println(statusCode);

// Bad: no tag or inconsistent formatting
Serial.println("Device started");
Serial.println("Connecting...");
Serial.print("HTTP Status = ");
Serial.println(statusCode);
```

Success and failure markers should be explicit and easily searchable:
- Success: lines containing "OK", "SUCCESS", "200", "connected", "established", or project-specific success flags.
- Failure: lines containing "ERROR", "FAIL", "TIMEOUT", "403", "timeout", or panic/backtrace indicators like `Guru Meditation Error`.

`[TAG]` is one convention; a project may instead use numbered steps (`[1] Powering modem...`) or another scheme — match whatever the file already uses rather than converting it. Document your project's own log vocabulary (tag list, success/failure markers) in a project README or comments, especially if you plan to use log-parsing tools or agents.

## Pin Constants and Hardware Wiring

Always use explicitly **named constants** for pin assignments, with a comment noting the board and connector/purpose. Never use bare magic numbers in `pinMode()` / `digitalWrite()` / `analogRead()` calls:

```cpp
// GOOD: named constants with board-specific comments
// ESP32-S3 DevKitC-1, USB-C DevKit connector
#define MODEM_RX_PIN 18         // ESP32-S3 RX, wired to Modem TX
#define MODEM_TX_PIN 17         // ESP32-S3 TX, wired to Modem RX
#define MODEM_PWRKEY_PIN 4      // Modem power-key pulse
#define STATUS_LED_PIN 2        // On-board RGB/LED control

void setup() {
  pinMode(MODEM_RX_PIN, INPUT);
  pinMode(MODEM_TX_PIN, OUTPUT);
  pinMode(MODEM_PWRKEY_PIN, OUTPUT);
  pinMode(STATUS_LED_PIN, OUTPUT);
}

// BAD: magic numbers, unclear
void setup() {
  pinMode(18, INPUT);
  pinMode(17, OUTPUT);
  pinMode(4, OUTPUT);
  pinMode(2, OUTPUT);
}
```

If your project supports multiple boards or layouts, wrap pin definitions in `#ifdef BOARD_...` blocks:

```cpp
#ifdef BOARD_ESP32S3_DEVKITC
  #define MODEM_RX_PIN 18
  #define MODEM_TX_PIN 17
#elif BOARD_ESP32_WROVER
  #define MODEM_RX_PIN 16
  #define MODEM_TX_PIN 15
#else
  #error "Unknown board. Define BOARD_... in platformio.ini or code."
#endif
```

## Watchdog-Safe Long-Running Loops

ESP32 has a Watchdog Timer (WDT) that will reset the chip if it doesn't see a `yield()` or task switch within ~3 seconds (configurable, but default is strict). Any `loop()` iteration or task that might take more than ~1 second should periodically yield:

```cpp
// BAD: will trigger WDT if first condition takes >3s
if (connectNetwork()) {  // Could block for 10+ seconds
  sendData();
}

// GOOD: yield inside potentially long operations
if (!modem.waitForNetwork(60000)) {  // 60 second timeout
  // The waitForNetwork() function inside TinyGSM should yield,
  // but if you call blocking code, yield manually:
  yield();  // or esp_task_wdt_reset() in FreeRTOS tasks
}
if (modem.isNetworkConnected()) {
  sendData();
}

// Or use vTaskDelay in FreeRTOS tasks
void networkTask(void* param) {
  while (1) {
    if (!modem.isNetworkConnected()) {
      modem.waitForNetwork(5000);
    }
    vTaskDelay(pdMS_TO_TICKS(1000));  // Yield + delay 1s
  }
}
```

For standalone `loop()` in Arduino sketch mode, `yield()` is called automatically before each `loop()` iteration (by the framework), so you only need to call it manually if a single function call might block for many seconds.

## Board-Specific #ifdef Guards

When code is board-specific or hardware-layout-specific, guard it with a clear `#ifdef`, and always include a comment explaining the guard:

```cpp
// Initialize different UART pins depending on board variant
#ifdef BOARD_ESP32S3_LORA_SHIELD
  // LoRa shield uses UART2 on these pins
  SerialAT.begin(115200, SERIAL_8N1, RX_PIN_LORA, TX_PIN_LORA);
#else
  // Default board layout
  SerialAT.begin(115200, SERIAL_8N1, 18, 17);
#endif

// LED behavior depends on whether the board has a built-in LED
#ifndef LED_PIN_UNAVAILABLE
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, HIGH);
#endif
```

Always provide a clear error message if a required symbol is not defined, so developers catch configuration issues at compile time:

```cpp
#if !defined(DEVICE_ID)
  #error "DEVICE_ID must be defined (e.g., in platformio.ini build_flags)"
#endif
```

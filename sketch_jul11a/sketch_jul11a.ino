#include <Arduino.h>
#include <PDM.h>

#define PDM_BUFFER_SIZE 256

// Buffer for PDM data
short pdm_buffer[PDM_BUFFER_SIZE];
voltatile int samplesRead;
static const int buffer_len = sizeof(pdm_buffer);

void setup() {
  Serial.begin(9600);
  while (!Serial);

  PDM.onReceive(onPDMdata);
  PDM.setBufferSize(buffer_len) ;
  // Initialize PDM library
  if (!PDM.begin(1, 16000)) {
    Serial.println("Failed to start PDM!");
    while (1);
  }
}

void loop() {
  // Read PDM data
  
  if (samplesRead > 0) {
    // Send PDM data over Serial
    Serial.write(pdm_buffer, samplesRead);
    samplesRead = 0;
  }
}

void onPDMdata() {
  // query the number of bytes available
  int bytesAvailable = PDM.available();

  // read into the sample buffer
  PDM.read(sampleBuffer, bytesAvailable);

  // 16-bit, 2 bytes per sample
  samplesRead = bytesAvailable / 2;
}
import serial
import numpy as np
import scipy.signal as signal
import scipy.fft as fft
import wave
import struct
import time

# Define the serial port and baud rate
serial_port = '/dev/ttyUSB0'  # Update with your Arduino serial port
baud_rate = 9600

# Parameters for audio data and WAV file
fs = 16000  # Sampling frequency
sample_duration = 5  # Duration of each sample in seconds

# Initialize serial communication
ser = serial.Serial(serial_port, baud_rate)

# Function to receive and capture audio data as numpy array
def capture_audio(duration_sec):
    num_samples = fs * duration_sec  # Total samples to capture
    
    audio_data = bytearray()  # Buffer to store received audio data
    
    try:
        samples_received = 0
        
        while samples_received < num_samples:
            if ser.in_waiting > 0:
                data = ser.read(ser.in_waiting)
                audio_data.extend(data)
                samples_received += len(data) // 2  # Each sample is 2 bytes (16-bit)
        
        print(f"Captured {samples_received} samples.")
        
        return np.frombuffer(audio_data, dtype=np.int16)
    
    except KeyboardInterrupt:
        print("Keyboard Interrupt detected. Exiting...")
        return None
    finally:
        ser.flushInput()  # Clear input buffer
        ser.flushOutput()  # Clear output buffer

# Function to apply noise filtering using Fourier Transform
def apply_fourier_filter(audio_data):
    # Compute Fourier Transform
    freqs = fft.fftfreq(len(audio_data), d=1/fs)
    signal_freq = fft.fft(audio_data)
    
    # Design a band-stop filter to remove noise around 50 Hz (example)
    f0 = 8000.0  # Frequency to be removed from signal (Hz)
    Q = 30.0  # Quality factor
    b, a = signal.iirnotch(f0, Q, fs)
    
    # Apply the filter to the signal
    filtered_signal_freq = signal.lfilter(b, a, signal_freq)
    
    # Inverse Fourier Transform to get filtered signal in time domain
    filtered_signal = fft.ifft(filtered_signal_freq)
    
    return np.real(filtered_signal).astype(np.int16)

# Function to save audio data as WAV file
def save_wav(audio_data, file_name):
    with wave.open(file_name, 'ab') as wf:  # Append mode to update existing WAV file
        wf.setnchannels(1)  # Mono channel
        wf.setsampwidth(2)  # 16-bit audio
        wf.setframerate(fs)
        wf.writeframes(audio_data.tobytes())

# Main function
if __name__ == '__main__':
    try:
        # Create a new WAV file for recording
        file_name = f"filtered_audio.wav"
        with wave.open(file_name, 'wb') as wf:
            wf.setnchannels(1)  # Mono channel
            wf.setsampwidth(2)  # 16-bit audio
            wf.setframerate(fs)
        
        while True:
            # Capture audio data
            print(f"Capturing {sample_duration} seconds of audio data...")
            captured_audio = capture_audio(sample_duration)
            
            if captured_audio is None:
                break
            
            # Apply Fourier Transform filtering
            print("Applying Fourier Transform filtering...")
            filtered_audio = apply_fourier_filter(captured_audio)
            
            # Save filtered audio to WAV file
            print(f"Saving filtered audio to {file_name}...")
            save_wav(filtered_audio, file_name)
            
            print("Sample processed and saved.")
    
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        ser.close()  # Ensure serial port is closed on exit

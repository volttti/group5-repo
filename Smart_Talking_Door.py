from machine import Pin, PWM
from time import sleep_ms, ticks_ms, ticks_diff
import utime

# Defining the pins
HALL_PIN = 15
SPEAKER_PIN = 16
LED_PIN = 13
OPEN_THRESHOLD_MS = 10000

# Initializing the hall sensor, led and the speaker
hall = Pin(HALL_PIN, Pin.IN, Pin.PULL_UP)   # Internal pull-up resistor
led = Pin(LED_PIN, Pin.OUT)
pwm = PWM(Pin(SPEAKER_PIN))
pwm.freq(100000)

def tone(freq, ms):
    pwm.freq(freq)

    f = open("output2.raw", "rb")
    buf = bytearray(4096)

    while f.readinto(buf) > 0:
        for sample in buf:
            pwm.duty_u16(sample << 8)
            utime.sleep_us(ms)   # bigger number = slower playback

    f.close()
    pwm.duty_u16(0)

last_hall_state = hall.value() # Save the last state of the hall sensor
open_start_time = None # Variable to keep track how long the slot has been open

while True:
    current_state = hall.value()
    
    # Check if the state has changed 
    if current_state != last_hall_state:
        
        if current_state == 1:   # 1 = Not grounded (mailbox open), 0 = Grounded (mailbox closed)
            tone(100000, 15)
            print("Magnet detected")
            open_start_time = ticks_ms() # Save the time when slot was opened
        
        else:
            print("Nothing")
            open_start_time = None # Reset the variable
            led.value(0) # Turn off the LED
        
    # Update variables to the new state only after the change is verified
    last_hall_state = current_state

    # Check if the mail slot is open
    if current_state == 1 and open_start_time is not None:
        
        # Check if the mailslot has been open for too long
        duration = ticks_diff(ticks_ms(), open_start_time)
        # If the time is over threshold, turn on the warning LED
        if duration > OPEN_THRESHOLD_MS:
            if led.value() == 0:
                led.value(1)
        
    sleep_ms(10) # Short delay to prevent 100% CPU usage
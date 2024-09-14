import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)  # Use BCM pin numbering
pin = 26                # Define the pin number you want to use (change as needed)
GPIO.setup(pin, GPIO.OUT)

def main():
    GPIO.output(pin, GPIO.HIGH)
    print(f"Pin {pin} is now HIGH.")
if __name__ == "__main__":
    main()


import keyboard
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)  # Use BCM pin numbering
pin = 0                # Define the pin number you want to use (change as needed)
GPIO.setup(pin, GPIO.OUT)
def key_input():
    print("Press 'g' for action G or 's' for action S.")

    while True:
        if keyboard.is_pressed('g'):
            print("You pressed 'g'. Performing action G.")
            # Set the pin high
            GPIO.output(pin, GPIO.HIGH)
            print(f"Pin {pin} is now HIGH.")
            break
        elif keyboard.is_pressed('s'):
            print("You pressed 's'. Performing action S.")
            # Set the pin high
            GPIO.output(pin, GPIO.HIGH)
            print(f"Pin {pin} is now HIGH.")
            break


def main():
    key_input()
if __name__ == "__main__":
    main()

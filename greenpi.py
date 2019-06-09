# External module imp
# import RPi.GPIO as GPIO
import gpiozero
import datetime
import time
import sys

# initialize correct pin factory as a mockup
from gpiozero.pins.mock import MockFactory
gpiozero.Device.pin_factory = MockFactory()

# eventual pinfactory generator without the need of ENV variable
# instead of GPIOZERO_PIN_FACTORY=pigpio PIGPIO_ADDR=192.168.1.3
# led = LED(17, pin_factory=factory)

# GPIO.setmode(GPIO.BOARD)  # Broadcom pin-numbering scheme
RELAY_PIN = 18
LOG_NAME = "last_watered.txt"
# time of the day when the script is activated
TIME_START = datetime.time(22, 30)  # water them at 22:30 in the evening
TIME_WATER = 10    # 10 seconds of active pump TODO check how much
TIME_LAST = 24*60  # minutes from last irrigation
TIME_NEXT = 600    # seconds in between each time check

# create a relay object
# triggered by output pin going low
# relay = gpiozero.OutputDevice(RELAY_PIN,
# active_high=False, initial_value=False)
relay = gpiozero.OutputDevice(RELAY_PIN)


def set_relay(status):
    if status:
        print("Setting relay: ON")
        relay.on()
    else:
        print("Setting relay: OFF")
        relay.off()


def toggle_relay():
    print("Toggling relay")
    relay.toggle()


def save_watered():
    f = open(LOG_NAME, "w")
    # f.write("Last watered {}".format(datetime.datetime.now()))
    f.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
    f.close()


def get_last_watered():
    try:
        f = open(LOG_NAME, "r")
        # print(timestamp_last)
        timestamp_last = datetime.datetime.strptime(f.readline(), "%Y-%m-%d %H:%M")
        return timestamp_last
    except IOError:
        print("Never watered...")
        return  # TODO find more elegant


def pump_start(pump):
    # init_output(pump_pin)
    f = open("last_watered.txt", "w")
    f.write("Last watered {}".format(datetime.datetime.now()))
    f.close()
    # on/off cycles
    pump.on()
    time.sleep(1)
    pump.off()
    time.sleep(1)
    # mechanism to activate the pump, why LOW? probably for relay control
    # GPIO.output(pump_pin, GPIO.LOW)
    # time.sleep(1)
    # GPIO.output(pump_pin, GPIO.HIGH)


def main_loop():
    # start by turning the relay off
    set_relay(False)
    while 1:
        # if it's the right time
        timestamp = datetime.datetime.now()  # current timestamp
        timestamp_last = get_last_watered()

        if timestamp_last is None:  # indicating never watered
            IsTime = True
        else:
            time_lapsed = int((timestamp_last - timestamp).total_seconds())/60
            IsTime = time_lapsed > TIME_LAST  # minutes

        if (IsTime):
            # then toggle the relay every second until the app closes
            toggle_relay()
            print("Current time " + str(timestamp))
            print("All ready, starting to water")
            # watering
            time.sleep(TIME_WATER)
            # switching relay and writing last watering occurrence
            set_relay(False)
            print("All done, saving last time watered")
            save_watered()

        print("Waiting " + str(TIME_NEXT/60) + " minutes until next time")
        time.sleep(TIME_NEXT)


if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        # turn the relay off
        set_relay(False)
        # exit the application
        print("\nExiting application\n")
        sys.exit(0)

from lib import rabbitmq
import time
import threading
import grovepi
import serial

ser = serial.Serial('/dev/ttyACM0', 115200)  # arduino-sensors

rmq1 = rabbitmq.RabbitMQ()
rmq2 = rabbitmq.RabbitMQ()
rmq3 = rabbitmq.RabbitMQ()

light_port = 1
temp_port = 3
ultrasonic_port = 2

led_port = 6
door_relay_port = 5
door_relay_indicator = 4
ac_relay_port = 7
ac_relay_indicator = 8
grovepi.pinMode(led_port, "OUTPUT")
grovepi.pinMode(door_relay_port, "OUTPUT")
grovepi.pinMode(door_relay_indicator, "OUTPUT")
grovepi.pinMode(ac_relay_port, "OUTPUT")
grovepi.pinMode(ac_relay_indicator, "OUTPUT")

emergency_button_port = 14
emergency_buzzer_port = 16
grovepi.pinMode(emergency_button_port, "INPUT")
grovepi.pinMode(emergency_buzzer_port, "OUTPUT")
actuator_commands = {}


def read_ultrasonic_door():  # for person at door detection, handle via arduino-sensors
    while True:
        if ser.in_waiting > 0:
            personatdoor = str(ser.readline(), 'utf-8').strip()
            print("sent personatdoor: " + personatdoor)
            rmq3.send("sensors.personatdoor", personatdoor)


def emergency():
    grovepi.digitalWrite(door_relay_port, 1)  # open doors
    grovepi.digitalWrite(door_relay_indicator, 1)
    grovepi.digitalWrite(led_port, 0)  # turn on lights
    grovepi.digitalWrite(ac_relay_port, 0)  # turn off ac, as not to potentially take power away from alarm
    grovepi.digitalWrite(ac_relay_indicator, 0)
    grovepi.analogWrite(emergency_buzzer_port, 255)


def clients():
    while True:
        time.sleep(0.2)
        if 'sensors.mode' in actuator_commands and actuator_commands['sensors.mode'] == 'emergency':
            # check if emergency was set elsewhere (web interface)
            emergency()
            continue

        emergency_trigger = grovepi.analogRead(emergency_button_port)  # enable emergency (simulate smoke detector)
        if emergency_trigger > 50:
            rmq1.send("sensors.mode", "emergency")  # see emergency from web ui (only it can turn off emergency)
            emergency()
            continue

        grovepi.analogWrite(emergency_buzzer_port, 0)  # turn off buzzer if not emergency mode

        lightlevel = grovepi.analogRead(light_port)
        print("sent lightlevel: " + str(lightlevel))
        rmq1.send("sensors.lightlevel", str(lightlevel))

        [temp, hum] = grovepi.dht(temp_port, 0)
        print("sent temperature: " + str(temp))
        rmq1.send("sensors.temperature", str(temp))

        distance = grovepi.ultrasonicRead(ultrasonic_port)  # for presence in room
        print("sent ultrasonic: " + str(distance))
        rmq1.send("sensors.ultrasonic", str(distance))

        if 'actuators.ac' in actuator_commands:
            ac_cmd = int(actuator_commands['actuators.ac'])
            print("received ac: " + str(ac_cmd))
            grovepi.digitalWrite(ac_relay_port, ac_cmd)
            grovepi.digitalWrite(ac_relay_indicator, ac_cmd)
        if 'actuators.door' in actuator_commands:
            door_cmd = int(actuator_commands['actuators.door'])
            print("received door: " + str(door_cmd))
            grovepi.digitalWrite(door_relay_port, door_cmd)
            grovepi.digitalWrite(door_relay_indicator, door_cmd)
        if 'actuators.led' in actuator_commands:
            led_cmd = int(actuator_commands['actuators.led'])
            print("received led: " + str(led_cmd))
            grovepi.digitalWrite(led_port, led_cmd)


def callback(ch, method, properties, body):
    actuator_commands[method.routing_key] = str(body, 'utf-8')


def main():
    threading.Thread(target=read_ultrasonic_door).start()
    threading.Thread(target=clients).start()
    rmq2.receive(["actuators.*", "sensors.mode"], callback)


if __name__ == "__main__":
    main()

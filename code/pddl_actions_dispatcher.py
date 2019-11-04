from lib import rabbitmq


rmq = rabbitmq.RabbitMQ()


def turn_on_led():
    rmq.send("actuators.led", "1")


def turn_off_led():
    rmq.send("actuators.led", "0")


def open_door():
    rmq.send("actuators.door", "1")


def close_door():
    rmq.send("actuators.door", "0")


def turn_on_ac():
    rmq.send("actuators.ac", "1")


def turn_off_ac():
    rmq.send("actuators.ac", "0")


action_mapping = {
    'turn_on_led': turn_on_led,
    'turn_off_led': turn_off_led,
    'open_door': open_door,
    'close_door': close_door,
    'turn_on_ac': turn_on_ac,
    'turn_off_ac': turn_off_ac
}


def dispatch(actions):
    for action in actions:
        action_mapping[action]()

import time
import datetime
import threading
from lib import mongodb, rabbitmq
import pddl_planner
import pddl_actions_dispatcher
from lib.constants import day_mode, night_mode, open_hour, close_hour


mdb = mongodb.MongoDB()
rmq = rabbitmq.RabbitMQ()
pddl_planner = pddl_planner.PddlPlanner()
state = {
    'sensors.mode': 'clear',
    'sensors.lightlevel': '100',
    'sensors.personatdoor': '0',
    'sensors.temperature': '20',
    'sensors.ultrasonic': '40'
}


def callback(ch, method, properties, body):
    sensor_value = str(body, 'utf-8')
    state[method.routing_key] = sensor_value
    mdb.save(method.routing_key, sensor_value, datetime.datetime.now())


def decide_mode():
    user_override = state['sensors.mode']
    if user_override == day_mode():
        return day_mode()
    elif user_override == night_mode():
        return night_mode()
    else:
        current_hour = datetime.datetime.now().hour
        if open_hour() < current_hour < close_hour():
            return day_mode()
        else:
            return night_mode()


def execute_planner():
    while True:
        time.sleep(1)
        pddl_planner.mode = decide_mode()
        print("State: " + str(state))
        actions = pddl_planner.run_planner(state)
        pddl_actions_dispatcher.dispatch(actions)


def main():
    mdb.delete_all()
    threading.Thread(target=execute_planner).start()
    rmq.receive(["sensors.*"], callback)


if __name__ == "__main__":
    main()

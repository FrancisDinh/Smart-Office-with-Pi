import subprocess
from lib.constants import day_mode


def read_pddl_file(file_path):
    with open(file_path, 'r') as pddl_file:
        return pddl_file.read()


class PddlPlanner:
    def __init__(self, mode=day_mode()):
        self.mode = mode
        self.dm_day = read_pddl_file('pddl/dm_day.pddl')
        self.pb_day = read_pddl_file('pddl/pb_day.pddl')
        self.dm_night = read_pddl_file('pddl/dm_night.pddl')
        self.pb_night = read_pddl_file('pddl/pb_night.pddl')

    def generate_problem(self, init):
        with open('problem.pddl', 'w') as problem:
            if self.mode == day_mode():
                problem.write(self.pb_day.strip().replace('(:init)', init))
            else:
                problem.write(self.pb_night.strip().replace('(:init)', init))

    def generate_domain(self):
        with open('domain.pddl', 'w') as domain:
            if self.mode == day_mode():
                domain.write(self.dm_day.strip())
            else:
                domain.write(self.dm_night.strip())

    def get_planning_results(self, process_result):
        actions = []
        try:
            lines = str(process_result.stdout, 'utf-8').split('time spent:')[0].split('step')[1].strip().split('\n')
            for line in lines:
                actions.append(line.split(':')[1].strip().split(' ')[0].strip().lower())
            print("Plan: " + str(actions))
            return actions
        except Exception:
            print("Plan:")
            return []

    def convert_state_to_init(self, state):
        init = "(:init"
        if self.mode == day_mode():
            if int(state['sensors.lightlevel']) > 80:
                init += "(TOOBRIGHT light_intensity)"
            else:
                init += "(TOODARK light_intensity)"
            if int(state['sensors.personatdoor']) == 1:
                init += "(ISATDOOR person_atdoor)"
            else:
                init += "(NOTISATDOOR person_atdoor)"
            if float(state['sensors.temperature']) > 23.0:
                init += "(TOOHOT temperature)"
            else:
                init += "(TOOCOLD temperature)"
            if int(state['sensors.ultrasonic']) < 50:
                init += "(ISPRESENT presence)"
        else:
            init += "(TOOBRIGHT light_intensity)"
            init += "(TOOCOLD temperature)"
            if int(state['sensors.ultrasonic']) < 50:
                init += "(ISATDOOR person_atdoor)"
                init += "(ISPRESENT presence)"
            else:
                init += "(NOTISPRESENT presence)"
                init += "(NOTISATDOOR person_atdoor)"
        init += ")"   
        return init

    def run_planner(self, state):
        self.generate_problem(self.convert_state_to_init(state))
        self.generate_domain()
        process_result = subprocess.run(['./pddl/ff-v2.3/ff', '-o', 'domain.pddl', '-f', 'problem.pddl'], stdout=subprocess.PIPE)
        return self.get_planning_results(process_result)

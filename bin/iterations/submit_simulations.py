#!/usr/bin/env python3

import csv
import subprocess
import time
from pathlib import Path

def countdown_timer(t):
    """
    Countdown timer for submitting next simulation
    """
    while t:
        mins, secs = divmod(t, 60)
        hours, mins = divmod(mins, 60)
        days, hours = divmod(hours, 24)
        timer = 'Next submission in: {:02d}:{:02d}:{:02d}:{:02d}'.format(days, hours, mins, secs) 
        print(timer, end="\r") 
        time.sleep(1) 
        t -= 1

def parse_config_file(path):
    '''
    Parses config file for simulation parameters
    '''
    parameter_list = []
    simulation_number = 0

    with open(path) as f:
        queue = [{k: v for k, v in row.items()} for row in csv.DictReader(f, skipinitialspace=True)]
    
    for parent in queue:
        element = parent['z']
        isotope = parent['a']
        decay_mode = parent['decay_mode']
        gamma1 = parent['gamma1']
        gamma2 = parent['gamma2']
        radius = parent['radius']
        total_events = int(float(parent['total_events']))
        batch_events = int(float(parent['events_per_sim']))
        iterations = int(parent['iterations'])

        parameter_dict = {
            'simulation_number' : simulation_number, 
            'element' : str(element),
            'isotope' : str(isotope),
            'decay_mode' : str(decay_mode),
            'gamma1' : gamma1,
            'gamma2' : gamma2,
            'radius' : radius,
            'total_events' : total_events,
            'batch_events' : batch_events,
            'iterations' : iterations
        }
        parameter_list.append(parameter_dict)
        
        simulation_number += 1

    return parameter_list

def main():
    top_dir = Path.cwd()
    config_file = "simulation_parameters.cfg"
    hours_to_seconds = 3600
    wait_time_hrs = 5
    batch_limit = 2
    submit_sim = True

    simulation_queue = parse_config_file(config_file)

    total_submissions = len(simulation_queue)
    for simulation in simulation_queue:
        data_dir = Path(top_dir / f"inputs/user-data/z{simulation['element']}.a{simulation['isotope']}.e{simulation['gamma1']}_{simulation['gamma2']}")

        file_prep_command = f"./bin/write_input_files.py -z {simulation['element']} -a {simulation['isotope']} --decay-mode {simulation['decay_mode']} -g1 {simulation['gamma1']} -g2 {simulation['gamma2']} -r {simulation['radius']} --batch-events {simulation['batch_events']} --data-dir {data_dir}"

        simulation_iter = 0
        batch_counter = 0
        while simulation_iter < simulation['iterations']:
            run_command = f"./bin/simulation_workflow.py -z {simulation['element']} -a {simulation['isotope']} -g1 {simulation['gamma1']} -g2 {simulation['gamma2']} -e {simulation['total_events']} -b {simulation['batch_events']} --iteration {simulation_iter} --submit {submit_sim}"

            status_message = f"Submitting simulation for z:{simulation['element']} a:{simulation['isotope']} g1:{simulation['gamma1']} g2:{simulation['gamma2']}"
            # print(status_message)
            try:
                print(simulation_iter, batch_counter)
                subprocess.call(file_prep_command, shell=True)
                subprocess.call(run_command, shell=True)
                simulation_iter += 1
                batch_counter += 1 
                if total_submissions > 1 or batch_counter >= batch_limit:
                    total_submissions -= 1
                    batch_counter = 0
                    print()
                    print(f"Submitted iteration {simulation_iter} of {simulation['iterations']}")
                    countdown_timer(int(wait_time_hrs * hours_to_seconds))
                    print()
            except OSError as error:
                    print("Something went wrong!")
                    print(error)
                    quit()


if __name__ == "__main__":
    main()

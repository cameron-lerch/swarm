'''
This program was written for admitted students visiting weekend. The swarm displayes Yale's Y. 
IMPORTANT:
- Always set up the crazy flies in numerical order, left to right, spaced 40cm apart. 

Written by Cameron Lerch on 03.06.22 and last updated on 03.06.22
'''

import time

import cflib.crtp
from cflib.crazyflie.swarm import CachedCfFactory
from cflib.crazyflie.swarm import Swarm

# URIs for the swarm, change the last digit to match the crazyflies you are using.
URI0 = 'radio://0/80/2M/E7E7E7E7E8'
URI1 = 'radio://0/80/2M/E7E7E7E7E1'
URI2 = 'radio://0/80/2M/E7E7E7E7E9'
URI3 = 'radio://0/80/2M/E7E7E7E7E3'
URI4 = 'radio://0/80/2M/E7E7E7E7E4'
URI5 = 'radio://0/80/2M/E7E7E7E7E7'
URI6 = 'radio://0/80/2M/E7E7E7E7E6'

z0 = 0.2
z1 = 0.2
z2 = 0.4
z5 = 0.7
z3 = 1.0
z4 = 1.3

t1 = 3.0
t2 = 15.0
t3 = 3.0

#    x   y   z  time
sequence0 = [
    (0.00, 0.00, z0, t1),
    (-0.80, -1.50, z2, t2),
    (0.00, 0.00, z0, t3),
]
sequence1 = [
    (-0.07, -0.54, z0, t1),
    (1.18, -0.60, z4, t2),
    (-0.07, -0.54, z0, t3),
]

sequence2 = [
    (-0.14, -1.03, z0, t1),
    (0.50, -1.04, z3, t2),
    (-0.14, -1.03, z0, t3),
]

sequence3 = [
    (-0.25, -1.58, z0, t1),
    (-0.25, -1.58, z5, t2),
    (-0.25, -1.58, z0, t3),
]

sequence4 = [
    (-0.30, -2.11, z0, t1),
    (0.36, -2.16, z3, t2),
    (-0.30, -2.11, z0, t3),
]

sequence5 = [
    (-0.39, -2.65, z0, t1),
    (1.01, -2.79, z4, t2),
    (-0.39, -2.65, z0, t3),
]

sequence6 = [
    (-0.48, -3.16, z0, t1),
    (-1.30, -1.50, z1, t2),
    (-0.48, -3.16, z0, t3),
]

seq_args = {
    URI0: [sequence0],
    URI1: [sequence1],
    URI2: [sequence2],
    URI3: [sequence3],
    URI4: [sequence4],
    URI5: [sequence5],
    URI6: [sequence6],
}

# List of URIs, comment the one you do not want to fly
uris = {
    URI0,
    URI1,
    URI2,
    URI3,
    URI4,
    URI5,
    URI6
}


def wait_for_param_download(scf):
    while not scf.cf.param.is_updated:
        time.sleep(1.0)
    print('Parameters downloaded for', scf.cf.link_uri)


def take_off(cf, position):
    take_off_time = 1.0
    sleep_time = 0.1
    steps = int(take_off_time / sleep_time)
    vz = position[2] / take_off_time

    print(vz)

    for i in range(steps):
        cf.commander.send_velocity_world_setpoint(0, 0, vz, 0)
        time.sleep(sleep_time)


def land(cf, position):
    landing_time = 1.0
    sleep_time = 0.1
    steps = int(landing_time / sleep_time)
    vz = -position[2] / landing_time

    print(vz)

    for _ in range(steps):
        cf.commander.send_velocity_world_setpoint(0, 0, vz, 0)
        time.sleep(sleep_time)

    cf.commander.send_stop_setpoint()
    # Make sure that the last packet leaves before the link is closed
    # since the message queue is not flushed before closing
    time.sleep(0.1)


def run_sequence(scf, sequence):
    try:
        cf = scf.cf

        take_off(cf, sequence[0])
        for position in sequence:
            print('Setting position {}'.format(position))
            end_time = time.time() + position[3]
            while time.time() < end_time:
                cf.commander.send_position_setpoint(position[0],
                                                    position[1],
                                                    position[2], 0)
                time.sleep(0.1)
        land(cf, sequence[-1])
    except Exception as e:
        print(e)


if __name__ == '__main__':
    # logging.basicConfig(level=logging.DEBUG)
    cflib.crtp.init_drivers()

    factory = CachedCfFactory(rw_cache='./cache')
    with Swarm(uris, factory=factory) as swarm:
        # If the copters are started in their correct positions this is
        # probably not needed. The Kalman filter will have time to converge
        # any way since it takes a while to start them all up and connect. We
        # keep the code here to illustrate how to do it.
        # swarm.reset_estimators()

        # The current values of all parameters are downloaded as a part of the
        # connections sequence. Since we have 10 copters this is clogging up
        # communication and we have to wait for it to finish before we start
        # flying.
        print('Waiting for parameters to be downloaded...')
        swarm.parallel(wait_for_param_download)

        swarm.parallel(run_sequence, args_dict=seq_args)
import time

import cflib.crtp
from cflib.crazyflie.swarm import CachedCfFactory
from cflib.crazyflie.swarm import Swarm
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie


def activate_led_bit_mask(scf: SyncCrazyflie):
    scf.cf.param.set_value('led.bitmask', 255)


def deactivate_led_bit_mask(scf: SyncCrazyflie):
    scf.cf.param.set_value('led.bitmask', 0)


def light_check(scf: SyncCrazyflie):
    activate_led_bit_mask(scf)
    time.sleep(2)
    deactivate_led_bit_mask(scf)
    time.sleep(2)


def arm(scf: SyncCrazyflie):
    scf.cf.platform.send_arming_request(True)
    time.sleep(1.0)


def take_off(scf: SyncCrazyflie):
    commander = scf.cf.high_level_commander

    commander.takeoff(1.0, 2.0)
    time.sleep(3)


def land(scf: SyncCrazyflie):
    commander = scf.cf.high_level_commander

    commander.land(0.0, 2.0)
    time.sleep(2)

    commander.stop()

uris = [
    'radio://0/80/2M/E7E7E7E7E7',
    'radio://0/20/2M/E7E7E7E702',
    'radio://0/20/2M/E7E7E7E703',
    'radio://0/20/2M/E7E7E7E704',
    'radio://0/20/2M/E7E7E7E704'
]

h = 0.0
x0, y0 = +0.5, +0.5
x1, y1 = -0.5, -0.5

pos_args = {
    uris[0]: (x0, y0, h),
    uris[1]: (x1, y0, h),
    uris[2]: (x1, y1, h),
    uris[3]: (x0, y1, h),
    uris[4]: (0, 0, h),
}

yaw = 0.15

def poshold(scf: SyncCrazyflie, sequence, t, h):
    cf = scf.cf
    steps = t * 10

    for uri, arguments in sequence.items():
        x, y, z = arguments
        print('Setting position {} to cf {}'.format((x, y, z), cf.link_uri))

        for r in range(steps):
            cf.commander.send_hover_setpoint(x, y, z, yaw)
            time.sleep(0.1)


if __name__ == '__main__':
    cflib.crtp.init_drivers()
    factory = CachedCfFactory(rw_cache='./cache')
    with Swarm(uris, factory=factory) as swarm:
        print('Connected to  Crazyflies')
        swarm.parallel_safe(light_check)
        print('Light check done')

        swarm.reset_estimators()
        print('Estimators have been reset')

        swarm.parallel_safe(arm)
        swarm.parallel_safe(take_off)
        # swarm.parallel_safe(run_square_sequence)
        swarm.parallel_safe(poshold, args=(pos_args, 300, h))
        swarm.parallel_safe(land)
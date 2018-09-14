# -*- coding: utf-8 -*-
'''
The truckstop engine. This engine runs a loop that updates a variety of values
this truck.
'''

# Import python libs
import logging
import os
from truck import Truck

log = logging.getLogger(__name__)


if __name__ == '__main__':
    truck_id = os.getenv('TRUCK_ID')
    if truck_id:
        truck = Truck(truck_id=truck_id)
        truck.turn_on()
        if truck.run_diagnostics()[0]:
            truck.start_engine()
            truck.run(frequency=2)
    else:
        raise Exception('Truck ID [{}] invalid'.format(truck_id))

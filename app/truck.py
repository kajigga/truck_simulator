import os
import json
import glob
import time
import logging
import requests
from communications import send_message
from random import choice, randint

log = logging.getLogger(__name__)

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
routes_path = os.path.join(PROJECT_ROOT, 'routes', 'route-*.json')


# TODO possible routes should not be hard-coded into the truck. They should be
# downloaded from the TruckStop command center
possible_routes = glob.glob(routes_path)


class Truck(object):
    def __init__(self, truck_id):
        self.id = truck_id
        self.distance_travelled = 0
        self.diagnostics_check = (None, [])
        self.destination = ''
        self.location = {}  # TODO Set this to the home office
        self.route = {}
        self.route_done = False
        self.at_beginning = False
        self.current_step = 0  # Step is used when following a route
        self.cargo = {'used': 0, 'capacity': 50}
        self.status = 'active'
        self.stay_days = 0
        self.turn_choices = (
            ['advance_route'] * 94 +
            ['stay_at_location'] * 5 +
            ['break_down'])

        # There won't be a problem unless the truck breaks down
        self.problem = {}
        self.message_queue = []
        self.MAX_MESSAGE_ATTEMPTS = 10
        self.cycles = 0
        self.engine_running = False

    @property
    def dict_keys(self):
        return [
            'id',
            'distance_travelled',
            'destination',
            'location',
            'route',
            'route_done',
            'at_beginning',
            'current_step',
            'cargo',
            'status',
            'stay_days',
            'problem',
            'cycles',
            'engine_running']

    def turn_on(self):
        """The Truck is turned_on (key turned).

        """
        if self.run_diagnostics():
            self.status = 'turned_on'
        else:
            self.status = 'failed_diagnostics'

    def run_diagnostics(self):
        """Running diagnostics should check the following:
        -

        and return a tuple representing whether all checks passed and any
        messages returned
        """
        checks_passed = True
        messages = []

        self.diagnostics_check = (checks_passed, messages)
        return self.diagnostics_check

    def start_engine(self):
        """Starting the engine does what?:
        -
        -

        the started engine return Boolean when engine is running
        """

        if self.run_diagnostics()[0]:
            self.engine_running = True
            log.debug('truckstop engine started')
            self.send_message('engine/start/successfull')
        else:
            self.engine_running = False
            log.debug('truckstop engine failed to start')
            self.send_message('engine/start/failure')
        return self.engine_running

    def stop_engine(self):
        """Starting the engine does what?:

        the started engine return Boolean when engine is running
        """

        self.engine_running = False

        return self.engine_running

    def run(self, frequency=60):
        """
        On every turn, one of the following may happen:
            - truck is seen for the first time
            - if the truck is at the beginning of a route:
                - load cargo
            - advance on route
            - stay at current location
            - truck breaks down
            - truck is attacked by marauding bandits ;)
            - truck completes a route
                - cargo is unloaded

        The following happens when a truck is seen for the first time or when a
        truck completes a route:
            - a new route is selected
        """
        # Notify the Truck Edge Server this Truck is online
        self.run_diagnostics()

        while self.diagnostics_check[0] and True:
            # self.send_message('truckstop/'+truck_id+'/turn', {})
            # __salt__['truckstop.run_cycle'](truck_id)
            self.cycles += 1

            if not self.route:
                # This is the first time or there is just no route assigned
                # self.send_message('truckstop/{}/no_truck'.format(truck_id),
                # truck)
                self.send_message('no_route')
                self.choose_route()
            elif self.route_done:
                # Route is done, choose a new one
                self.choose_route()
            elif self.at_beginning:
                # At beginning of route
                self.load_cargo()
            elif self.status == 'broken_down':
                # The truck is broken down
                # check if the repairs are donw
                self.check_repairs()
            elif self.status == 'stationary':
                # Chech stationary time
                self.check_stationary_time()
            else:
                '''do one of following
                    - advance on route
                    - stay at location
                    - break down
                '''
                getattr(self, choice(self.turn_choices))()

            if self.cycles % frequency == 0:
                self.attempt_to_send_messages()
            time.sleep(1)
        log.debug('diagnostics: %s', '\n'.join(self.diagnostics_check[1]))

    def attempt_to_send_messages(self):
        # Attempt to send all queued messages
        while self.message_queue:
            tag, attempts, data = self.message_queue.pop(0)
            log.debug('%s %s %s', tag, attempts, data)
            if not send_message(tag, data):
                # message could not be sent
                # decrement the number of attempts to make
                attempts -= 1
                # requeue the message if attempts is greater than 0
                if attempts > 0:
                    self.message_queue.append((tag, attempts, data))

    def choose_route(self):
        """Take a truck_id and have a route assigned to the truck"""

        # empty cargo, setting used to 0
        self.cargo['used'] = 0

        # TODO Have the truck poll the SaltStack api to check for assigned
        # routes
        self.route = choice(possible_routes)
        self.destination = load_route(self.route)['end_address']
        self.at_beginning = True
        self.current_step = 0

        self.send_message('route_assigned')

    def load_cargo(self):
        """Load cargo into the truck."""
        self.cargo['used'] = randint(1, self.cargo['capacity'] + 1)
        self.at_beginning = False  # The truck is ready to go.
        self.send_message('cargo_loaded')

    def arrive_at_destination(self):
        """Mark the truck as arrived at the destination"""
        steps = load_route(self.route)['steps']
        self.location = steps[-1]['end_location']
        self.cargo['used'] = 0
        self.route = None

        self.send_message('arrive_at_destination')

    def advance_route(self):
        """Move the truck along on it's route. This normally happens automatically
        when the truckstop engine is running."""
        self.current_step += 1
        self.at_beginning = False

        steps = load_route(self.route)['steps']
        if self.current_step < len(steps):
            self.location = steps[self.current_step]['end_location']
            meters = steps[self.current_step]['distance']['value']
            self.distance_travelled += meters_to_miles(meters)
            self.send_message('location')
        else:
            # Truck is at destination
            # empty cargo
            self.arrive_at_destination()

    def stay_at_location(self):
        """Make the truck stay where it's at for a time"""
        # How long should the truck stay
        self.stay_days = randint(1, 5)
        self.status = 'stationary'
        self.stop_engine()
        self.send_message('stopped')

    def break_down(self):
        self.problem = {'days_to_fix': randint(1, 10), 'diagnosis': ''}

        self.status = 'broken_down'

        self.send_message('broken_down')

    def check_repairs(self):
        if self.problem.get('days_to_fix') == 0:
            # Truck is ready to go, set status to 'active'
            self.status = 'active'
            self.problem = {}
        else:
            self.problem['days_to_fix'] -= 1
        self.send_message('repairs_check')

    def check_stationary_time(self):
        if self.stay_days == 0:
            # Truck is ready to go, set status to 'active'
            self.status = 'active'
            self.start_engine()
        else:
            self.stay_days -= 1
        self.send_message('stay_check')

    def send_message(self, tag):
        tag = '{}/{}'.format(self.id, tag)
        # v1 - add messages to a queue
        # a message is two parts, the tag and the max attempts
        log.debug('tag: %s', tag)
        msg = (tag,
               self.MAX_MESSAGE_ATTEMPTS,
               self.to_dict())
        self.message_queue.append(msg)

    def to_dict(self):
        """This method generates a nice dictionary of the truck for
        transmitting via message system"""
        return_dict = {}
        for k in self.dict_keys:
            return_dict[k] = getattr(self, k)
        return return_dict

    def poll_truckstop(self):
        """
        Poll for commands.
        """
        cmd = [{
            'client': 'local',
            'tgt': 'truckstop-master',
            'fun': 'truckstop.get_commands',
            'username': 'saltdev',
            'password': 'saltdev',
            'eauth': 'pam',
            'kwarg': {
                'truck_id': self.id
            }
            }]

        cmds = requests.post(
                '{}/{}'.format(os.getenv('TRUCKSTOP_URL')),
                json=cmd)
        # TODO cmds should be a list of things to do
        return cmds


def load_route(route_path):
    with open(route_path) as _f:
        route = json.load(_f)
    return route


def meters_to_miles(meters):
    # conversion factor
    conv = 0.621371

    # calculate miles
    return meters / 1000 * conv

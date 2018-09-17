# -*- coding: utf-8 -*-
"""
Support for running the truckstop system.

:depends: none

"""
from __future__ import absolute_import, print_function, unicode_literals
import sys
import copy
import glob
import logging
import salt.utils
from random import choice

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
log = logging.getLogger(__name__)


__virtualname__ = 'truckstop'


def __virtual__():
    problems = []
    if not _route_path():
        problems.append('truckstop.route_path not found. must '
                        'be configured in config or pillar')
    if not _truckstop_url():
        problems.append('truckstop.truckstop_url not found. must '
                        'be configured in config or pillar')
    if problems:
        return False, problems
    return __virtualname__


def _route_path():
    return __salt__['config.get']('truckstop:route_path')


def _truckstop_url():
    return __salt__['config.get']('truckstop:truckstop_url')


def possible_routes():
    # return glob.glob('/trucking_routes/route-*.json')
    return glob.glob('{}/route-*.json'.format(_route_path()))


TRUCK_TEMPLATE = {
    'distance_travelled': 0,
    'location': '',
    'truck_id': None,
    'route': {},
    'current_step': 0,
    'cargo': {'used': 50, 'capacity': 50}
}


def __sdb_lookup(key, default=None):
    value = __salt__['sdb.get']('sdb://truck_db/{}'.format(key))
    if not value:
        value = default
    return value


def save_truck(truck):
    trucks = get_active_trucks()
    truck_id = truck.get('truck_id', truck.get('id'))
    if truck_id in trucks:
        _key = 'sdb://truck_db/trucks/{}'.format(truck_id)
        __salt__['sdb.set'](_key, truck)
    return truck


def get_active_trucks(include_data=False):
    """
    Get a list of active trucks.

    CLI Examples:
    .. code-block:: bash
        salt myminion truckstop.get_active_trucks

    """
    trucks = __sdb_lookup('trucks/active', [])
    if not include_data:
        return trucks
    return [lookup_truck(truck_id) for truck_id in trucks]


def set_active_trucks(truck_list):
    return __salt__['sdb.set']('sdb://truck_db/trucks/active', truck_list)


def get_inactive_trucks(include_data=False):
    """
    Get a list of inactive trucks.

    CLI Examples:
    .. code-block:: bash
        salt myminion truckstop.get_inactive_trucks

    """
    trucks = __sdb_lookup('trucks/inactive', [])
    if not include_data:
        return trucks
    return [lookup_truck(truck_id) for truck_id in trucks]


def set_inactive_trucks(truck_list):
    return __salt__['sdb.set']('sdb://truck_db/trucks/inactive', truck_list)


def __load_route(route_path):
    return salt.utils.json.load(open(route_path))


def stop_all_trucks():
    msg = []
    trucks = get_active_trucks()
    for truck_id in trucks:
        stop_truck(truck_id)
        msg.append('{} stopped'.format(truck_id))
    set_inactive_trucks(trucks)
    set_active_trucks([])

    return msg


def stop_truck(truck_id):
    """Stop a truck given the ID """
    msg = ""
    try:
        msg = __salt__['dockerng.stop'](truck_id)
    except:
        msg = "Docker container {} must have been removed already".format(truck_id)
    return msg


def start_all_trucks():
    msg = []
    trucks = get_inactive_trucks()
    for truck_id in trucks:
        start_new_truck(truck_id)
        msg.append('{} started'.format(truck_id))
    set_inactive_trucks([])
    set_active_trucks(trucks)

    return msg


def start_new_truck(truck_id):
    """
    Add a new truck to the system. This means starting a new docker container
    with the truck_id
    """

    add_truck(truck_id)

    # Create a container
    environment = {
      'TRUCK_ID': truck_id,
      'TRUCKSTOP_URL': __salt__['pillar.get']('truckstop:truckstop_url')
    }

    log.debug(environment)

    try:
        __salt__['dockerng.inspect'](truck_id)  # ['truckstop-master']
        msg = '{} already existed'.format(truck_id)
    except:
        __salt__['dockerng.create'](name=truck_id,
                                    image='truck:latest',
                                    environment=environment)
        msg = '{} was created'.format(truck_id)

    __salt__['dockerng.start'](name=truck_id)

    return msg


def restart_truck(truck_id):

    __salt__['dockerng.rm'](name=truck_id, force=True)
    start_new_truck(truck_id)


def add_truck(truck_id, truck_info={}):
    """
    Check to see if the truck is already in the db. Add it if it is not
    found. Return the found information if it is.
    Add the truck to the trucking db
    """
    truck = lookup_truck(truck_id)
    if not truck:
        truck = copy.copy(TRUCK_TEMPLATE)
        truck['truck_id'] = truck_id
        truck.update(truck_info)

    truck = save_truck(truck)

    truck_list = set(get_active_trucks())
    log.debug('adding %s to central', truck_id)
    truck_list.add(truck_id)
    set_active_trucks(list(truck_list))

    truck_list = set(get_active_trucks())

    __salt__['event.send']('truckstop/{}/added'.format(truck_id), truck)
    return (truck_id in truck_list, truck)


# TODO
def remove_truck(truck_id):
    truck_list = set(get_active_trucks())
    if truck_id not in truck_list:
        msg = '{} was not in the list'.format(truck_id)
    else:
        truck_list.remove(truck_id)
        stop_truck(truck_id)
        set_active_trucks(list(truck_list))
        msg = '{} was removed'.format(truck_id)
    return msg


def reset_all_trucks():
    truck_list = set(get_active_trucks())
    for truck_id in truck_list:
        reset_truck(truck_id)


def reset_truck(truck_id):
    """
    Reset the record for this truck in the db

    CLI Examples:
    .. code-block:: bash
        salt myminion truckstop.reset_truck test_truck

    """
    truck = copy.copy(TRUCK_TEMPLATE)
    truck['truck_id'] = truck_id
    restart_truck(truck_id)
    save_truck(truck)
    return True


def choose_route(truck_id):
    '''Take a truck_id and have a route assigned to the truck. Only assign a
    route if one is not already assigned.'''
    truck = lookup_truck(truck_id)

    if not truck:
        # This truck is not registered
        return None

    if not truck['route']:
        # empty cargo, setting used to 0

        if truck:
            truck['route'] = choice(possible_routes())

        save_truck(truck)
        __salt__['event.send']('truckstop/{}/route_assigned'.format(truck_id),
                               truck)
    return truck['route']


def lookup_truck(truck_id, key=None):
    """
    Lookup a truck in the DB given a `truck_id`. An optional key parameter is
    also accepted to return just that key from the truck

    CLI Examples:
    .. code-block:: bash
        salt myminion truckstop.lookup_truck test_truck
        salt myminion truckstop.lookup_truck test_truck destination
    """
    # return __salt__['sdb.get']('sdb://truck_db/trucks/{}'.format(truck_id))
    truck = __sdb_lookup('trucks/{}'.format(truck_id), {})
    if key:
        return truck.get(key)
    return truck


def empty_queue():
    """
    Empty the command queue
    """
    _key = 'sdb://truck_db/commands'
    __salt__['sdb.set'](_key, [])


def enqueue_command(cmd):
    """
    Queue a command to the whole fleet of trucks.
    """
    commands = __sdb_lookup('commands', [])
    commands.append(cmd)
    _key = 'sdb://truck_db/commands'
    __salt__['sdb.set'](_key, commands)
    log.debug('commands %s', commands)
    # TODO Should probably figure out if there was a problem queuing commands
    return True


def get_commands(last_poll_page=0):
    """
    Fetch commands.
    It should be seen as a queue that is emptied upon retrieval. If
    last_poll_page is not set, all commands will be returned. Passing
    the last_poll_page will return all commands sent after that page.

    CLI Examples:
    .. code-block:: bash
        salt myminion truckstop.get_commands test_truck
        salt myminion truckstop.get_commands test_truck 25
    """

    cmds = __sdb_lookup('commands', [])
    page = len(cmds)
    log.debug('cmds %s', cmds)
    if last_poll_page > 0:
        cmds = map(lambda y: y[1], filter(
                lambda x: x[0] >= last_poll_page,
                enumerate(cmds)))
    return {'commands': cmds, 'page': page}


def update_data_file():
    """Update the truckstop data file for the map"""
    salt.utils.json.dump(
            get_active_trucks(include_data=True),
            open('/etc/salt/app/static/data.js', 'w+'))

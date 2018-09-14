# -*- coding: utf-8 -*-


def beacon(config):
    """Iterate through the list of active trucks, returning the full current
    telemetry on each one"""

    active_trucks = __salt__['truckstop.get_active_trucks']()
    truck_report = []
    for truck_id in active_trucks:
        truck = __salt__['truckstop.lookup_truck'](truck_id)

        # TODO Should I make the changes to the trucks here directly? It would improve the
        # race-condition and reporting up to the master
        truck_report.append({
            'tag': 'truck/{}'.format(truck_id),
            'telemetry': truck
            })
    return truck_report

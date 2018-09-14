import os
import sys
import logging
import requests
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
HOOK_PATH = 'hook'

log = logging.getLogger(__name__)
# log.setLevel(logging.DEBUG)


def send_message(tag, data):  # Try to send this message 10 times
    tag_mod = '{}/truckstop/{}'.format(HOOK_PATH, tag)
    log.debug('tag: %s data:%s', tag_mod, data)
    # Send data to the edge server using the salt-api or, if configured, the
    # salt-enterprise API
    # Execution of the truck should not fail if the connection fails
    try:
        requests.post('{}/{}'.format(os.getenv('TRUCKSTOP_URL'), tag_mod),
                      json=data)
        return True
    except requests.exceptions.ConnectionError:
        return False

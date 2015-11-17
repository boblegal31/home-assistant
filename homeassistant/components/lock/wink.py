"""
homeassistant.components.lock.wink
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Support for Wink locks.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/lock.wink/
"""
import logging

from homeassistant.helpers.entity import Entity
from homeassistant.const import CONF_ACCESS_TOKEN, STATE_LOCKED, STATE_UNLOCKED

REQUIREMENTS = ['https://github.com/balloob/python-wink/archive/'
                '9eb39eaba0717922815e673ad1114c685839d890.zip'
                '#python-wink==0.1.1']


def setup_platform(hass, config, add_devices, discovery_info=None):
    """ Sets up the Wink platform. """
    import pywink

    if discovery_info is None:
        token = config.get(CONF_ACCESS_TOKEN)

        if token is None:
            logging.getLogger(__name__).error(
                "Missing wink access_token. "
                "Get one at https://winkbearertoken.appspot.com/")
            return

        pywink.set_bearer_token(token)

    add_devices(WinkLockDevice(lock) for lock in pywink.get_locks())


class WinkLockDevice(Entity):
    """ Represents a Wink lock. """

    def __init__(self, wink):
        self.wink = wink

    @property
    def state(self):
        """ Returns the state. """
        return STATE_LOCKED if self.is_locked else STATE_UNLOCKED

    @property
    def unique_id(self):
        """ Returns the id of this wink lock """
        return "{}.{}".format(self.__class__, self.wink.deviceId())

    @property
    def name(self):
        """ Returns the name of the lock if any. """
        return self.wink.name()

    def update(self):
        """ Update the state of the lock. """
        self.wink.updateState()

    @property
    def is_locked(self):
        """ True if device is locked. """
        return self.wink.state()

    def do_lock(self):
        """ Lock the device. """
        self.wink.setState(True)

    def do_unlock(self):
        """ Unlock the device. """
        self.wink.setState(False)

"""
custom_components.example
~~~~~~~~~~~~~~~~~~~~~~~~~

Example component to target an entity_id to:
 - turn it on at 7AM in the morning
 - turn it on if anyone comes home and it is off
 - turn it off if all lights are turned off
 - turn it off if all people leave the house
 - offer a service to turn it on for 10 seconds

Configuration:

To use the Example custom component you will need to add the following to
your configuration.yaml file.

example:
  target: TARGET_ENTITY

Variable:

target
*Required
TARGET_ENTITY should be one of your devices that can be turned on and off,
ie a light or a switch. Example value could be light.Ceiling or switch.AC
(if you have these devices with those names).
"""
import time
import logging

from homeassistant.const import STATE_HOME, STATE_NOT_HOME, STATE_ON, STATE_OFF
from homeassistant.helpers import validate_config
from homeassistant.helpers.event_decorators import \
    track_state_change, track_time_change, service
import homeassistant.components as core
from homeassistant.components import device_tracker
from homeassistant.components import light

# The domain of your component. Should be equal to the name of your component
DOMAIN = "example"

# List of component names (string) your component depends upon
# We depend on group because group will be loaded after all the components that
# initialize devices have been setup.
DEPENDENCIES = ['group', 'device_tracker', 'light']

# Configuration key for the entity id we are targetting
CONF_TARGET = 'target'

# Variable for storing configuration parameters
CONFIG = {}

# Name of the service that we expose
SERVICE_FLASH = 'flash'

# Shortcut for the logger
_LOGGER = logging.getLogger(__name__)


def setup(hass, config):
    """ Setup example component. """

    # Validate that all required config options are given
    if not validate_config(config, {DOMAIN: [CONF_TARGET]}, _LOGGER):
        return False

    CONFIG['target_id'] = config[DOMAIN][CONF_TARGET]

    # Validate that the target entity id exists
    if hass.states.get(config['target_id']) is None:
        _LOGGER.error("Target entity id %s does not exist",
                      CONFIG['target_id'])

        # Tell the bootstrapper that we failed to initialize
        return False

    # Tell the bootstrapper that we initialized successfully
    return True


@track_state_change(device_tracker.ENTITY_ID_ALL_DEVICES)
def track_devices(hass, entity_id, old_state, new_state):
    """ Called when the group.all devices change state. """
    target_id = CONFIG['target_id']

    # If anyone comes home and the entity is not on, turn it on.
    if new_state.state == STATE_HOME and not core.is_on(hass, target_id):

        core.turn_on(hass, target_id)

    # If all people leave the house and the entity is on, turn it off
    elif new_state.state == STATE_NOT_HOME and core.is_on(hass, target_id):

        core.turn_off(hass, target_id)


@track_time_change(hour=7, minute=0, second=0)
def wake_up(hass, now):
    """
    Turn it on in the morning (7 AM) if there are people home and
    it is not already on.
    """
    target_id = CONFIG['target_id']

    if device_tracker.is_on(hass) and not core.is_on(hass, target_id):
        _LOGGER.info('People home at 7AM, turning it on')
        core.turn_on(hass, target_id)


@track_state_change(light.ENTITY_ID_ALL_LIGHTS, STATE_ON, STATE_OFF)
def all_lights_off(hass, entity_id, old_state, new_state):
    """ If all lights turn off, turn off. """
    target_id = CONFIG['target_id']

    if core.is_on(hass, target_id):
        _LOGGER.info('All lights have been turned off, turning it off')
        core.turn_off(hass, target_id)


@service(DOMAIN, SERVICE_FLASH)
def flash_service(hass, call):
    """
    Service that will turn the target off for 10 seconds if on and vice versa.
    """
    target_id = CONFIG['target_id']

    if core.is_on(hass, target_id):
        core.turn_off(hass, target_id)

        time.sleep(10)

        core.turn_on(hass, target_id)

    else:
        core.turn_on(hass, target_id)

        time.sleep(10)

        core.turn_off(hass, target_id)

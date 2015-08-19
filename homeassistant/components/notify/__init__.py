"""
homeassistant.components.notify
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provides functionality to notify people.
"""
from functools import partial
import logging

from homeassistant.loader import get_component
from homeassistant.helpers import config_per_platform

from homeassistant.const import CONF_PLATFORM, CONF_NAME

DOMAIN = "notify"
DEPENDENCIES = []

# Title of notification
ATTR_TITLE = "title"
ATTR_TITLE_DEFAULT = "Home Assistant"

# Text to notify user of
ATTR_MESSAGE = "message"

SERVICE_NOTIFY = "notify"

_LOGGER = logging.getLogger(__name__)


def send_message(hass, message):
    """ Send a notification message. """
    hass.services.call(DOMAIN, SERVICE_NOTIFY, {ATTR_MESSAGE: message})


def setup(hass, config):
    """ Sets up notify services. """
    success = False

    for platform, p_config in config_per_platform(config, DOMAIN, _LOGGER):
        # get platform
        notify_implementation = get_component(
            'notify.{}'.format(platform))

        if notify_implementation is None:
            _LOGGER.error("Unknown notification service specified.")
            continue

        # create platform service
        notify_service = notify_implementation.get_service(
            hass, {DOMAIN: p_config})

        if notify_service is None:
            _LOGGER.error("Failed to initialize notification service %s",
                          platform)
            continue

        # create service handler
        def notify_message(notify_service, call):
            """ Handle sending notification message service calls. """
            message = call.data.get(ATTR_MESSAGE)

            if message is None:
                return

            title = call.data.get(ATTR_TITLE, ATTR_TITLE_DEFAULT)

            notify_service.send_message(message, title=title)

        # register service
        service_call_handler = partial(notify_message, notify_service)
        service_notify = p_config.get(CONF_NAME, SERVICE_NOTIFY)
        hass.services.register(DOMAIN, service_notify, service_call_handler)
        success = True

    return success


# pylint: disable=too-few-public-methods
class BaseNotificationService(object):
    """ Provides an ABC for notification services. """

    def send_message(self, message, **kwargs):
        """
        Send a message.
        kwargs can contain ATTR_TITLE to specify a title.
        """
        raise NotImplementedError

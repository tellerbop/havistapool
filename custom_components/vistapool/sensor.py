"""Support for Vista Pool sensors."""
import logging

from homeassistant.const import CONF_USERNAME

from .vistapool_entity import VistaPoolEntity
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Old way."""


async def async_setup_entry(hass, config_entry, async_add_entities):
    sensors = []

    account = config_entry.data.get(CONF_USERNAME)
    poolData = hass.data[DOMAIN][account]

    for config_pool in poolData.config_pools:
        for sensor in config_pool.sensors:
            sensors.append(VistaPoolSensor(config_pool, sensor))

    async_add_entities(sensors, True)


class VistaPoolSensor(VistaPoolEntity):
    """Representation of a Vista Pool sensor."""

    @property
    def state(self):
        """Return the state."""
        return self._instrument.state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._instrument.unit
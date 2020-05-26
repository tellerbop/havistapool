from homeassistant.helpers.entity import Entity
from homeassistant.helpers.dispatcher import (
    async_dispatcher_connect,
    async_dispatcher_send,
)

from .const import DOMAIN, SIGNAL_STATE_UPDATED


class VistaPoolEntity(Entity):
    """Base class for all entities."""

    def __init__(self, data, instrument):
        """Initialize the entity."""
        self._data = data
        self._instrument = instrument
        self._pid = self._instrument.pid
        self._component = self._instrument.component
        self._attribute = self._instrument.attr

    async def async_added_to_hass(self):
        """Register update dispatcher."""
        async_dispatcher_connect(
            self.hass, SIGNAL_STATE_UPDATED, self.async_schedule_update_ha_state
        )

    @property
    def icon(self):
        """Return the icon."""
        return self._instrument.icon

    @property
    def _entity_name(self):
        return self._instrument.name

    @property
    def _pool_name(self):
        return self._instrument.pool_name

    @property
    def name(self):
        """Return full name of the entity."""
        return "{} {}".format(self._pool_name, self._entity_name)

    @property
    def should_poll(self):
        """Return the polling state."""
        return False

    @property
    def assumed_state(self):
        """Return true if unable to access real state of entity."""
        return True

    @property
    def device_state_attributes(self):
        """Return device specific state attributes."""
        return dict(
            self._instrument.attributes,            
            name=self._instrument.name,
            pid=self._instrument.pid,
            
        )

    @property
    def unique_id(self):
        return self._instrument.full_name

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._instrument.pool_name)},            
            "manufacturer": "VistaPool",
            "name": self._pool_name,
            "device_type": self._component,
        }
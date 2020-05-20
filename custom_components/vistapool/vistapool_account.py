import logging
from datetime import timedelta
import threading
import asyncio
import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.dispatcher import (
    async_dispatcher_connect,
    async_dispatcher_send,
)
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.event import async_track_point_in_utc_time
from homeassistant.util.dt import utcnow
from homeassistant.const import (
    CONF_NAME,
    CONF_PASSWORD,
    CONF_RESOURCES,
    CONF_SCAN_INTERVAL,
    CONF_USERNAME,
)

from .dashboard import Dashboard
from .vistapool_connect_account import VistaPoolConnectAccount
from .pool import PoolData

from .const import (
    DOMAIN,
    CONF_PID,
    CONF_ACTION,        
    DEFAULT_UPDATE_INTERVAL,
    MIN_UPDATE_INTERVAL,
    SIGNAL_STATE_UPDATED,
    TRACKER_UPDATE,
    COMPONENTS,
)

SERVICE_EXECUTE_POOL_ACTION = "execute_pool_action"
SERVICE_EXECUTE_POOL_ACTION_SCHEMA = vol.Schema(
    {vol.Required(CONF_PID): cv.string, vol.Required(CONF_ACTION): cv.string}
)

_LOGGER = logging.getLogger(__name__)


class VistaPoolAccount():
    def __init__(self, hass, config_entry, unit_system: str):
        """Initialize the component state."""
        self.hass = hass
        self.config_entry = config_entry
        self.config_pools = set()
        self.pools = set()
        self.interval = config_entry.data.get(CONF_SCAN_INTERVAL)
        self.unit_system = unit_system

    def init_connection(self):
        session = async_get_clientsession(self.hass)
        self.connection = VistaPoolConnectAccount(
            session=session,
            username=self.config_entry.data.get(CONF_USERNAME),
            password=self.config_entry.data.get(CONF_PASSWORD),
        )

        self.hass.services.async_register(
            DOMAIN,
            SERVICE_EXECUTE_POOL_ACTION,
            self.execute_pool_action,
            schema=SERVICE_EXECUTE_POOL_ACTION_SCHEMA,
        )

    def is_enabled(self, attr):
        return True
        # """Return true if the user has enabled the resource."""
        # return attr in config[DOMAIN].get(CONF_RESOURCES, [attr])

    def discover_pools(self, pools):

        if len(pools) > 0:
            for pool in pools:
                pid = pool.pid

                self.pools.add(pid)

                dashboard = Dashboard(
                    self.connection, pool, unit_system=self.unit_system
                )
                
                cfg_pool = PoolData(self.config_entry)
                cfg_pool.pool = pool
                self.config_pools.add(cfg_pool)
                

                for instrument in (
                    instrument                   
                    for instrument in dashboard.instruments
                    if instrument._component in COMPONENTS
                    and self.is_enabled(instrument.slug_attr)
                ):

                    if instrument._component == "sensor":
                        cfg_pool.sensors.add(instrument)
                    if instrument._component == "binary_sensor":
                        cfg_pool.binary_sensors.add(instrument)
                    if instrument._component == "switch":
                        cfg_pool.switches.add(instrument)

            self.hass.async_add_job(
                self.hass.config_entries.async_forward_entry_setup(
                    self.config_entry, "sensor"
                )
            )
            self.hass.async_add_job(
                self.hass.config_entries.async_forward_entry_setup(
                    self.config_entry, "binary_sensor"
                )
            )
            self.hass.async_add_job(
                self.hass.config_entries.async_forward_entry_setup(
                    self.config_entry, "switch"
                )
            )

    async def update(self, now):

        """Update status from the online service."""
        try:
            if not await self.connection.update():
                return False

            self.discover_pools(
                [x for x in self.connection._pools if x.pid not in self.pools]
            )

            async_dispatcher_send(self.hass, SIGNAL_STATE_UPDATED)    

            return True
        finally:
            async_track_point_in_utc_time(
                self.hass, self.update, utcnow() + timedelta(minutes=self.interval)
            )

    async def execute_pool_action(self, service):
        pid = service.data.get(CONF_PID).lower()
        action = service.data.get(CONF_ACTION).lower()
        # no actions yet
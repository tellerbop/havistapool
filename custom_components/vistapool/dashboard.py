#  Utilities for integration with Home Assistant (directly or via MQTT)

import logging
import re

_LOGGER = logging.getLogger(__name__)


class Instrument:
    def __init__(self, component, attr, name, icon=None):
        self._attr = attr
        self._component = component
        self._name = name
        self._connection = None
        self._pool = None
        self._icon = icon

    def __repr__(self):
        return self._name

    def configurate(self, **args):
        pass

    def camel2slug(self, s):
        """Convert camelCase to camel_case.
        >>> camel2slug('fooBar')
        'foo_bar'
        """
        return re.sub("([A-Z])", "_\\1", s).lower().lstrip("_")

    @property
    def slug_attr(self):
        return self.camel2slug(self._attr.replace(".", "_"))

    def setup(self, connection, pool, mutable=True, **config):
        self._connection = connection
        self._pool = pool

        if not mutable and self.is_mutable:
            _LOGGER.info("Skipping %s because mutable", self)
            return False

        if not self.is_supported:
            _LOGGER.debug(
                 "%s (%s:%s) is not supported", self, type(self).__name__, self._attr,
             )
            return False

        _LOGGER.debug("%s is supported", self)

        self.configurate(**config)

        return True

    @property
    def full_name(self):
        return "%s %s" % (self.name, self.pool_reference)

    @property
    def component(self):
        return self._component

    @property
    def icon(self):
        return self._icon

    @property
    def name(self):
        return self._name

    @property
    def attr(self):
        return self._attr

    @property
    def pool_name(self):
        return self._pool.name

    @property
    def pid(self):
        return self._pool.pid

    @property
    def pool_reference(self):
        return self._pool.ref

    @property
    def is_mutable(self):
        raise NotImplementedError("Must be set")

    @property
    def is_supported(self):
        supported = self._attr + "_supported"
        if hasattr(self._pool, supported):
            return getattr(self._pool, supported)
        if hasattr(self._pool, self._attr):
            return True
        return False

    @property
    def str_state(self):
        return self.state

    @property
    def state(self):
        if hasattr(self._pool, self._attr):
            return getattr(self._pool, self._attr)
        return self._pool.get_attr(self._attr)

    @property
    def attributes(self):
        return {}


class Sensor(Instrument):
    def __init__(self, attr, name, icon, unit):
        super().__init__(component="sensor", attr=attr, name=name, icon=icon)
        self._unit = unit
        self._convert = False

    def configurate(self, unit_system=None, **config):
        return

    @property
    def is_mutable(self):
        return False

    @property
    def str_state(self):
        if self.unit:
            return "%s %s" % (self.state, self.unit)
        else:
            return "%s" % self.state

    @property
    def state(self):
        val = super().state
        return val

    @property
    def unit(self):
        supported = self._attr + "_unit"
        if hasattr(self._pool, supported):
            return getattr(self._pool, supported)

        return self._unit


class BinarySensor(Instrument):
    def __init__(self, attr, name, device_class, icon=None):
        super().__init__(component="binary_sensor", attr=attr, name=name, icon=icon)
        self.device_class = device_class

    @property
    def is_mutable(self):
        return False

    @property
    def str_state(self):
        if self.state is None:
            _LOGGER.error("Can not encode state %s:%s", self._attr, self.state)
            return "?"
        return "On" if self.state else "Off"

    @property
    def state(self):
        val = super().state
        if isinstance(val, (bool, list)):
            #  for list (e.g. bulb_failures):
            #  empty list (False) means no problem
            return bool(val)        
        elif isinstance(val, str):
            return True if val == "ON" else False            
        return val

    @property
    def is_on(self):
        return self.state


class Switch(Instrument):
    def __init__(self, attr, name, icon):
        super().__init__(component="switch", attr=attr, name=name, icon=icon)

    @property
    def is_mutable(self):
        return True

    @property
    def str_state(self):
        return "On" if self.state else "Off"

    def is_on(self):
        return self.state

    def turn_on(self):
        pass

    def turn_off(self):
        pass

class LastUpdate(Instrument):
    def __init__(self):
        super().__init__(
            component="sensor",
            attr="last_update_time",
            name="Last Update",
            icon="mdi:update",
        )
        self.unit = None

    @property
    def is_mutable(self):
        return False

    @property
    def str_state(self):
        ts = super().state
        return str(ts.astimezone(tz=None)) if ts else None

    @property
    def state(self):
        val = super().state
        return val


def create_instruments():
    return [        
        LastUpdate(),        
        # Sensor(attr="location", name="Location", icon="mdi:map-marker", unit=None),
        Sensor(attr="temperature", name="Temperature", icon="mdi:thermometer", unit="C"),   
        Sensor(attr="ph", name="PH", icon="mdi:alpha-p-circle", unit="Ph"),
        Sensor(attr="ph_hi", name="PH High Value", icon="mdi:alpha-p-box", unit="Ph"),   
        Sensor(attr="rx", name="RX", icon="mdi:alpha-r-circle", unit="Rx"),   
        Sensor(attr="rx_target", name="RX Target", icon="mdi:alpha-r-box", unit="Rx"),           
        BinarySensor(attr="connected", name="Connected", device_class="connectivity"),        
        BinarySensor(attr="rx_relay_state", name="Rx Relay State", device_class="opening"),        
        BinarySensor(attr="ph_relay_state", name="Ph Relay State", device_class="opening"), 
        ]



class Dashboard:
    def __init__(self, connection, pool, **config):
        self.instruments = [
            instrument
            for instrument in create_instruments()
            if instrument.setup(connection, pool, **config)
        ]

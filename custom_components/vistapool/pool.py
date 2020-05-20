import logging

_LOGGER = logging.getLogger(__name__)
class PoolData:
    def __init__(self, config_entry):
        self.sensors = set()
        self.binary_sensors = set()
        self.switches = set()
        self.config_entry = config_entry
        self.pool = None

class CurrentPoolDataResponse:
    def __init__(self, data):
        data = data
        self.pid = data["id"]

class PoolDataResponse:
    def __init__(self, data):
        self.data_fields = []        
        self.data_fields.append(Field("temperature", data["main"]["temperature"], "C"))
        self.data_fields.append(Field("filtration_mode", data["main"]["filtrationMode"]))
        self.data_fields.append(Field("filtration_status", data["main"]["filtrationStatus"]))
        self.data_fields.append(Field("light_type", data["light"]["type"]))
        self.data_fields.append(Field("light_status", data["light"]["status"]))
        self.data_fields.append(Field("ph", data["modules"]["ph"]["currentValue"]))
        self.data_fields.append(Field("ph_hi", data["modules"]["ph"]["status"]["hi_value"]))
        self.data_fields.append(Field("ph_relay_state", data["modules"]["ph"]["status"]["status"]))        
        self.data_fields.append(Field("ph_color", data["modules"]["ph"]["status"]["color"]["hex"]))
        self.data_fields.append(Field("rx", data["modules"]["rx"]["currentValue"]))
        self.data_fields.append(Field("rx_target", data["modules"]["rx"]["status"]["value"]))
        self.data_fields.append(Field("rx_relay_state", data["modules"]["rx"]["status"]["relayStatus"]["status"]))
        self.data_fields.append(Field("rx_color", data["modules"]["rx"]["status"]["color"]["hex"]))
        for field in self.data_fields:
            _LOGGER.debug("%s", str(field))

class Field:
    def __init__(self, name: str, value, unit: str = ""):
        self.name = name
        self.value = value
        self.unit = unit
        

    def __str__(self):
        str_rep = str(self.name) + " " + str(self.value)
        if self.unit is not None:
            str_rep += self.unit
        return str_rep


class Pool:
    def __init__(self):
        self.pid = ""
        self.ref = ""
        self.location = ""
        self.connected = 0
        self.name = ""        

    def parse(self, data):
        self.pid = data.get("id")
        self.ref = data.get("reference")
        self.location = data.get("location")
        self.connected = data.get("connected")
        self.name = data.get("name")        

    def __str__(self):
        return str(self.__dict__)


class PoolResponse:
    def __init__(self):
        self.pools = []        

    def parse(self, data):
        for item in data.get("pools"):
            pool = Pool()
            pool.parse(item)
            self.pools.append(pool)

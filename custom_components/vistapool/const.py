DOMAIN = "vistapool"

CONF_PID = "pid"
CONF_POOLNAME = "poolname"
CONF_ACTION = "action"

MIN_UPDATE_INTERVAL = 5
DEFAULT_UPDATE_INTERVAL = 10

CONF_SERVICE_URL = "service_url"
CONF_MUTABLE = "mutable"

SIGNAL_STATE_UPDATED = "{}.updated".format(DOMAIN)
TRACKER_UPDATE = f"{DOMAIN}_tracker_update"

RESOURCES = [
    "temperature",
    "last_update_time",
    "local_time",
    "light_state_type",
    "light_state_status",
    "filtration_status",
    "filtration_mode",
    "filtration_time_remaining",
    "PH",
    "PH_status_type",
    "PH_status_hi_value",
    "PH_status_value",
    "PH_status_color_class",
    "PH_status_color_hex",
    "RX",
    "RX1",
    "RX_status_color_class",
    "RX_status_color_hex",    
]

COMPONENTS = {
    "sensor": "sensor",
    "binary_sensor": "binary_sensor",    
    "switch": "switch",
}

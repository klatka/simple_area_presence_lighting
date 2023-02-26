"""Constants for the integration."""

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.const import Platform

PLATFORMS: list[Platform] = [Platform.LIGHT, Platform.SWITCH]
DOMAIN = "simple_area_presence_lighting"

ALL_BINARY_SENSOR_DEVICE_CLASSES = [
    cls.value for cls in BinarySensorDeviceClass
]

CONF_NAME, DEFAULT_NAME = "name", "default"
CONF_AREA_ID, DEFAULT_AREA_ID = "area_id", "test_area"
CONF_USE_AREA_LIGHTS, DEFAULT_USE_AREA_LIGHTS = "use_area_lights", True
CONF_LIGHTS, DEFAULT_LIGHTS = "lights", []
(
    CONF_USE_AREA_PRESENCE_SENSORS,
    DEFAULT_USE_AREA_PRESENCE_SENSORS,
) = (
    "use_area_presence_sensor_entities",
    True,
)
(
    CONF_SENSOR_DEVICE_CLASSES,
    DEFAULT_SENSOR_DEVICE_CLASSES,
) = (
    "area_presence_sensor_device_classes",
    [
        BinarySensorDeviceClass.MOTION,
        BinarySensorDeviceClass.OCCUPANCY,
        BinarySensorDeviceClass.PRESENCE,
    ],
)
CONF_PRESENCE_SENSOR_ENTITIES, DEFAULT_PRESENCE_SENSOR_ENTITIES = (
    "presence_sensor_entities",
    [],
)
CONF_CREATE_LIGHT_GROUP, DEFAULT_CREATE_LIGHT_GROUP = (
    "create_light_group",
    False,
)
CONF_STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): cv.string,
    }
)

VALIDATION_TUPLES = [
    (CONF_AREA_ID, DEFAULT_AREA_ID, cv.string),
    (CONF_USE_AREA_LIGHTS, DEFAULT_USE_AREA_LIGHTS, bool),
    (CONF_LIGHTS, DEFAULT_LIGHTS, cv.entity_ids),
    (
        CONF_USE_AREA_PRESENCE_SENSORS,
        DEFAULT_USE_AREA_PRESENCE_SENSORS,
        bool,
    ),
    (
        CONF_SENSOR_DEVICE_CLASSES,
        DEFAULT_SENSOR_DEVICE_CLASSES,
        cv.ensure_list,
    ),
    (
        CONF_PRESENCE_SENSOR_ENTITIES,
        DEFAULT_PRESENCE_SENSOR_ENTITIES,
        cv.entity_ids,
    ),
    (CONF_CREATE_LIGHT_GROUP, DEFAULT_CREATE_LIGHT_GROUP, bool),
]

ACTION_TURN_OFF_LIGHTS = "turn_off"
ACTION_TURN_ON_LIGHTS = "turn_on"

ATTR_LIGHTS = "lights"
ATTR_PRESENCE = "presence"
ATTR_PRESENCE_ACTIVE = "active_sensors"
ATTR_PRESENCE_SENSOR_ENTITIES = "sensors"

LIGHT_GROUP_PREFIX_ID = f"{DOMAIN}_lights"
LIGHT_GROUP_PREFIX_NAME = "Area Lights"

SWITCH_AREA_DARK_ICON = "mdi:weather-night"
SWITCH_AREA_DARK_PREFIX_ID = f"{DOMAIN}_area_dark"
SWITCH_AREA_DARK_PREFIX_NAME = "Area Dark"
SWITCH_LIGHT_CONTROL_ICON = "mdi:lightbulb-auto-outline"
SWITCH_LIGHT_CONTROL_PREFIX_ID = f"{DOMAIN}"
SWITCH_LIGHT_CONTROL_PREFIX_NAME = "Simple Area Presence Lighting"
SWITCH_OVERRIDE_PRESENCE_ICON = "mdi:lightbulb-alert-outline"
SWITCH_OVERRIDE_PRESENCE_PREFIX_ID = f"{DOMAIN}_override_presence"
SWITCH_OVERRIDE_PRESENCE_PREFIX_NAME = "Override Presence"

TEST_LIGHTS = ["light.test"]
TEST_PRESENCE_SENSOR_ENTITIES = ["binary_sensor.presence"]

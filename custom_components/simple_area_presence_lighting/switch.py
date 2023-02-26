"""Switch for the integration."""
from __future__ import annotations

import logging


from homeassistant.components.light import DOMAIN as LIGHT_DOMAIN
from homeassistant.components.switch import SwitchEntity
from homeassistant.const import (
    ATTR_AREA_ID,
    ATTR_ENTITY_ID,
    EVENT_HOMEASSISTANT_STARTED,
    EVENT_STATE_CHANGED,
    SERVICE_TURN_OFF,
    SERVICE_TURN_ON,
    STATE_OFF,
    STATE_ON,
)
from homeassistant.core import Context, Event
from homeassistant.helpers.restore_state import RestoreEntity

from . import base
from .const import (
    ACTION_TURN_OFF_LIGHTS,
    ACTION_TURN_ON_LIGHTS,
    ATTR_LIGHTS,
    ATTR_PRESENCE,
    ATTR_PRESENCE_SENSOR_ENTITIES,
    CONF_AREA_ID,
    CONF_LIGHTS,
    CONF_NAME,
    CONF_PRESENCE_SENSOR_ENTITIES,
    CONF_SENSOR_DEVICE_CLASSES,
    CONF_USE_AREA_LIGHTS,
    CONF_USE_AREA_PRESENCE_SENSORS,
    DEFAULT_LIGHTS,
    DEFAULT_PRESENCE_SENSOR_ENTITIES,
    DEFAULT_SENSOR_DEVICE_CLASSES,
    DEFAULT_USE_AREA_LIGHTS,
    DEFAULT_USE_AREA_PRESENCE_SENSORS,
    DOMAIN,
    SWITCH_AREA_DARK_ICON,
    SWITCH_AREA_DARK_PREFIX_ID,
    SWITCH_AREA_DARK_PREFIX_NAME,
    SWITCH_LIGHT_CONTROL_ICON,
    SWITCH_LIGHT_CONTROL_PREFIX_ID,
    SWITCH_LIGHT_CONTROL_PREFIX_NAME,
    SWITCH_OVERRIDE_PRESENCE_ICON,
    SWITCH_OVERRIDE_PRESENCE_PREFIX_ID,
    SWITCH_OVERRIDE_PRESENCE_PREFIX_NAME,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities: bool):
    """Set up the switches."""

    # Get config
    entry_name = hass.data[DOMAIN][config_entry.entry_id][CONF_NAME]
    options = config_entry.options

    # Check if already configured
    if not options:
        return

    # Get area id
    # Warning: Check if None before use
    area_id = options[CONF_AREA_ID]

    all_lights = []

    # Get all lights in area
    if options.get(CONF_USE_AREA_LIGHTS, DEFAULT_USE_AREA_LIGHTS):
        # Check if there is an area set
        if not area_id:
            return

        all_lights = all_lights + base.get_lights_in_area(hass, area_id)

    # Add lights from options
    all_lights = all_lights + options.get(CONF_LIGHTS, DEFAULT_LIGHTS)

    # Check if there are any lights
    if not all_lights:
        return

    all_presence_sensor_entities = []

    # Get all presence sensing entities in area
    if options.get(
        CONF_USE_AREA_PRESENCE_SENSORS,
        DEFAULT_USE_AREA_PRESENCE_SENSORS,
    ):
        # Check if there is an area set
        if not area_id:
            return

        supported_device_classes = options.get(
            CONF_SENSOR_DEVICE_CLASSES,
            DEFAULT_SENSOR_DEVICE_CLASSES,
        )

        all_presence_sensor_entities = (
            all_presence_sensor_entities
            + base.get_presence_sensor_entities_in_area(
                hass, area_id, supported_device_classes
            )
        )

    # Add presence sensing entities from options
    all_presence_sensor_entities = (
        all_presence_sensor_entities
        + options.get(
            CONF_PRESENCE_SENSOR_ENTITIES, DEFAULT_PRESENCE_SENSOR_ENTITIES
        )
    )

    # Check if there are any presence sensing entities
    if not all_presence_sensor_entities:
        return

    # Create area dark switch
    area_dark_switch = AreaDarkSwitch(hass, entry_name)

    # Create override occupancy switch
    override_presence_switch = OverrideOccupancySwitch(hass, entry_name)

    # Create light control switch
    light_control_switch = LightControlSwitch(
        hass,
        entry_name,
        area_id,
        all_lights,
        all_presence_sensor_entities,
        area_dark_switch,
        override_presence_switch,
    )

    # Create all switches
    async_add_entities(
        [area_dark_switch, override_presence_switch, light_control_switch],
        update_before_add=True,
    )


class LightControlSwitch(SwitchEntity, RestoreEntity):
    """Representation of a light control switch."""

    _attr_has_entity_name = True

    def __init__(
        self,
        hass,
        entry_name,
        area_id,
        lights,
        presence_sensor_entities,
        area_dark_switch: AreaDarkSwitch,
        override_presence_switch: OverrideOccupancySwitch,
    ):
        """Initialize the light control switch."""
        self.hass = hass

        self.area_dark_switch = area_dark_switch
        self.override_presence_switch = override_presence_switch

        self._unique_id = f"{SWITCH_LIGHT_CONTROL_PREFIX_ID}_{entry_name}"
        self._name = f"{SWITCH_LIGHT_CONTROL_PREFIX_NAME} {entry_name}"

        self._icon = SWITCH_LIGHT_CONTROL_ICON
        self._state = None

        self._lights = lights
        self._presence_detected = False
        self._presence_sensor_entities = presence_sensor_entities
        self._presence_sensor_entities_active = []

        self._context = Context(id=DOMAIN)

        self._extra_state_attributes = {
            ATTR_AREA_ID: area_id,
            ATTR_LIGHTS: self._lights,
            ATTR_PRESENCE: self._presence_detected,
            ATTR_PRESENCE_SENSOR_ENTITIES: self._presence_sensor_entities,
        }

        _LOGGER.debug(
            "Light control switch created (%s)", self._unique_id
        )

    @property
    def name(self):
        """Return the name of the device if any."""
        return self._name

    @property
    def unique_id(self):
        """Return the unique ID of entity."""
        return self._unique_id

    @property
    def icon(self) -> str:
        """Icon to use in the frontend, if any."""
        return self._icon

    @property
    def is_on(self) -> bool | None:
        """Return true if switch is on."""
        return self._state

    @property
    def extra_state_attributes(self):
        """Return the attributes of the switch."""
        return self._extra_state_attributes

    async def async_turn_on(self, **kwargs) -> None:
        """Turn on switch."""
        _LOGGER.debug(
            "%s called 'async_turn_on', current state is '%s'",
            self._name,
            self._state,
        )

        if self.is_on:
            return

        _LOGGER.debug("Turning on %s", self._name)
        self._state = True
        await self._setup_listeners()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn off switch."""
        _LOGGER.debug(
            "%s called 'async_turn_off', current state is '%s'",
            self._name,
            self._state,
        )

        if not self.is_on:
            return

        _LOGGER.debug("Turning off %s", self._name)
        self._state = False

    async def async_added_to_hass(self) -> None:
        """Call when entity about to be added to hass."""
        if self.hass.is_running:
            await self._setup_listeners()
        else:
            self.hass.bus.async_listen_once(
                EVENT_HOMEASSISTANT_STARTED, self._setup_listeners
            )

        last_state = await self.async_get_last_state()
        is_new_entry = last_state is None
        if is_new_entry or last_state.state == STATE_ON:
            await self.async_turn_on()
        else:
            self._state = False

    def _update_attributes(self) -> None:
        """Update attributes."""

        # Update active presence sensing entities
        self._presence_sensor_entities_active = []
        for presence_sensing_entity in self._presence_sensor_entities:
            if self.hass.states.is_state(presence_sensing_entity, STATE_ON):
                self._presence_sensor_entities_active.append(
                    presence_sensing_entity
                )

        # Check if presence is overriden
        presence_overriden = self.hass.states.is_state(
            self.override_presence_switch.entity_id, STATE_ON
        )

        # Check if presence is detected
        self._presence_detected = False
        if self._presence_sensor_entities_active or presence_overriden:
            self._presence_detected = True

        self._extra_state_attributes.update(
            {
                ATTR_PRESENCE: self._presence_detected,
            }
        )

    async def _setup_listeners(self, _=None) -> None:
        _LOGGER.debug("%s called '_setup_listeners'", self._name)
        if not self.is_on or not self.hass.is_running:
            _LOGGER.debug("%s cancelled '_setup_listeners'", self._name)
            return

        # Update attributes
        self._update_attributes()

        # Listen for state changes
        self.hass.bus.async_listen(
            EVENT_STATE_CHANGED, self._handle_state_changed
        )

    async def _handle_state_changed(self, event: Event) -> None:
        """Track 'state_changed' events."""

        # Check if the event is for our presence sensing entity
        # or the dark mode switch
        # or the override occupancy switch
        entity_id = event.data.get(ATTR_ENTITY_ID, "")
        if not (
            entity_id in self._presence_sensor_entities
            or entity_id == self.area_dark_switch.entity_id
            or entity_id == self.override_presence_switch.entity_id
        ):
            return

        # Update attributes
        self._update_attributes()

        # State machine
        action = None
        new_state = event.data.get("new_state")
        old_state = event.data.get("old_state")
        if (
            new_state is not None
            and new_state.state == STATE_ON
            and old_state is not None
            and old_state.state == STATE_OFF
        ):
            action = ACTION_TURN_ON_LIGHTS
        elif (
            new_state is not None
            and new_state.state == STATE_OFF
            and old_state is not None
            and old_state.state == STATE_ON
        ):
            action = ACTION_TURN_OFF_LIGHTS

        _LOGGER.debug(
            "Detected a '%s' 'state_changed' action: '%s'",
            entity_id,
            action,
        )

        # Check if area is dark
        area_dark = self.hass.states.is_state(
            self.area_dark_switch.entity_id, STATE_ON
        )

        # Check if all lights are off
        all_lights_off = True
        for light in self._lights:
            if self.hass.states.get(light).state == STATE_ON:
                all_lights_off = False
                break

        # Determine if lights should be turned off
        if action == ACTION_TURN_OFF_LIGHTS:
            if not all_lights_off and (
                not area_dark or not self._presence_detected
            ):
                service_data = {ATTR_ENTITY_ID: self._lights}
                await self.hass.services.async_call(
                    LIGHT_DOMAIN,
                    SERVICE_TURN_OFF,
                    service_data,
                    context=self._context,
                )
                return

        # Determine if lights should be turned on
        if action == ACTION_TURN_ON_LIGHTS:
            if all_lights_off and (self._presence_detected and area_dark):
                service_data = {ATTR_ENTITY_ID: self._lights}
                await self.hass.services.async_call(
                    LIGHT_DOMAIN,
                    SERVICE_TURN_ON,
                    service_data,
                    context=self._context,
                )
                return


class OverrideOccupancySwitch(SwitchEntity, RestoreEntity):
    """Representation of a override occupancy switch."""

    _attr_has_entity_name = True

    def __init__(
        self,
        hass,
        entry_name,
    ):
        """Initialize the override occupancy switch."""
        self.hass = hass

        self._unique_id = f"{SWITCH_OVERRIDE_PRESENCE_PREFIX_ID}_{entry_name}"
        self._name = f"{SWITCH_OVERRIDE_PRESENCE_PREFIX_NAME} {entry_name}"

        self._icon = SWITCH_OVERRIDE_PRESENCE_ICON
        self._state = None

        _LOGGER.debug(
            "Override occupancy switch created (%s)", self._unique_id
        )

    @property
    def name(self):
        """Return the name of the device if any."""
        return self._name

    @property
    def unique_id(self):
        """Return the unique ID of entity."""
        return self._unique_id

    @property
    def icon(self) -> str:
        """Icon to use in the frontend, if any."""
        return self._icon

    @property
    def is_on(self) -> bool | None:
        """Return true if switch is on."""
        return self._state

    async def async_turn_on(self, **kwargs) -> None:
        """Turn on switch."""
        _LOGGER.debug("Turning on %s", self._name)
        self._state = True

    async def async_turn_off(self, **kwargs) -> None:
        """Turn off switch."""
        _LOGGER.debug("Turning off %s", self._name)
        self._state = False

    async def async_added_to_hass(self) -> None:
        """Call when entity about to be added to hass."""
        last_state = await self.async_get_last_state()
        _LOGGER.debug("last state of %s is %s", self._name, last_state)
        if last_state is not None and last_state.state == STATE_ON:
            await self.async_turn_on()
        else:
            await self.async_turn_off()


class AreaDarkSwitch(SwitchEntity, RestoreEntity):
    """Representation of a area dark switch."""

    _attr_has_entity_name = True

    def __init__(
        self,
        hass,
        entry_name,
    ):
        """Initialize the override occupancy switch."""
        self.hass = hass

        self._unique_id = f"{SWITCH_AREA_DARK_PREFIX_ID}_{entry_name}"
        self._name = f"{SWITCH_AREA_DARK_PREFIX_NAME} {entry_name}"

        self._icon = SWITCH_AREA_DARK_ICON
        self._state = None

        _LOGGER.debug("Area dark switch created (%s)", self._unique_id)

    @property
    def name(self):
        """Return the name of the device if any."""
        return self._name

    @property
    def unique_id(self):
        """Return the unique ID of entity."""
        return self._unique_id

    @property
    def icon(self) -> str:
        """Icon to use in the frontend, if any."""
        return self._icon

    @property
    def is_on(self) -> bool | None:
        """Return true if switch is on."""
        return self._state

    async def async_turn_on(self, **kwargs) -> None:
        """Turn on switch."""
        _LOGGER.debug("Turning on %s", self._name)
        self._state = True

    async def async_turn_off(self, **kwargs) -> None:
        """Turn off switch."""
        _LOGGER.debug("Turning off %s", self._name)
        self._state = False

    async def async_added_to_hass(self) -> None:
        """Call when entity about to be added to hass."""
        last_state = await self.async_get_last_state()
        _LOGGER.debug("last state of %s is %s", self._name, last_state)
        if last_state is not None and last_state.state == STATE_ON:
            await self.async_turn_on()
        else:
            await self.async_turn_off()

"""Config flow for the integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.components.binary_sensor import (
    DOMAIN as BINARY_SENSOR_DOMAIN,
)
from homeassistant.components.light import DOMAIN as LIGHT_DOMAIN
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from homeassistant.helpers.selector import (
    AreaSelector,
    AreaSelectorConfig,
    EntitySelector,
    EntitySelectorConfig,
    selector,
)

from .const import (
    ALL_BINARY_SENSOR_DEVICE_CLASSES,
    CONF_AREA_ID,
    CONF_CREATE_LIGHT_GROUP,
    CONF_LIGHTS,
    CONF_NAME,
    CONF_PRESENCE_SENSOR_ENTITIES,
    CONF_SENSOR_DEVICE_CLASSES,
    CONF_STEP_USER_DATA_SCHEMA,
    CONF_USE_AREA_LIGHTS,
    CONF_USE_AREA_PRESENCE_SENSORS,
    DOMAIN,
    VALIDATION_TUPLES,
)

_LOGGER = logging.getLogger(__name__)


async def validate_config(data: dict[str, Any]):
    """Validate the user input."""
    if not data[CONF_NAME]:
        raise ValueError("Name not given")


async def validate_options(hass, data: dict[str, Any]):
    """Validate the user input."""
    if not data[CONF_AREA_ID]:
        raise ValueError("Area not given")

    # Check if area exists
    # areas = area_registry.async_get(hass)
    # area = areas.async_get_area(data[CONF_AREA_ID])
    # if not area:
    #     raise ValueError("Area not exists")


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            try:
                await validate_config(user_input)
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

            if not errors:
                await self.async_set_unique_id(user_input[CONF_NAME])
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=user_input[CONF_NAME], data=user_input
                )

        """Show form to print error."""
        return self.async_show_form(
            step_id="user",
            data_schema=CONF_STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        errors = {}

        if user_input is not None:
            try:
                await validate_options(self.hass, user_input)
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

            if not errors:
                return self.async_create_entry(
                    title="Options", data=user_input
                )

        all_lights = [
            light for light in self.hass.states.async_entity_ids(LIGHT_DOMAIN)
        ]

        all_usable_sensors = [
            sensor
            for sensor in self.hass.states.async_entity_ids(
                BINARY_SENSOR_DOMAIN
            )
        ]

        selectors = {
            CONF_AREA_ID: self._build_selector_area(multiple=False),
            CONF_USE_AREA_LIGHTS: bool,
            CONF_LIGHTS: self._build_selector_entity(
                sorted(all_lights), multiple=True
            ),
            CONF_USE_AREA_PRESENCE_SENSORS: bool,
            CONF_SENSOR_DEVICE_CLASSES: self._build_selector_dropdown_values(
                sorted(ALL_BINARY_SENSOR_DEVICE_CLASSES), multiple=True
            ),
            CONF_PRESENCE_SENSOR_ENTITIES: self._build_selector_entity(
                all_usable_sensors, multiple=True
            ),
            CONF_CREATE_LIGHT_GROUP: bool,
        }

        options_schema = {}
        for name, default, validation in VALIDATION_TUPLES:
            key = vol.Optional(
                name, default=self.config_entry.options.get(name, default)
            )
            value = selectors.get(name, validation)
            options_schema[key] = value

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(options_schema),
            errors=errors,
        )

    def _build_selector_area(self, multiple=False):
        return AreaSelector(AreaSelectorConfig(multiple=multiple))

    def _build_selector_dropdown_values(self, options=[], multiple=False):
        return selector(
            {
                "select": {
                    "options": options,
                    "multiple": multiple,
                    "mode": "dropdown",
                }
            }
        )

    def _build_selector_entity(self, options=[], multiple=False):
        return NullableEntitySelector(
            EntitySelectorConfig(include_entities=options, multiple=multiple)
        )


class NullableEntitySelector(EntitySelector):
    def __call__(self, data):
        """Validate the passed selection, if passed."""
        if not data:
            return data

        return super().__call__(data)

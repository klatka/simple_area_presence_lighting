"""Tests for the config flow."""

import pytest
from homeassistant import data_entry_flow
from homeassistant.helpers import area_registry

from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.simple_area_presence_lighting.const import (
    CONF_AREA_ID,
    CONF_SENSOR_DEVICE_CLASSES,
    CONF_CREATE_LIGHT_GROUP,
    CONF_LIGHTS,
    CONF_NAME,
    CONF_PRESENCE_SENSOR_ENTITIES,
    CONF_USE_AREA_LIGHTS,
    CONF_USE_AREA_PRESENCE_SENSORS,
    DEFAULT_AREA_ID,
    DEFAULT_SENSOR_DEVICE_CLASSES,
    DEFAULT_NAME,
    DEFAULT_USE_AREA_LIGHTS,
    DEFAULT_USE_AREA_PRESENCE_SENSORS,
    DOMAIN,
    TEST_LIGHTS,
    TEST_PRESENCE_SENSOR_ENTITIES,
)


@pytest.mark.asyncio
async def test_flow_manual_configuration(hass):
    """Test that config flow works."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": "user"}
    )

    assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
    assert result["step_id"] == "user"
    assert result["handler"] == DOMAIN

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input={CONF_NAME: DEFAULT_NAME}
    )

    assert result["type"] == data_entry_flow.RESULT_TYPE_CREATE_ENTRY
    assert result["title"] == DEFAULT_NAME


@pytest.mark.asyncio
async def test_flow_set_options(hass):
    """Test updating options."""

    # Create test area
    areas = area_registry.async_get(hass)
    areas.async_get_or_create(name=DEFAULT_AREA_ID)
    area = areas.async_get_area_by_name(DEFAULT_AREA_ID)
    assert area

    # Create entry
    config = {
        CONF_NAME: DEFAULT_NAME,
    }

    entry = MockConfigEntry(
        domain=DOMAIN,
        title=DEFAULT_NAME,
        data=config,
    )

    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)

    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
    assert result["step_id"] == "init"

    # Check if options are empty
    config = hass.config_entries.async_get_entry(entry.entry_id).options
    assert CONF_AREA_ID not in config

    options = {
        CONF_AREA_ID: DEFAULT_AREA_ID,
        CONF_USE_AREA_LIGHTS: DEFAULT_USE_AREA_LIGHTS,
        CONF_LIGHTS: TEST_LIGHTS,
        CONF_USE_AREA_PRESENCE_SENSORS: DEFAULT_USE_AREA_PRESENCE_SENSORS,
        CONF_SENSOR_DEVICE_CLASSES: DEFAULT_SENSOR_DEVICE_CLASSES,
        CONF_PRESENCE_SENSOR_ENTITIES: TEST_PRESENCE_SENSOR_ENTITIES,
        CONF_CREATE_LIGHT_GROUP: False,
    }

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input=options,
    )

    assert result["type"] == data_entry_flow.RESULT_TYPE_CREATE_ENTRY
    for key, value in options.items():
        assert result["data"][key] == value

    # Check if options are not empty
    config = hass.config_entries.async_get_entry(entry.entry_id).options

    assert config[CONF_AREA_ID] == DEFAULT_AREA_ID
    assert config[CONF_LIGHTS] == TEST_LIGHTS
    assert (
        config[CONF_PRESENCE_SENSOR_ENTITIES] == TEST_PRESENCE_SENSOR_ENTITIES
    )
    assert not config[CONF_CREATE_LIGHT_GROUP]

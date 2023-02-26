"""Tests for the integration."""

import pytest
from homeassistant.config_entries import ConfigEntryState
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
async def test_valid_config_entry(hass):
    """Test setting up with valid config."""

    config = {
        CONF_NAME: DEFAULT_NAME,
    }

    entry = MockConfigEntry(
        domain=DOMAIN,
        data=config,
    )

    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert entry.state == ConfigEntryState.LOADED
    entries = hass.config_entries.async_entries(DOMAIN)
    assert len(entries) == 1


@pytest.mark.asyncio
async def test_unload_entry(hass):
    """Test removing entry."""

    config = {
        CONF_NAME: DEFAULT_NAME,
    }

    entry = MockConfigEntry(
        domain=DOMAIN,
        data=config,
    )

    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()

    assert entry.state == ConfigEntryState.NOT_LOADED


@pytest.mark.asyncio
async def test_reconfigure_options(hass):
    """Test setting up with valid config and reconfigure options."""

    config = {
        CONF_NAME: DEFAULT_NAME,
    }

    entry = MockConfigEntry(
        domain=DOMAIN,
        data=config,
    )

    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    options = {
        CONF_AREA_ID: DEFAULT_AREA_ID,
        CONF_USE_AREA_LIGHTS: DEFAULT_USE_AREA_LIGHTS,
        CONF_LIGHTS: TEST_LIGHTS,
        CONF_USE_AREA_PRESENCE_SENSORS: DEFAULT_USE_AREA_PRESENCE_SENSORS,
        CONF_SENSOR_DEVICE_CLASSES: DEFAULT_SENSOR_DEVICE_CLASSES,
        CONF_PRESENCE_SENSOR_ENTITIES: TEST_PRESENCE_SENSOR_ENTITIES,
        CONF_CREATE_LIGHT_GROUP: False,
    }

    assert hass.config_entries.async_update_entry(entry, options=options)
    await hass.async_block_till_done()

    assert entry.state == ConfigEntryState.LOADED

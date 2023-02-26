"""Tests for the integration."""

import pytest

from homeassistant.components.light import DOMAIN as LIGHT_DOMAIN
from homeassistant.const import (
    ATTR_ENTITY_ID,
    ATTR_FRIENDLY_NAME,
    STATE_OFF,
    STATE_ON,
    STATE_UNAVAILABLE,
)
from homeassistant.helpers import area_registry, entity_registry
from homeassistant.util import slugify

from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.simple_area_presence_lighting.const import (
    CONF_AREA_ID,
    CONF_CREATE_LIGHT_GROUP,
    CONF_LIGHTS,
    CONF_NAME,
    CONF_PRESENCE_SENSOR_ENTITIES,
    CONF_SENSOR_DEVICE_CLASSES,
    CONF_USE_AREA_LIGHTS,
    CONF_USE_AREA_PRESENCE_SENSORS,
    DEFAULT_AREA_ID,
    DEFAULT_NAME,
    DEFAULT_SENSOR_DEVICE_CLASSES,
    DEFAULT_USE_AREA_LIGHTS,
    DEFAULT_USE_AREA_PRESENCE_SENSORS,
    DOMAIN,
    LIGHT_GROUP_PREFIX_NAME,
    TEST_LIGHTS,
    TEST_PRESENCE_SENSOR_ENTITIES,
)


@pytest.mark.asyncio
async def test_setup_light_default(hass):
    """Test setup without light group so no light group should be created."""

    config = {
        CONF_NAME: DEFAULT_NAME,
    }

    options = {
        CONF_AREA_ID: DEFAULT_AREA_ID,
        CONF_USE_AREA_LIGHTS: DEFAULT_USE_AREA_LIGHTS,
        CONF_LIGHTS: TEST_LIGHTS,
        CONF_USE_AREA_PRESENCE_SENSORS: DEFAULT_USE_AREA_PRESENCE_SENSORS,
        CONF_SENSOR_DEVICE_CLASSES: DEFAULT_SENSOR_DEVICE_CLASSES,
        CONF_PRESENCE_SENSOR_ENTITIES: TEST_PRESENCE_SENSOR_ENTITIES,
        CONF_CREATE_LIGHT_GROUP: False,
    }

    entry = MockConfigEntry(
        domain=DOMAIN,
        data=config,
        options=options,
    )

    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert len(hass.states.async_entity_ids(LIGHT_DOMAIN)) == 0


@pytest.mark.asyncio
async def test_setup_light_create_light_group(hass):
    """Test light group with given lights."""

    config = {
        CONF_NAME: DEFAULT_NAME,
    }

    options = {
        CONF_AREA_ID: DEFAULT_AREA_ID,
        CONF_USE_AREA_LIGHTS: DEFAULT_USE_AREA_LIGHTS,
        CONF_LIGHTS: TEST_LIGHTS,
        CONF_USE_AREA_PRESENCE_SENSORS: DEFAULT_USE_AREA_PRESENCE_SENSORS,
        CONF_SENSOR_DEVICE_CLASSES: DEFAULT_SENSOR_DEVICE_CLASSES,
        CONF_PRESENCE_SENSOR_ENTITIES: TEST_PRESENCE_SENSOR_ENTITIES,
        CONF_CREATE_LIGHT_GROUP: True,
    }

    entry = MockConfigEntry(
        domain=DOMAIN,
        data=config,
        options=options,
    )

    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert len(hass.states.async_entity_ids(LIGHT_DOMAIN)) == 1

    entity_id = (
        f"{LIGHT_DOMAIN}."
        f"{slugify(LIGHT_GROUP_PREFIX_NAME)}_"
        f"{slugify(DEFAULT_NAME)}"
    )

    assert hass.states.is_state(entity_id, STATE_UNAVAILABLE)


@pytest.mark.asyncio
async def test_setup_light_create_light_group_after_reconfigured_options(hass):
    """Test light group with given lights after reconfigure options."""

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

    assert len(hass.states.async_entity_ids(LIGHT_DOMAIN)) == 0

    options = {
        CONF_AREA_ID: DEFAULT_AREA_ID,
        CONF_USE_AREA_LIGHTS: DEFAULT_USE_AREA_LIGHTS,
        CONF_LIGHTS: TEST_LIGHTS,
        CONF_USE_AREA_PRESENCE_SENSORS: DEFAULT_USE_AREA_PRESENCE_SENSORS,
        CONF_SENSOR_DEVICE_CLASSES: DEFAULT_SENSOR_DEVICE_CLASSES,
        CONF_PRESENCE_SENSOR_ENTITIES: TEST_PRESENCE_SENSOR_ENTITIES,
        CONF_CREATE_LIGHT_GROUP: True,
    }

    assert hass.config_entries.async_update_entry(entry, options=options)
    await hass.async_block_till_done()

    assert len(hass.states.async_entity_ids(LIGHT_DOMAIN)) == 1

    entity_id = (
        f"{LIGHT_DOMAIN}."
        f"{slugify(LIGHT_GROUP_PREFIX_NAME)}_"
        f"{slugify(DEFAULT_NAME)}"
    )

    assert hass.states.is_state(entity_id, STATE_UNAVAILABLE)


@pytest.mark.asyncio
async def test_setup_light_create_light_group_with_lights_in_area(hass):
    """Test light group with lights in area."""

    # Create test area
    area_reg = area_registry.async_get(hass)
    area_reg.async_get_or_create(DEFAULT_AREA_ID)
    area = area_reg.async_get_area_by_name(DEFAULT_AREA_ID)
    assert area

    # Get entity registry
    entity_reg = entity_registry.async_get(hass)

    # Create light entitiy and assign it to the specified area
    light_name = "Area Light 1"
    light1 = entity_reg.async_get_or_create(
        LIGHT_DOMAIN, "test", slugify(light_name)
    )
    light1 = entity_reg.async_update_entity(light1.entity_id, area_id=area.id)

    hass.states.async_set(
        light1.entity_id,
        STATE_ON,
        attributes={ATTR_FRIENDLY_NAME: light_name},
    )

    # Create another light entitiy and assign it to the specified area
    light_name = "Area Light 2"
    light2 = entity_reg.async_get_or_create(
        LIGHT_DOMAIN, "test", slugify(light_name)
    )
    light2 = entity_reg.async_update_entity(light2.entity_id, area_id=area.id)

    hass.states.async_set(
        light2.entity_id,
        STATE_OFF,
        attributes={ATTR_FRIENDLY_NAME: light_name},
    )

    assert len(hass.states.async_entity_ids(LIGHT_DOMAIN)) == 2

    # Create fal config entry
    config = {
        CONF_NAME: DEFAULT_NAME,
    }

    options = {
        CONF_AREA_ID: DEFAULT_AREA_ID,
        CONF_USE_AREA_LIGHTS: DEFAULT_USE_AREA_LIGHTS,
        CONF_LIGHTS: [],
        CONF_USE_AREA_PRESENCE_SENSORS: DEFAULT_USE_AREA_PRESENCE_SENSORS,
        CONF_SENSOR_DEVICE_CLASSES: DEFAULT_SENSOR_DEVICE_CLASSES,
        CONF_PRESENCE_SENSOR_ENTITIES: TEST_PRESENCE_SENSOR_ENTITIES,
        CONF_CREATE_LIGHT_GROUP: True,
    }

    entry = MockConfigEntry(
        domain=DOMAIN,
        data=config,
        options=options,
    )

    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert len(hass.states.async_entity_ids(LIGHT_DOMAIN)) == 3

    state = hass.states.get(
        f"{LIGHT_DOMAIN}."
        f"{slugify(LIGHT_GROUP_PREFIX_NAME)}_"
        f"{slugify(DEFAULT_NAME)}"
    )

    assert state.state == STATE_ON
    assert state.attributes[ATTR_ENTITY_ID] == [
        light1.entity_id,
        light2.entity_id,
    ]


@pytest.mark.asyncio
async def test_setup_light_create_light_group_with_lights_in_area_and_options(
    hass,
):
    """Test light group with lights in area and from options."""

    # Create test area
    area_reg = area_registry.async_get(hass)
    area_reg.async_get_or_create(DEFAULT_AREA_ID)
    area = area_reg.async_get_area_by_name(DEFAULT_AREA_ID)
    assert area

    # Get entity registry
    entity_reg = entity_registry.async_get(hass)

    # Create light entitiy and assign it to the specified area
    light_name = "Area Light 1"
    light1 = entity_reg.async_get_or_create(
        LIGHT_DOMAIN, "test", slugify(light_name)
    )
    light1 = entity_reg.async_update_entity(light1.entity_id, area_id=area.id)

    hass.states.async_set(
        light1.entity_id,
        STATE_ON,
        attributes={ATTR_FRIENDLY_NAME: light_name},
    )

    # Create another light entitiy and assign it to the specified area
    light_name = "Area Light 2"
    light2 = entity_reg.async_get_or_create(
        LIGHT_DOMAIN, "test", slugify(light_name)
    )
    light2 = entity_reg.async_update_entity(light2.entity_id, area_id=area.id)

    hass.states.async_set(
        light2.entity_id,
        STATE_OFF,
        attributes={ATTR_FRIENDLY_NAME: light_name},
    )

    assert len(hass.states.async_entity_ids(LIGHT_DOMAIN)) == 2

    # Create fal config entry
    config = {
        CONF_NAME: DEFAULT_NAME,
    }

    options = {
        CONF_AREA_ID: DEFAULT_AREA_ID,
        CONF_USE_AREA_LIGHTS: DEFAULT_USE_AREA_LIGHTS,
        CONF_LIGHTS: TEST_LIGHTS,
        CONF_USE_AREA_PRESENCE_SENSORS: DEFAULT_USE_AREA_PRESENCE_SENSORS,
        CONF_SENSOR_DEVICE_CLASSES: DEFAULT_SENSOR_DEVICE_CLASSES,
        CONF_PRESENCE_SENSOR_ENTITIES: TEST_PRESENCE_SENSOR_ENTITIES,
        CONF_CREATE_LIGHT_GROUP: True,
    }

    entry = MockConfigEntry(
        domain=DOMAIN,
        data=config,
        options=options,
    )

    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert len(hass.states.async_entity_ids(LIGHT_DOMAIN)) == 3

    state = hass.states.get(
        f"{LIGHT_DOMAIN}."
        f"{slugify(LIGHT_GROUP_PREFIX_NAME)}_"
        f"{slugify(DEFAULT_NAME)}"
    )

    assert state.state == STATE_ON
    assert light1.entity_id in state.attributes[ATTR_ENTITY_ID]
    assert light2.entity_id in state.attributes[ATTR_ENTITY_ID]

    all_test_lights_in_attr = all(
        item in state.attributes[ATTR_ENTITY_ID] for item in TEST_LIGHTS
    )
    assert all_test_lights_in_attr

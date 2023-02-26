"""Tests for the integration."""

import pytest

from homeassistant.components.binary_sensor import (
    DOMAIN as BINARY_SENSOR_DOMAIN,
    BinarySensorDeviceClass,
)

from homeassistant.components.switch import DOMAIN as SWITCH_DOMAIN
from homeassistant.const import (
    # ATTR_ENTITY_ID,
    ATTR_FRIENDLY_NAME,
    # SERVICE_TURN_OFF,
    # SERVICE_TURN_ON,
    # EVENT_STATE_CHANGED,
    STATE_OFF,
    STATE_ON,
)
from homeassistant.helpers import area_registry, entity_registry
from homeassistant.util import slugify

from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.simple_area_presence_lighting.const import (
    ATTR_LIGHTS,
    ATTR_PRESENCE_SENSOR_ENTITIES,
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
    SWITCH_AREA_DARK_PREFIX_NAME,
    SWITCH_LIGHT_CONTROL_PREFIX_NAME,
    SWITCH_OVERRIDE_PRESENCE_PREFIX_NAME,
    TEST_LIGHTS,
    TEST_PRESENCE_SENSOR_ENTITIES,
)


@pytest.mark.asyncio
async def test_setup_switch_default(hass):
    """Test switch."""

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

    assert len(hass.states.async_entity_ids(SWITCH_DOMAIN)) == 3

    state = hass.states.get(
        f"{SWITCH_DOMAIN}."
        f"{slugify(SWITCH_AREA_DARK_PREFIX_NAME)}_"
        f"{slugify(DEFAULT_NAME)}"
    )
    assert state.state == STATE_OFF

    state = hass.states.get(
        f"{SWITCH_DOMAIN}."
        f"{slugify(SWITCH_OVERRIDE_PRESENCE_PREFIX_NAME)}_"
        f"{slugify(DEFAULT_NAME)}"
    )
    assert state.state == STATE_OFF

    state = hass.states.get(
        f"{SWITCH_DOMAIN}."
        f"{slugify(SWITCH_LIGHT_CONTROL_PREFIX_NAME)}_"
        f"{slugify(DEFAULT_NAME)}"
    )
    assert state.state == STATE_ON


@pytest.mark.asyncio
async def test_setup_switch_after_reconfigured_options(hass):
    """Test switch after reconfigure options."""

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

    assert len(hass.states.async_entity_ids(SWITCH_DOMAIN)) == 0

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

    assert len(hass.states.async_entity_ids(SWITCH_DOMAIN)) == 3

    state = hass.states.get(
        f"{SWITCH_DOMAIN}."
        f"{slugify(SWITCH_AREA_DARK_PREFIX_NAME)}_"
        f"{slugify(DEFAULT_NAME)}"
    )
    assert state.state == STATE_OFF

    state = hass.states.get(
        f"{SWITCH_DOMAIN}."
        f"{slugify(SWITCH_OVERRIDE_PRESENCE_PREFIX_NAME)}_"
        f"{slugify(DEFAULT_NAME)}"
    )
    assert state.state == STATE_OFF

    state = hass.states.get(
        f"{SWITCH_DOMAIN}."
        f"{slugify(SWITCH_LIGHT_CONTROL_PREFIX_NAME)}_"
        f"{slugify(DEFAULT_NAME)}"
    )
    assert state.state == STATE_ON
    assert state.attributes[ATTR_LIGHTS] == TEST_LIGHTS
    assert (
        state.attributes[ATTR_PRESENCE_SENSOR_ENTITIES]
        == TEST_PRESENCE_SENSOR_ENTITIES
    )


@pytest.mark.asyncio
async def test_setup_switch_with_all_supported_entities_in_area(hass):
    """Test switch with entities of all supported device classes in area."""

    # Create test area
    area_reg = area_registry.async_get(hass)
    area_reg.async_get_or_create(name=DEFAULT_AREA_ID)
    area = area_reg.async_get_area_by_name(DEFAULT_AREA_ID)
    assert area

    # Get entity registry
    entity_reg = entity_registry.async_get(hass)

    # Create test binary sensor as presence sensor and assign to area
    sensor_name = "Motion Sensor 1"
    sensor1 = entity_reg.async_get_or_create(
        BINARY_SENSOR_DOMAIN, "test", slugify(sensor_name)
    )
    sensor1 = entity_reg.async_update_entity(
        sensor1.entity_id,
        area_id=area.id,
        device_class=BinarySensorDeviceClass.MOTION,
    )

    hass.states.async_set(
        sensor1.entity_id,
        STATE_ON,
        attributes={
            ATTR_FRIENDLY_NAME: sensor_name,
        },
    )

    # Create test binary sensor as presence sensor and assign to area
    sensor_name = "Occupancy Sensor 1"
    sensor2 = entity_reg.async_get_or_create(
        BINARY_SENSOR_DOMAIN, "test", slugify(sensor_name)
    )
    sensor2 = entity_reg.async_update_entity(
        sensor2.entity_id,
        area_id=area.id,
        device_class=BinarySensorDeviceClass.OCCUPANCY,
    )

    hass.states.async_set(
        sensor2.entity_id,
        STATE_ON,
        attributes={
            ATTR_FRIENDLY_NAME: sensor_name,
        },
    )

    # Create test binary sensor as presence sensor and assign to area
    sensor_name = "Presence Sensor 1"
    sensor3 = entity_reg.async_get_or_create(
        BINARY_SENSOR_DOMAIN, "test", slugify(sensor_name)
    )
    sensor3 = entity_reg.async_update_entity(
        sensor3.entity_id,
        area_id=area.id,
        device_class=BinarySensorDeviceClass.PRESENCE,
    )

    hass.states.async_set(
        sensor3.entity_id,
        STATE_ON,
        attributes={
            ATTR_FRIENDLY_NAME: sensor_name,
        },
    )

    assert len(hass.states.async_entity_ids(BINARY_SENSOR_DOMAIN)) == 3

    # Create config entry
    config = {
        CONF_NAME: DEFAULT_NAME,
    }

    options = {
        CONF_AREA_ID: DEFAULT_AREA_ID,
        CONF_USE_AREA_LIGHTS: DEFAULT_USE_AREA_LIGHTS,
        CONF_LIGHTS: TEST_LIGHTS,
        CONF_USE_AREA_PRESENCE_SENSORS: DEFAULT_USE_AREA_PRESENCE_SENSORS,
        CONF_SENSOR_DEVICE_CLASSES: DEFAULT_SENSOR_DEVICE_CLASSES,
        CONF_PRESENCE_SENSOR_ENTITIES: [],
        CONF_CREATE_LIGHT_GROUP: False,
    }

    entry = MockConfigEntry(
        domain=DOMAIN,
        data=config,
        options=options,
    )

    # Setup config entry
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert len(hass.states.async_entity_ids(SWITCH_DOMAIN)) == 3

    state = hass.states.get(
        f"{SWITCH_DOMAIN}."
        f"{slugify(SWITCH_LIGHT_CONTROL_PREFIX_NAME)}_"
        f"{slugify(DEFAULT_NAME)}"
    )

    assert state.state == STATE_ON
    assert state.attributes[ATTR_LIGHTS] == TEST_LIGHTS
    assert state.attributes[ATTR_PRESENCE_SENSOR_ENTITIES] == [
        sensor1.entity_id,
        sensor2.entity_id,
        sensor3.entity_id,
    ]


@pytest.mark.asyncio
async def test_setup_switch_with_entities_in_area_and_options(hass):
    """Test switch with entities in area and from options."""

    # Create test area
    area_reg = area_registry.async_get(hass)
    area_reg.async_get_or_create(name=DEFAULT_AREA_ID)
    area = area_reg.async_get_area_by_name(DEFAULT_AREA_ID)
    assert area

    # Get entity registry
    entity_reg = entity_registry.async_get(hass)

    # Create test binary sensor as presence sensor and assign to area
    sensor_name = "Motion Sensor 1"
    sensor1 = entity_reg.async_get_or_create(
        BINARY_SENSOR_DOMAIN, "test", slugify(sensor_name)
    )
    sensor1 = entity_reg.async_update_entity(
        sensor1.entity_id,
        area_id=area.id,
        device_class=BinarySensorDeviceClass.MOTION,
    )

    hass.states.async_set(
        sensor1.entity_id,
        STATE_ON,
        attributes={
            ATTR_FRIENDLY_NAME: sensor_name,
        },
    )

    assert len(hass.states.async_entity_ids(BINARY_SENSOR_DOMAIN)) == 1

    # Create config entry
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

    # Setup config entry
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert len(hass.states.async_entity_ids(SWITCH_DOMAIN)) == 3

    state = hass.states.get(
        f"{SWITCH_DOMAIN}."
        f"{slugify(SWITCH_LIGHT_CONTROL_PREFIX_NAME)}_"
        f"{slugify(DEFAULT_NAME)}"
    )

    assert state.state == STATE_ON
    assert state.attributes[ATTR_LIGHTS] == TEST_LIGHTS
    assert sensor1.entity_id in state.attributes[ATTR_PRESENCE_SENSOR_ENTITIES]

    all_test_sensors_in_attr = all(
        item in state.attributes[ATTR_PRESENCE_SENSOR_ENTITIES]
        for item in TEST_PRESENCE_SENSOR_ENTITIES
    )
    assert all_test_sensors_in_attr


# TODO: Check entities that has a device assigned to the area
# TODO: Check if there are states without entity registration


@pytest.mark.asyncio
async def test_state_machine_when_light_turned_on_and_dark(hass):
    """Test state machine when light turned on and dark."""

    # Set test states
    hass.states.async_set(TEST_LIGHTS[0], STATE_OFF)
    hass.states.async_set(TEST_PRESENCE_SENSOR_ENTITIES[0], STATE_OFF)

    # Create config entry
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

    # Setup config entry
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert len(hass.states.async_entity_ids(SWITCH_DOMAIN)) == 3

    # Simulate presence
    hass.states.async_set(
        TEST_PRESENCE_SENSOR_ENTITIES[0],
        STATE_ON,
    )

    # Get area dark entity id
    area_dark_entity_id = (
        f"{SWITCH_DOMAIN}."
        f"{slugify(SWITCH_AREA_DARK_PREFIX_NAME)}_"
        f"{slugify(DEFAULT_NAME)}"
    )

    # Simulate area is dark
    hass.states.async_set(
        area_dark_entity_id,
        STATE_ON,
    )

    # hass.bus.async_fire(
    #     EVENT_STATE_CHANGED, {ATTR_ENTITY_ID: area_dark_entity_id}
    # )

    # # Simulate area is dark
    # area_dark_entity_id = {
    #     ATTR_ENTITY_ID: (
    #         f"{SWITCH_DOMAIN}."
    #         f"{slugify(SWITCH_AREA_DARK_PREFIX_NAME)}_"
    #         f"{slugify(DEFAULT_NAME)}"
    #     )
    # }

    # TODO: Unable to call service switch/turn_on: Switch not found
    # await hass.services.async_call(
    #     SWITCH_DOMAIN, SERVICE_TURN_ON, area_dark_entity_id, blocking=True
    # )

    # await hass.async_block_till_done()
    # Check that light is turned on
    # assert hass.states.is_state(TEST_LIGHTS[0], STATE_ON)

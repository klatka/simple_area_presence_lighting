"""Base for the integration."""
from __future__ import annotations

import logging

from homeassistant.components.binary_sensor import (
    DOMAIN as BINARY_SENSOR_DOMAIN,
)
from homeassistant.components.light import DOMAIN as LIGHT_DOMAIN
from homeassistant.helpers import device_registry, entity_registry


_LOGGER = logging.getLogger(__name__)


def get_lights_in_area(hass, area_id):
    lights = []

    # Get device registry
    device_reg = device_registry.async_get(hass)

    # Get entity registry
    entity_reg = entity_registry.async_get(hass)

    # Get all entities assigned to the area
    for state in hass.states.async_all(LIGHT_DOMAIN):
        entity = entity_reg.async_get(state.entity_id)

        if entity is None:
            continue

        device = device_reg.async_get(entity.device_id)
        if (
            hasattr(entity, "area_id")  # Check for 'area_id' attribute
            and entity.area_id == area_id
            or (
                device is not None  # add a check for NoneType
                and hasattr(device, "area_id")  # Check for 'area_id' attribute
                and device.area_id == area_id
            )
        ):
            lights.append(state.entity_id)

    _LOGGER.debug("Lights in area: %s", lights)

    return lights


def get_presence_sensor_entities_in_area(
    hass, area_id, supported_device_classes
):
    presence_sensor_entities = []

    # Get device registry
    device_reg = device_registry.async_get(hass)

    # Get entity registry
    entity_reg = entity_registry.async_get(hass)

    for state in hass.states.async_all(BINARY_SENSOR_DOMAIN):
        entity = entity_reg.async_get(state.entity_id)

        if entity is None:
            continue

        device = device_reg.async_get(entity.device_id)
        if (
            hasattr(entity, "area_id")  # Check for 'area_id' attribute
            and entity.area_id == area_id
            or (
                device is not None  # add a check for NoneType
                and hasattr(device, "area_id")  # Check for 'area_id' attribute
                and device.area_id == area_id
            )
            and entity.device_class in supported_device_classes
        ):
            presence_sensor_entities.append(state.entity_id)

    _LOGGER.debug(
        "Presence sensing entities in area: %s", presence_sensor_entities
    )

    return presence_sensor_entities

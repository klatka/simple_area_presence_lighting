"""Light for the integration."""
from __future__ import annotations

import logging

from homeassistant.components.group.light import LightGroup

from . import base
from .const import (
    CONF_AREA_ID,
    CONF_CREATE_LIGHT_GROUP,
    CONF_LIGHTS,
    CONF_NAME,
    CONF_USE_AREA_LIGHTS,
    DEFAULT_CREATE_LIGHT_GROUP,
    DEFAULT_LIGHTS,
    DEFAULT_USE_AREA_LIGHTS,
    DOMAIN,
    LIGHT_GROUP_PREFIX_ID,
    LIGHT_GROUP_PREFIX_NAME,
)


_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities: bool):
    """Set up the light group."""
    entry_name = hass.data[DOMAIN][config_entry.entry_id][CONF_NAME]
    options = config_entry.options

    # Check if already configured
    if not options:
        return

    all_lights = []

    # Get all lights in area
    if options.get(CONF_USE_AREA_LIGHTS, DEFAULT_USE_AREA_LIGHTS):
        # Check if there is an area set
        area_id = options[CONF_AREA_ID]

        if not area_id:
            return

        all_lights = all_lights + base.get_lights_in_area(hass, area_id)

    # Add lights from options
    all_lights = all_lights + options.get(CONF_LIGHTS, DEFAULT_LIGHTS)

    # Check if there are any lights
    if not all_lights:
        return

    # Check if light group should be created
    if not options.get(CONF_CREATE_LIGHT_GROUP, DEFAULT_CREATE_LIGHT_GROUP):
        return

    lg_unique_id = f"{LIGHT_GROUP_PREFIX_ID}_{entry_name}"
    lg_name = f"{LIGHT_GROUP_PREFIX_NAME} {entry_name}"
    lg_entity_ids = [entity_id for entity_id in all_lights]

    # Create light group
    async_add_entities(
        [
            LightGroup(
                unique_id=lg_unique_id,
                name=lg_name,
                entity_ids=lg_entity_ids,
                mode=False,
            )
        ],
        update_before_add=True,
    )

    _LOGGER.debug("Light group created (%s)", lg_unique_id)

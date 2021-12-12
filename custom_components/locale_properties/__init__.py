# SPDX-FileCopyrightText: 2021 The ha-locale-properties Authors
#
# SPDX-License-Identifier: Apache-2.0

import logging

from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN
from .scraper import fetch_uncollected_deliveries

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass, config):
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass, entry):
    _LOGGER.debug(
        f"async_setup_entry({entry.data[CONF_HOST]}, {entry.data[CONF_USERNAME]}, PASSWORD_OMITTED)"
    )
    try:
        await fetch_uncollected_deliveries(
            base_url=entry.data[CONF_HOST],
            email=entry.data[CONF_USERNAME],
            password=entry.data[CONF_PASSWORD],
            session=async_get_clientsession(hass),
        )
    except Exception:
        _LOGGER.debug("async_setup_entry() sanity check failed", exc_info=True)
        return False

    _LOGGER.debug("sanity check completed")

    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )

    return True

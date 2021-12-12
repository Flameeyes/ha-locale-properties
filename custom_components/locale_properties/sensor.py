# SPDX-FileCopyrightText: 2021 The ha-locale-properties Authors
#
# SPDX-License-Identifier: Apache-2.0

import datetime
import logging
from urllib.parse import urlparse

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.typing import HomeAssistantType

from .scraper import fetch_uncollected_deliveries

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = datetime.timedelta(minutes=5)


class LocaleUncollectedDeliveries(SensorEntity):
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:package-variant-closed"

    def __init__(self, base_url, email, password):
        _LOGGER.debug(f"LocaleUncollectedDeliveries({base_url}, {email}, {password})")
        self._base_url = base_url
        self._hostname = urlparse(base_url).netloc

        self._email = email
        self._password = password

        self._state = None

    @property
    def unique_id(self):
        return f"{self._hostname}_{self._email}_uncollected_deliveries"

    @property
    def name(self):
        return f"Uncollected Deliveries for {self._email}"

    @property
    def state(self):
        return self._state

    async def async_update(self):
        _LOGGER.debug("async_update")
        self._state = await fetch_uncollected_deliveries(
            base_url=self._base_url,
            email=self._email,
            password=self._password,
            session=async_get_clientsession(self.hass),
        )


async def async_setup_entry(
    hass: HomeAssistantType, entry: ConfigEntry, async_add_entities
) -> None:
    _LOGGER.debug(
        f"async_setup_entry({entry.data[CONF_HOST]}, {entry.data[CONF_USERNAME]}, PASSWORD_OMITTED)"
    )
    async_add_entities(
        [
            LocaleUncollectedDeliveries(
                entry.data[CONF_HOST],
                entry.data[CONF_USERNAME],
                entry.data[CONF_PASSWORD],
            )
        ],
        True,
    )

# SPDX-FileCopyrightText: 2021 The ha-locale-properties Authors
#
# SPDX-License-Identifier: Apache-2.0

import logging
from urllib.parse import urlparse

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN
from .scraper import fetch_uncollected_deliveries

_LOGGER = logging.getLogger(__name__)


class LocaleConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):

    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            _LOGGER.debug(f"async_step_user user_info={user_input!r}")

            email = user_input[CONF_USERNAME]
            host = urlparse(user_input[CONF_HOST]).netloc

            await self.async_set_unique_id(f"{host} {email}")

            try:
                await fetch_uncollected_deliveries(
                    base_url=user_input[CONF_HOST],
                    email=user_input[CONF_USERNAME],
                    password=user_input[CONF_PASSWORD],
                    session=async_get_clientsession(self.hass),
                )
            except Exception:
                _LOGGER.debug("async_step_user connection error", exc_info=True)
                return self.async_abort(reason="connection_error")

            return self.async_create_entry(
                title=f"{host} ({email})",
                data=user_input,
            )

        data_schema = {
            vol.Required(CONF_HOST): str,  # vol.FqdnUrl,
            vol.Required(CONF_USERNAME): str,  # vol.Email,
            vol.Required(CONF_PASSWORD): str,
        }

        return self.async_show_form(step_id="user", data_schema=vol.Schema(data_schema))

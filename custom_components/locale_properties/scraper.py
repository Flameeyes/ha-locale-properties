# SPDX-FileCopyrightText: 2021 The ha-locale-properties Authors
#
# SPDX-License-Identifier: Apache-2.0

import json
import logging
from urllib.parse import urljoin, urlparse

import aiohttp
import bs4
from homeassistant.exceptions import ConfigEntryAuthFailed

_LOGGER = logging.getLogger(__name__)


async def fetch_uncollected_deliveries(
    *, base_url: str, email: str, password: str, session: aiohttp.ClientSession
) -> int:
    if urlparse(base_url).scheme == "":
        base_url = f"https://{base_url}"

    authorize_url = urljoin(base_url, "/home/authorize")
    deliveries_url = urljoin(base_url, "/homepage/widget/deliveries")

    jar = aiohttp.CookieJar()

    await session.get(
        base_url,
        cookies=jar,
        raise_for_status=True,
    )

    async with session.post(
        authorize_url,
        data={
            "email": email,
            "password": password,
        },
        cookies=jar,
        allow_redirects=False,
        raise_for_status=True,
    ) as auth_result:

        if auth_result.status != 302:
            _LOGGER.error(f"/home/authorize request failed: {auth_result!r}")
            raise ConfigEntryAuthFailed("/home/authorize request failed")

    async with session.post(
        deliveries_url,
        data={"ignore-cache": "true"},
        cookies=jar,
        headers={"X-Requested-With": "XMLHttpRequest"},
        raise_for_status=True,
    ) as deliveries:

        deliveries_text = await deliveries.text()

    if deliveries_text == "logout":
        raise ConfigEntryAuthFailed("Session Expired")

    deliveries_json = json.loads(deliveries_text)
    deliveries_html = deliveries_json["widgets"][0]["html"]

    _LOGGER.debug(f"widget HTML: {deliveries_html!r}")

    deliveries_soup = bs4.BeautifulSoup(deliveries_html, "html.parser")
    uncollected_packages = deliveries_soup.find(
        "h4", string="Uncollected Packages"
    ).next_sibling.next_sibling

    if uncollected_packages.attrs["class"] != ["delivery-stat"]:
        _LOGGER.error(f"Unexpected sibling: {uncollected_packages!r}")
        raise ValueError("Unexpected sibling!")

    return int(uncollected_packages.next_element.strip())

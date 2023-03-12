"""The Berlin (BVG) and Brandenburg (VBB) transport integration."""
from __future__ import annotations
import logging
from typing import Optional
from datetime import datetime, timedelta

import requests

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.sensor import PLATFORM_SCHEMA
from .const import (  # pylint: disable=unused-import
    DOMAIN,  # noqa
    SCAN_INTERVAL,  # noqa
    API_ENDPOINT,
    API_KEY,
    API_MAX_RESULTS,
    CONF_DEPARTURES,
    CONF_DEPARTURES_STOP_ID,
    CONF_DEPARTURES_WALKING_TIME,
    CONF_DEPARTURES_NAME,
)
from .departure import Departure

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    _: DiscoveryInfoType | None = None,
) -> None:
    """Set up the sensor platform."""
    if CONF_DEPARTURES in config:
        for departure in config[CONF_DEPARTURES]:
            add_entities([TransportSensor(hass, departure)])


class TransportSensor(SensorEntity):
    departures: list[Departure] = []

    def __init__(self, hass: HomeAssistant, config: dict) -> None:
        self.hass: HomeAssistant = hass
        self.config: dict = config
        self.stop_id: str = config[CONF_DEPARTURES_STOP_ID]
        self.sensor_name: str | None = config.get(CONF_DEPARTURES_NAME)
        self.walking_time: int = config.get(CONF_DEPARTURES_WALKING_TIME) or 1
        # we add +1 minute anyway to delete the "just gone" transport

    @property
    def name(self) -> str:
        return self.sensor_name or f"Stop ID: {self.stop_id}"

    # @property
    # def icon(self) -> str:
    #     next_departure = self.next_departure()
    #     if next_departure:
    #         return next_departure.icon
    #     return DEFAULT_ICON

    @property
    def unique_id(self) -> str:
        return f"stop_{self.stop_id}_{self.sensor_name}_departures"

    @property
    def state(self) -> str:
        next_departure = self.next_departure()
        if next_departure:
            return f"Next {next_departure.line_name} at {next_departure.time}"
        return "N/A"

    @property
    def extra_state_attributes(self):
        return {
            "departures": [departure.to_dict() for departure in self.departures or []]
        }
    # core home assist дергает тольео след метод
    def update(self):
        self.departures = self.fetch_departures()

    def fetch_departures(self) -> Optional[list[Departure]]:
        try:
            response = requests.get(
                url=API_ENDPOINT,
                headers = {
                    'X-Access-Token':API_KEY
                    },
                params = {
                    'ids': self.stop_id,
                    'timeFrom': datetime.utcnow(),
                    'minuteBefore': self.walking_time * (-1),
                    'preferredTimezone':'Europe_Prague',
                    'limit': API_MAX_RESULTS,
                    },
                timeout=30,
            )
            response.raise_for_status()
        except requests.exceptions.HTTPError as ex:
            _LOGGER.warning(f"API error: {ex}")
            return []
        except requests.exceptions.Timeout as ex:
            _LOGGER.warning(f"API timeout: {ex}")
            return []

        _LOGGER.debug(f"OK: departures for {self.stop_id}: {response.text}")

        # parse JSON response
        try:
            departures = response.json()
        except requests.exceptions.InvalidJSONError as ex:
            _LOGGER.error(f"API invalid JSON: {ex}")
            return []

        # convert api data into objects
        unsorted = [Departure.from_dict(departure) for departure in departures]
        return sorted(unsorted, key=lambda d: d.timestamp)

    def next_departure(self):
        if self.departures and isinstance(self.departures, list):
            return self.departures[0]
        return None

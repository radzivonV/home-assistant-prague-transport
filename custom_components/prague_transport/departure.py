from dataclasses import dataclass
from datetime import datetime


@dataclass
class Departure:
    """Departure dataclass to store data from API:
    https://api.golemio.cz/v2/pid/docs/openapi/#/%F0%9F%9A%8F%20PID%20Departure%20Boards/get_pid_departureboards"""

    trip_id: str
    departure_timestamp: datetime
    departure_time: datetime
    route_name: str
    headsign: str | None = None,
    delay: int | None = None

    @classmethod
    def from_dict(cls, source):
        timestamp=datetime.fromisoformat(source.get("departure_timestamp").get("scheduled"))
        return cls(    
            trip_id=source.get('trip').get('id'),
            departure_timestamp=timestamp,
            departure_time=timestamp.strftime("%H:%M"),
            route_name = source.get("route").get("short_name"),
            headsign = source.get("trip").get("headsign"),
            delay = source.get("delay").get('minutes') or None
        )

    def to_dict(self):
        return {
            "route_name": self.route_name,
            "departure_time": self.departure_time,
            "headsign": self.headsign,
            "delay": self.delay
        }

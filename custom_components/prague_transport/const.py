from datetime import timedelta

DOMAIN = "prague_transport"
SCAN_INTERVAL = timedelta(seconds=90)
API_ENDPOINT = "https://api.golemio.cz/v2/pid/departureboards"
with open('api_key.txt') as f:
    API_KEY =  f.read()

API_MAX_RESULTS = 10

CONF_DEPARTURES = "departures"
CONF_DEPARTURES_NAME = "name"
CONF_DEPARTURES_STOP_ID = "stop_id"
CONF_DEPARTURES_WALKING_TIME = "walking_time"
CONF_DEPARTURED_PLATFORM = "platform"

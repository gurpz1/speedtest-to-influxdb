from typing import NamedTuple


class InfluxDB(NamedTuple):
    url = "http://localhost:8086"
    bucket = "speedtest/autogen"
    token = "speedtest:speedtest"
    org = "-"
    timeout = 6000
    verify_ssl = False
import time
import random
import asyncio


class SatelliteTelemetry:
    def __init__(self, name):
        self.name = name
        self.actuate = False
        self.payload = False
        self.lowpower = False
        self.idle = True
        self.start_time = time.time()  # For calculating uptime
        self.telemetry = {
            "attitude": {

            },
            "angular_rate": {

            },
            "bat_voltage": {

            },
            "temp": {

            },
            "t_since_shutdown": {

            },
            "t_since_boot": {

            },
            "last_uplink_success": {

            },
            "t_since_uplink": {

            },
            "uplink_count": {

            },
            "reset_count": {

            },
            "reboot_code": {

            },
            "mekf_diverged": {

            },
            "antenna_deployment": {

            }

        }



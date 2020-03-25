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

    async def relay_telemetry(self, packet, gateway):

            metrics = []
            for subsystem in self.telemetry:
                for metric in self.telemetry[subsystem]:
                    metrics.append({
                        "system": self.name,
                        "subsystem": subsystem,
                        "metric": metric,
                        "value": self.telemetry[subsystem][metric]["value"],
                        "timestamp": int(time.time() * 1000)
                    })
            metrics.append({
                "system": self.name,
                "subsystem": "obc",
                "metric": "uptime",
                "value": (time.time() - self.start_time),
                "timestamp": int(time.time() * 1000)

            })
            asyncio.ensure_future(gateway.transmit_metrics(metrics=metrics))
            await asyncio.sleep(1)



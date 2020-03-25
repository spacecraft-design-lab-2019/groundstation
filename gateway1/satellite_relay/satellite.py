import asyncio
import time
import traceback
from random import randint
import requests
import logging
import re
import json
import datetime
import os
import serial

from satellite_telemetry import SatelliteTelemetry

logger = logging.getLogger(__name__)

ser = serial.Serial('/dev/ttyUSB0') # Change this port as required depending on configuration.


class CommandCancelledError(Exception):
    """Raised when a command is cancelled to halt the progress of that command"""


class Sat:
    def __init__(self, name="Space Oddity"):
        self.name = name
        self.telemetry = SatelliteTelemetry(name=name)
        self.file_list = []
        self.running_commands = {}
        self.force_cancel = True  # Forces all commands to be cancelled, regardless of run state.
        self.definitions = {
            "ping": {
                "display_name": "Ping",
                "description": "Ping",
                "tags": ["testing", "operations"],
                "fields": []
            },
            "error": {
                "display_name": "Error Command",
                "description": "Always errors to show the error process.",
                "tags": ["testing"],
                "fields": []
            },
            "update_file_list": {
                "display_name": "Update File List",
                "description": "Downlinks the latest file list from the spacecraft.",
                "tags": ["files", "operations"],
                "fields": []
            },
            "uplink_file": {
                "display_name": "Uplink File",
                "description": "Uplink a staged file to the spacecraft.",
                "tags": ["files"],
                "fields": [
                    {"name": "gateway_download_path", "type": "string"}
                ]
            },
            "downlink_file": {
                "display_name": "Downlink File",
                "description": "Downlink an image from the Spacecraft.",
                "tags": ["files"],
                "fields": [
                    {"name": "filename", "type": "string"}
                ]
            },
            "picture": {
                "display_name": "Take a picture",
                "description": "Commands the spacecraft to take a photo",
                "tags": ["operations", "testing"],
                "fields": []
            },
            "actuate": {
                "display_name": "Actuate torquers",
                "description": "Intakes a dipole moment and outputs a new orientation for the spacecraft.",
                "tags": ["operations"],
                "fields": [
                    {"name": "dipole", "type": "float"}
                ]
            },
            "state": {
                "display_name": "Changes spacecraft state",
                "description": "Accepts state input and changes state of the spacecraft.",
                "tags": ["operations", "testing"],
                "fields": [
                    {"name": "state", "type": "integer"}
                ]
            }
        }

    async def cancel_callback(self, id, gateway):

        if str(id) in self.running_commands:
            self.running_commands[str(id)]["cancel"] = True
        elif self.force_cancel and str(id) not in self.running_commands:
            asyncio.ensure_future(gateway.cancel_command(command_id=id))
            asyncio.ensure_future(gateway.transmit_events(events=[{
                "system": self.name,
                "type": "Command Cancellation Forced",
                "command_id": id,
                "level": "warning",
                "message": "Command is not running. Forcing state to Cancelled. Unable to verify if it was actually run on the System."
            }]))
        else:
            asyncio.ensure_future(gateway.transmit_events(events=[{
                "system": self.name,
                "type": "Command Cancellation Failed",
                "command_id": id,
                "level": "warning",
                "message": "Command is not running. Unable to cancel command."
            }]))

    def check_cancelled(self, id, gateway):
        if self.running_commands[str(id)]["cancel"]:
            # Raise an exception to immediately stop the command operations
            raise(CommandCancelledError(f"Command {id} Cancelled"))
        else:
            return

    async def command_callback(self, command, gateway):
        self.running_commands[str(command.id)] = {"cancel": False}
        try:
            if command.type == "ping":
                ser.write("send") # Add command text for ping here.
                pong = ser.readline() # See if response
                if "blah" in pong: # Fill in response for ping here.
                    asyncio.ensure_future(gateway.complete_command(
                        command_id=command.id, output="pong"))

            elif command.type == "update_file_list":
                """
                Sends a file to Major Tom.
                """
                ser.write("") # Fill in relevant command here
                ser.readline() # Fill in required size for a file. Adjust wait times etc.
                for i in range(1, randint(2, 4)):
                    self.file_list.append({
                        "name": f'Payload-Image-{(len(self.file_list)+1):04d}.png',
                        "size": randint(2000000, 3000000), # fill in real file format later
                        "timestamp": int(time.time() * 1000) + i*10,
                        "metadata": {"type": "image", "lat": (randint(-89, 89) + .0001*randint(0, 9999)), "lng": (randint(-179, 179) + .0001*randint(0, 9999))}
                        # Fill in real lat/long later!
                    })

                self.check_cancelled(id=command.id, gateway=gateway)
                asyncio.ensure_future(gateway.update_file_list(
                    system=self.name, files=self.file_list))
                await asyncio.sleep(3)
                self.check_cancelled(id=command.id, gateway=gateway)
                asyncio.ensure_future(gateway.complete_command(
                    command_id=command.id,
                    output="Updated Remote File List"
                ))

            elif command.type == "error":
                """
                Always errors. Used for testing
                """
                self.check_cancelled(id=command.id, gateway=gateway)
                asyncio.ensure_future(gateway.transmit_command_update(
                    command_id=command.id,
                    state="uplinking_to_system",
                    dict={
                        "status": "Uplinking Command"
                    }
                ))
                await asyncio.sleep(3)
                self.check_cancelled(id=command.id, gateway=gateway)
                asyncio.ensure_future(gateway.fail_command(
                    command_id=command.id, errors=["Command failed to execute."]))

            elif command.type == "state":
                """
                Sends changes in satellite state to the satellite. 
                """
                state = command.fields["gateway_download_path"]
                asyncio.ensure_future(gateway.transmit_command_update(
                    command_id=command.id,
                    state="transmitted_to_system",
                    dict={
                        "status": "Transmitted State Command",
                        "payload": state
                    }
                ))
                await asyncio.sleep(3)
                self.check_cancelled(id=command.id, gateway=gateway)
                self.telemetry.state = True

                ser.write(state) # Is there a state change awk. bit? If so then can confirm here!
                asyncio.ensure_future(gateway.complete_command(
                    command_id=command.id,
                    output="Spacecraft Confirmed In State " + state
                ))

            elif command.type == "actuate":
                """
                Sends changes in satellite state to the satellite. 
                """
                dipole = command.fields["gateway_download_path"]
                asyncio.ensure_future(gateway.transmit_command_update(
                    command_id=command.id,
                    state="transmitted_to_system",
                    dict={
                        "status": "Transmitted Actuate Command to " + dipole,
                        "payload": dipole
                    }
                ))
                await asyncio.sleep(3)
                self.check_cancelled(id=command.id, gateway=gateway)
                self.telemetry.state = True

                ser.write(dipole) # Add the correct commanding format
                asyncio.ensure_future(gateway.complete_command(
                    command_id=command.id,
                    output="Spacecraft Confirmed Dipole" + dipole
                ))

            elif command.type == "picture":
                """
                Sends changes in satellite state to the satellite. 
                """
                asyncio.ensure_future(gateway.transmit_command_update(
                    command_id=command.id,
                    state="transmitted_to_system",
                    dict={
                        "status": "Transmitted Picture Command",
                    }
                ))
                await asyncio.sleep(3)
                self.check_cancelled(id=command.id, gateway=gateway)
                self.telemetry.state = True

                ser.write("take picture") # add command name!

                asyncio.ensure_future(gateway.complete_command(
                    command_id=command.id,
                    output="Spacecraft Confirmed Picture"
                ))

            elif command.type == "uplink_file":
                """
                Simulates uplinking a file by going through the whole progress bar scenario
                """
                self.check_cancelled(id=command.id, gateway=gateway)
                asyncio.ensure_future(gateway.transmit_command_update(
                    command_id=command.id,
                    state="processing_on_gateway",
                    dict={
                        "status": "Downloading Staged File from Major Tom for Transmission"
                    }
                ))
                # Download file from Major Tom
                try:
                    self.check_cancelled(id=command.id, gateway=gateway)
                    filename, content = gateway.download_staged_file(
                        gateway_download_path=command.fields["gateway_download_path"])
                except Exception as e:
                    asyncio.ensure_future(gateway.fail_command(command_id=command.id, errors=[
                                          "File failed to download", f"Error: {traceback.format_exc()}"]))

                # Write file locally.
                with open(filename, "wb") as f:
                    f.write(content)

                ser.write(filename) # Again, not sure if this is the right format for the radio yet - need info.

                # Need to add a specific approach to changing the code on the satellite remotely.

                await asyncio.sleep(2)
                self.check_cancelled(id=command.id, gateway=gateway)
                asyncio.ensure_future(gateway.complete_command(
                    command_id=command.id,
                    output=f"File {filename} Successfully Uplinked to Spacecraft"
                ))

            elif command.type == "downlink_file":
                """
                "Downlinks" an image file and uploads it to Major Tom.
                """
                await asyncio.sleep(1)
                self.check_cancelled(id=command.id, gateway=gateway)
                asyncio.ensure_future(gateway.transmit_command_update(
                    command_id=command.id,
                    state="downlinking_from_system",
                    dict={
                        "status": "Downlinking File from Spacecraft"
                    }
                ))
                await asyncio.sleep(3)
                self.check_cancelled(id=command.id, gateway=gateway)

                # Update command in Major Tom
                await asyncio.sleep(2)
                self.check_cancelled(id=command.id, gateway=gateway)
                asyncio.ensure_future(gateway.transmit_command_update(
                    command_id=command.id,
                    state="processing_on_gateway",
                    dict={
                        "status": f'File: "{api_filename}" Downlinked, Validating'
                    }
                ))
                await asyncio.sleep(3)
                self.check_cancelled(id=command.id, gateway=gateway)
                asyncio.ensure_future(gateway.transmit_command_update(
                    command_id=command.id,
                    state="processing_on_gateway",
                    dict={
                        "status": f'"{api_filename}" is Valid, Uploading to Major Tom'
                    }
                ))

                # Upload file to Major Tom with Metadata
                self.check_cancelled(id=command.id, gateway=gateway)
                try:
                    gateway.upload_downlinked_file(
                        filename=image_filename,
                        filepath=image_filename,  # Same as the name since we stored it locally
                        system=self.name,
                        command_id=command.id,
                        content_type=image_r.headers["Content-Type"],
                        metadata=latest_image
                    )
                    await asyncio.sleep(2)
                    self.check_cancelled(id=command.id, gateway=gateway)
                    asyncio.ensure_future(gateway.complete_command(
                        command_id=command.id,
                        output=f'"{image_filename}" successfully downlinked from Spacecraft and uploaded to Major Tom'
                    ))
                except RuntimeError as e:
                    asyncio.ensure_future(gateway.fail_command(command_id=command.id, errors=[
                                          "Downlinked File failed to upload to Major Tom",
                                          f"Error: {traceback.format_exc()}"]))

                # Remove file now that it's uploaded so we don't fill the disk.
                os.remove(image_filename)

        except Exception as e:
            if type(e) == type(CommandCancelledError()):
                asyncio.ensure_future(gateway.cancel_command(command_id=command.id))
            else:
                asyncio.ensure_future(gateway.fail_command(
                    command_id=command.id, errors=[
                        "Command Failed to Execute. Unknown Error Occurred.", f"Error: {traceback.format_exc()}"]))
        self.running_commands.pop(str(command.id))

    async def check_telemetry(self, id, gateway):
        """
        Inputs: id of satellite
                gateway we are talking to
                (All this gets run in the event loop)

        * To do: check to make sure that there are no senarios where read and write block each other.

        Option here to design in the telemetry handling schema -
        e.g. only running this code when the spacecraft is actively broadcasting."""

        packet = ser.readline()
        await SatelliteTelemetry.relay_telemetry(packet, gateway)
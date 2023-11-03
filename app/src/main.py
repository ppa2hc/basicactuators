# Copyright (c) 2022 Robert Bosch GmbH and Microsoft Corporation
#
# This program and the accompanying materials are made available under the
# terms of the Apache License, Version 2.0 which is available at
# https://www.apache.org/licenses/LICENSE-2.0.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#
# SPDX-License-Identifier: Apache-2.0

# flake8: noqa: E501,B950 line too long
import asyncio
import json
import logging
import signal

from vehicle import Vehicle, vehicle  # type: ignore
from velocitas_sdk.util.log import (  # type: ignore
    get_opentelemetry_log_factory,
    get_opentelemetry_log_format,
)
from velocitas_sdk.vdb.reply import DataPointReply
from velocitas_sdk.vehicle_app import VehicleApp

# Configure the VehicleApp logger with the necessary log config and level.
logging.setLogRecordFactory(get_opentelemetry_log_factory())
logging.basicConfig(format=get_opentelemetry_log_format())
logging.getLogger().setLevel("DEBUG")
logger = logging.getLogger(__name__)


class BasicactuatorsApp(VehicleApp):
    """Velocitas App for basicactuators."""

    def __init__(self, vehicle_client: Vehicle):
        super().__init__()
        self.Vehicle = vehicle_client
        self.home = None
        self.stop = None

    async def on_start(self):
        self.home = 0
        self.stop = 0

        await self.Vehicle.Cabin.Seat.Row1.Pos1.Position.set(self.home)
        await self.Vehicle.Cabin.HVAC.Station.Row1.Left.FanSpeed.set(self.stop)
        await self.Vehicle.Cabin.HVAC.Station.Row1.Right.FanSpeed.set(self.stop)
        await self.Vehicle.Body.Lights.IsLowBeamOn.set(False)
        await self.Vehicle.Body.Lights.IsBrakeOn.set(False)
        await self.Vehicle.Body.Lights.IsHazardOn.set(False)

        await asyncio.sleep(1)
        await self.Vehicle.Cabin.HVAC.Station.Row1.Left.FanSpeed.set(100)
        await self.Vehicle.Cabin.HVAC.Station.Row1.Right.FanSpeed.set(100)

        await asyncio.sleep(1)
        await self.Vehicle.Body.Lights.IsBrakeOn.set(True)
        await self.Vehicle.Body.Lights.IsLowBeamOn.set(True)
        await self.Vehicle.Body.Lights.IsHazardOn.set(True)

        await asyncio.sleep(1)
        await self.Vehicle.Cabin.Seat.Row1.Pos1.Position.set(10)


async def main():
    logger.info("Starting BasicactuatorsApp...")
    vehicle_app = BasicactuatorsApp(vehicle)
    await vehicle_app.run()


LOOP = asyncio.get_event_loop()
LOOP.add_signal_handler(signal.SIGTERM, LOOP.stop)
LOOP.run_until_complete(main())

from __future__ import annotations

import json
from os import path
from typing import List

from pydantic import Field

from learninghouse.core.logging import logger
from learninghouse.core.settings import service_settings
from learninghouse.models.base import (
    EnumModel,
    LHBaseModel,
    ListModel,
)


class SensorType(EnumModel):
    NUMERICAL = "numerical"
    CATEGORICAL = "categorical"

    def __init__(self, typed: str):
        # pylint: disable=super-init-not-called
        self._typed: str = typed

    @property
    def typed(self) -> str:
        return self._typed


class SensorConfiguration(LHBaseModel):
    name: str = Field(None, example="azimuth")
    typed: SensorType = Field(None, example=SensorType.NUMERICAL)


class Sensor(SensorConfiguration):
    pass


class Sensors(ListModel):
    root: List[Sensor] = Field(
        None,
        example=[
            {"name": "azimuth", "typed": "numerical"},
            {"name": "elevation", "typed": "numerical"},
            {"name": "rain_gauge", "typed": "numerical"},
            {"name": "pressure", "typed": "numerical"},
            {"name": "pressure_trend_1h", "typed": "categorical"},
            {"name": "temperature_outside", "typed": "numerical"},
            {"name": "temperature_trend_1h", "typed": "categorical"},
            {"name": "light_state", "typed": "categorical"},
        ],
    )

    @classmethod
    def load_config(cls) -> Sensors:
        filename = service_settings().brains_directory / "sensors.json"
        sensors = []

        if path.exists(filename):
            with open(filename, "r", encoding="utf-8") as sensorfile:
                sensors = json.load(sensorfile)
        else:
            logger.warning("No sensors.json found")

        return Sensors(sensors)

    def write_config(self) -> None:
        filename = service_settings().brains_directory / "sensors.json"
        self.write_to_file(filename, indent=4)

    @property
    def numericals(self) -> List[str]:
        return list(
            map(
                lambda x: x.name,
                filter(lambda x: x.typed == SensorType.NUMERICAL, self),
            )
        )

    @property
    def categoricals(self) -> List[str]:
        return list(
            map(
                lambda x: x.name,
                filter(lambda x: x.typed == SensorType.CATEGORICAL, self),
            )
        )


class SensorDeleteResult(LHBaseModel):
    name: str = Field(None, example="azimuth")

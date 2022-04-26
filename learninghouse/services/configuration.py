from os import listdir, path
from os import remove as rm_file
from shutil import rmtree

from learninghouse.api.errors.brain import BrainExists, BrainNoConfiguration
from learninghouse.api.errors.sensor import NoSensor, SensorExists
from learninghouse.core.logging import logger
from learninghouse.core.settings import service_settings
from learninghouse.models.configuration import (
    BrainConfiguration, BrainConfigurations, BrainDeleteResult, BrainFileType,
    Sensor, Sensors, SensorType, SensorDeleteResult, sanitize_configuration_directory,
    sanitize_configuration_filename)


class SensorConfigurationService():
    @staticmethod
    def list_all() -> Sensors:
        return Sensors.load_config()

    @staticmethod
    def get(name: str) -> Sensor:
        try:
            sensortype = Sensors.load_config()[name]
            return Sensor(name=name, typed=sensortype)
        except KeyError as exc:
            raise NoSensor(name) from exc

    @staticmethod
    def create(name: str, typed: SensorType) -> Sensor:
        sensors = Sensors.load_config()
        if name in sensors:
            raise SensorExists(name)

        sensors[name] = typed
        sensors.write_config()

        return Sensor(name=name, typed=typed)

    @staticmethod
    def update(name: str, typed: SensorType) -> Sensor:
        sensors = Sensors.load_config()

        sensors[name] = typed
        sensors.write_config()

        return Sensor(name=name, typed=typed)

    @staticmethod
    def delete(name: str) -> None:
        sensors = Sensors.load_config()
        try:
            del sensors[name]
            sensors.write_config()
            return SensorDeleteResult(name=name)
        except KeyError as exc:
            raise NoSensor(name) from exc


class BrainConfigurationService():
    @staticmethod
    def list_all() -> BrainConfigurations:
        brains = {}
        for directory in listdir(service_settings().brains_directory):
            if BrainConfiguration.json_config_file_exists(directory):
                brains[directory] = BrainConfiguration.from_json_file(
                    directory)

        return BrainConfigurations.parse_obj(brains)

    @staticmethod
    def get(name: str) -> BrainConfiguration:
        try:
            return BrainConfiguration.from_json_file(name)
        except FileNotFoundError as exc:
            raise BrainNoConfiguration(name) from exc

    @staticmethod
    def create(name: str, configuration: BrainConfiguration) -> BrainConfiguration:
        if BrainConfiguration.json_config_file_exists(name):
            raise BrainExists(name)

        configuration.to_json_file(name)

        return configuration

    @staticmethod
    def update(name: str, configuration: BrainConfiguration) -> BrainConfiguration:
        if not BrainConfiguration.json_config_file_exists(name):
            raise BrainNoConfiguration(name)

        configuration.to_json_file(name)

        return configuration

    @staticmethod
    def delete(name: str, filetype: BrainFileType) -> BrainDeleteResult:
        brainpath = sanitize_configuration_directory(name)

        if not path.exists(brainpath):
            raise BrainNoConfiguration(name)

        if BrainFileType.ALL == filetype:
            logger.info(f'Remove whole brain: {name}')
            rmtree(brainpath)
        else:
            filename = sanitize_configuration_filename(name, filetype)
            if not path.exists(filename):
                raise BrainNoConfiguration(name)

            logger.info(f'Remove {filetype.filename} from brain {name}')

            rm_file(filename)

        return BrainDeleteResult(name=name, filetype=filetype)

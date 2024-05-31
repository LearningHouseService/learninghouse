from learninghouse.api.errors.sensor import NoSensor, SensorExists
from learninghouse.models.sensor import (
    Sensor,
    SensorDeleteResult,
    Sensors,
    SensorType,
)


class SensorConfigurationService:
    @staticmethod
    def list_all() -> Sensors:
        return Sensors.load_config()

    @staticmethod
    def get(name: str) -> Sensor:
        sensors = Sensors.load_config()

        for sensor in sensors:  # type: Sensor
            if sensor.name == name:
                return sensor

        raise NoSensor(name)

    @staticmethod
    def create(name: str, typed: SensorType) -> Sensor:
        sensors = Sensors.load_config()

        for sensor in sensors:  # type: Sensor
            if sensor.name == name:
                raise SensorExists(name)

        new_sensor = Sensor(name=name, typed=typed)
        sensors.append(new_sensor)
        sensors.write_config()

        return new_sensor

    @staticmethod
    def update(name: str, typed: SensorType, cycles: int, calc_sun_position: bool) -> Sensor:
        sensors = Sensors.load_config()
        for sensor in sensors:  # type: Sensor
            if sensor.name == name:
                sensor.typed = typed
                sensor.cycles = cycles
                sensor.calc_sun_position = calc_sun_position
                sensors.write_config()
                return sensor

        raise NoSensor(name)

    @staticmethod
    def delete(name: str) -> None:
        sensors = Sensors.load_config()

        for sensor in sensors:  # type: Sensor
            if sensor.name == name:
                sensors.remove(sensor)
                sensors.write_config()
                return SensorDeleteResult(name=name)

        raise NoSensor(name)

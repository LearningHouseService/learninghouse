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
        from learninghouse.api.errors.sensor import NoSensor

        sensors = Sensors.load_config()

        for sensor in sensors.root:
            if sensor.name == name:
                return sensor

        raise NoSensor(name)

    @staticmethod
    def create(name: str, typed: SensorType) -> Sensor:
        from learninghouse.api.errors.sensor import SensorExists

        sensors = Sensors.load_config()

        for sensor in sensors.root:
            if sensor.name == name:
                raise SensorExists(name)

        new_sensor = Sensor(name=name, typed=typed)
        sensors.append(new_sensor)
        sensors.write_config()

        return new_sensor

    @staticmethod
    def update(
        name: str, typed: SensorType, cycles: int, calc_sun_position: bool
    ) -> Sensor:
        from learninghouse.api.errors.sensor import NoSensor

        sensors = Sensors.load_config()
        for sensor in sensors.root:
            if sensor.name == name:
                sensor.typed = typed
                sensor.cycles = cycles
                sensor.calc_sun_position = calc_sun_position
                sensors.write_config()
                return sensor

        raise NoSensor(name)

    @staticmethod
    def delete(name: str) -> SensorDeleteResult:
        from learninghouse.api.errors.sensor import NoSensor

        sensors = Sensors.load_config()

        for sensor in sensors.root:
            if sensor.name == name:
                sensors.remove(sensor)
                sensors.write_config()
                return SensorDeleteResult(name=name)

        raise NoSensor(name)

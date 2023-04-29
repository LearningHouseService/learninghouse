import json

with open("./sensors.json", "r+", encoding="utf-8") as file:
    sensors_old = json.load(file)
    sensors_new = []

    for name, typed in sensors_old.items():
        sensors_new.append({"name": name, "typed": typed})

    file.seek(0)
    json.dump(sensors_new, file, indent=4)
    file.truncate()

import csv
from datetime import datetime
from dateutil import tz

from_zone = tz.tzutc()
to_zone = tz.tzlocal()

with open('./training_data.csv', 'r', encoding='utf-8') as csvfile:
    with open('./training_data_new.csv', 'w', encoding='utf-8') as csvfile2:
        reader = csv.DictReader(csvfile)
        writer = csv.DictWriter(csvfile2, fieldnames=reader.fieldnames)
        writer.writeheader()

        for row in reader:
            if row['timestamp']:
                utc = datetime.fromtimestamp(float(row['timestamp']))
                utc = utc.replace(tzinfo=from_zone)
                date = utc.astimezone(to_zone)

                print(f'{utc}=>{date}')

                row['timestamp'] = date.timestamp()
                row['datetime'] = date.strftime('%Y-%m-%d %H:%M:%s')
                row['month_of_year'] = date.month
                row['day_of_month'] = date.day
                row['day_of_week'] = date.strftime('%A')
                row['hour_of_day'] = date.hour
                row['minute_of_hour'] = date.minute

            writer.writerow(row)

import csv


class HiveData:
    def __init__(self, filename, database, user):
        self.filename = filename
        self.db = database
        self.user = user

    def post_data(self):
        with open(self.filename, newline='\n') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='"')
            json_array = []
            for row in reader:
                json_array.append(
                    {
                        "measurement": "hivedata",
                        "tags": {
                            "hive_id": row[0], "user": self.user
                        },
                        "time": row[1],
                        "fields": {
                            "probe_type": row[2], "outdoor": row[3],
                            "temperature": float(row[4]),
                            "humidity": float(row[5])
                        }
                    })
        self.db.write_points(json_array)

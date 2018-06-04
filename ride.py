import json

class Ride:

    def __init__(self, row):
        # Divvy data columns:
        #
        # trip_id: ID attached to each trip taken
        # start_time: day and time trip started, in CST
        # stop_time: day and time trip ended, in CST
        # bikeid: ID attached to each bike
        # tripduration: time of trip in seconds 
        # from_station_name: name of station where trip originated
        # to_station_name: name of station where trip terminated 
        # from_station_id: ID of station where trip originated
        # to_station_id: ID of station where trip terminated
        # usertype: "Customer" is a rider who purchased a 24-Hour Pass; "Subscriber" is a rider who purchased an Annual Membership
        # gender: gender of rider 
        # birthyear: birth year of rider
        # "trip_id","start_time","end_time","bikeid","tripduration","from_station_id","from_station_name","to_station_id","to_station_name","usertype","gender","birthyear"
        self.trip_id = int(row[0])
        self.start_time = row[1]
        self.stop_time = row[2]
        self.bikeid = int(row[3])
        self.tripduration = int(row[4])
        self.from_station_id = int(row[5])
        self.from_station_name = row[6]
        self.to_station_id = int(row[7])
        self.to_station_name = row[8]
        self.usertype = row[9]
        self.gender = row[10]

        if len(row[11]) > 0:
            self.birthyear = int(row[11])
        else:
            self.birthyear = None

    
    def __repr__(self):
        return json.dumps(self, default=lambda x: x.__dict__)
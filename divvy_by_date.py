# based very heavily on Hannah Davis' workshop at Eyeo 2018 (https://github.com/handav/workshop)
import csv
import midiutil
import numpy
from scipy import stats
from datetime import datetime

from ride import Ride

month_lengths = [0, 31, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335]

# FILE VARIABLES
csv_input = '../data/Divvy_Trips_2017_Q3Q4/Divvy_Trips_2017_Q3.csv'
# csv_input = '../data/Divvy_Trips_2017_Q3Q4/test.csv'
# csv_input = '../data/Divvy_Trips_2017_Q3Q4/q3_small.csv'
midi_output = './midi_folder/divvy_by_date.mid'

stations_csv = '../data/Divvy_Bicycle_Stations_-_All_-_Map.csv'
stations = []

# TIME VARIABLES
start_month = 7
start_day = 1
start_hour = 0
subtract_beat = month_lengths[(start_month-1)] + start_day + start_hour
sightings = {}
past_day = 0

def get_duration(val, duration_stats):
    possible_beats = [0.25, 0.5, 1, 2]
    if val <= duration_stats['mean']/2:
        duration = possible_beats[0]
    if val > duration_stats['mean']/2 and val <= duration_stats['mean']:
        duration = possible_beats[1]
    if val > duration_stats['mean'] and val <= duration_stats['mean'] + duration_stats['mean']/2:
        duration = possible_beats[2]
    if val > duration_stats['mean'] + duration_stats['mean']/2:
        duration = possible_beats[3]
    return duration

def get_latitude(address):
    if address in stations:
        return stations[address]
    return 0

def get_note(station_name, station_stats):
    base_octave_major = [60, 62, 64, 65, 67, 69, 71]
    major_scale = base_octave_major + [note + 12 for note in base_octave_major] + [note + 24 for note in base_octave_major]
    minor_scale = [60, 62, 63, 65, 67, 68, 70]
    scale = major_scale
    print(scale)
    latitude = get_latitude(station_name)
    for note_index in range(station_stats['divisions']):
        low_bound = station_stats['percentiles'][0] + note_index * station_stats['step']
        high_bound = low_bound + station_stats['step']
        if low_bound <= latitude <= high_bound:
            print(low_bound, latitude, high_bound, note_index)
            print(major_scale[note_index])
            return major_scale[note_index]
    print('not found - 60')
    return major_scale[0]

def save_midi(midi_file):
    filename = midi_output
    with open(filename, 'wb') as output_file:
        midi_file.writeFile(output_file)
        print('midi file saved')

def check_for_voice(description):
    if 'talk' in description or 'voice' in description or 'said' in description or 'say' in description:
        return True
    else:
        return False

def parse_date(date):
    info = date.split(' ')[0].split('/')
    month = int(info[0])
    day = int(info[1])
    
    time_sections = date.split(" ")[1].split(":")
    hour = int(time_sections[0])
    
    beat = (month_lengths[(month-1)] + day + hour) - subtract_beat
    return [day, month, hour, beat]

def get_stats(rides, property):
    val_list = []
    for ride in rides:
        value = getattr(ride, property)
        val_list.append(value)
        # if not '.' in value:
        #     val_list.append(int(value))
        # else:
        #     val_list.append(round(float(value)))
    stdev = numpy.std(val_list)
    mean = numpy.mean(val_list)
    median = numpy.median(val_list)
    mode = stats.mode(val_list)
    return {
        "mean": mean, 
        "median": median, 
        "mode": mode[0],
        "stdev": stdev
    }

def get_lat_stats(stations):
    values = list(stations.values())
    
    divisions = 21
    percentile_step = 100 / divisions
    percentiles = numpy.percentile(values, [i*percentile_step for i in range(divisions)])

    return {
        'divisions': divisions,
        'step': (percentiles[-1] - percentiles[0])/float(divisions),
        'percentiles': percentiles
    }

def compose_midi(rides, duration_stats, station_stats):
    track = 0
    channel = 0
    time = 0 # in beats
    tempo = 200  # beats per minute
    volume = 100 # from 0-127
    program = 0 # Midi instrument
    midi_file = midiutil.MIDIFile(1, deinterleave=False, adjust_origin=False)
    midi_file.addTempo(track, time, tempo)
    midi_file.addProgramChange(track, channel, time, program)
    midi_file.addProgramChange(track, channel+1, time, 112)
    for ride in rides:
        time = parse_date(ride.start_time)[3]
        if time >= 0:
            duration = get_duration(ride.tripduration, duration_stats) # duration is in beats
            note = get_note(ride.to_station_name, station_stats)
            midi_file.addNote(track, channel, note, time, duration, volume) 
            if ride.usertype == "Customer":
                midi_file.addNote(track, channel+1, note, time, 2, volume)
            else:
                midi_file.addNote(track, channel, note, time, duration, volume)        
    save_midi(midi_file)

def clean_date(date):
    formatted_date = date.split(' ')[0].split('/')
    if len(formatted_date[0]) == 1:
        formatted_date[0] = '0' + formatted_date[0]
    if len(formatted_date[1]) == 1:
        formatted_date[1] = '0' + formatted_date[1]
    formatted_date = '/'.join(formatted_date)
    return formatted_date

def clean_data(rides):
    data = sorted(rides, key = lambda ride: datetime.strptime(clean_date(ride.start_time), "%m/%d/%Y"))
    return data

def get_stations(stations_csv):
    stations = {}
    with open(stations_csv, 'rt') as csvfile:
        reader = csv.reader(csvfile, quotechar='"')
        skip = True
        for row in reader:
            if skip:
                skip = False
                continue
                
            stations[row[1]] = float(row[6])

    return stations


with open(csv_input, 'rt') as csvfile:

    stations = get_stations(stations_csv)
    station_stats = get_lat_stats(stations)
    print(station_stats)

    reader = csv.reader(csvfile, quotechar='"')
    all_rides = []
    skip = True
    for row in reader:
        if skip:
            skip = False
            continue
            
        all_rides.append(Ride(row))
    all_rides = clean_data(all_rides)
    duration_stats = get_stats(all_rides, 'tripduration')
    print(duration_stats)
    compose_midi(all_rides, duration_stats, station_stats)

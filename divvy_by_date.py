# based very heavily on Hannah Davis' workshop at Eyeo 2018 (https://github.com/handav/workshop)
import csv
import midiutil
import numpy
from scipy import stats
from datetime import datetime

from ride import Ride

month_lengths = [0, 31, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335]

# FILE VARIABLES
# csv_input = '../data/Divvy_Trips_2017_Q3Q4/Divvy_Trips_2017_Q3.csv'
csv_input = '../data/Divvy_Trips_2017_Q3Q4/test.csv'
# csv_input = '../data/Divvy_Trips_2017_Q3Q4/q3_small.csv'
midi_output = './midi_folder/divvy_by_date.mid'

# TIME VARIABLES
start_month = 9
start_day = 30
subtract_beat = month_lengths[(start_month-1)] + start_day 
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

def get_note(val):
    major_scale = [60, 62, 64, 65, 67, 69, 71]
    minor_scale = [60, 62, 63, 65, 67, 68, 70]
    scale = major_scale

    # TODO: make this based on geography in some way?
    return major_scale[val % 7]

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
    beat = (month_lengths[(month-1)] + day) - subtract_beat
    return [day, month, beat]

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

def compose_midi(rides, duration_stats):
    track = 0
    channel = 0
    time = 0 # in beats
    tempo = 200  # beats per minute
    volume = 100 # from 0-127
    program = 0 # Midi instrument
    midi_file = midiutil.MIDIFile(1, deinterleave=False, adjust_origin=False)
    midi_file.addTempo(track, time, tempo)
    midi_file.addProgramChange(track, channel, time, program)
    midi_file.addProgramChange(track, channel+1, time, 52)
    for ride in rides:
        time = parse_date(ride.start_time)[2]
        if time >= 0:
            duration = get_duration(ride.tripduration, duration_stats) # duration is in beats
            note = get_note(int(ride.from_station_id))
            midi_file.addNote(track, channel, note, time, duration, volume) 
            # if check_for_voice(row[7]) == True:
            #     midi_file.addNote(track, channel+1, note, time, 2, volume)
            # else:
            #     midi_file.addNote(track, channel, note, time, duration, volume)        
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

with open(csv_input, 'rt') as csvfile:
    reader = csv.reader(csvfile, quotechar='"')
    all_rides = []
    skip = True
    for row in reader:
        if skip:
            skip = False
            continue
            
        all_rides.append(Ride(row))
    # print(all_rides)
    all_rides = clean_data(all_rides)
    print(repr(all_rides))
    duration_stats = get_stats(all_rides, 'tripduration')
    print(duration_stats)
    compose_midi(all_rides, duration_stats)

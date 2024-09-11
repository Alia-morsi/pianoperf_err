import sys
import os
import mido
from mido import MidiFile, MidiTrack, Message #ditching midi for this absolute time thing
import pretty_midi
from pretty_midi import Note

# Define a function to convert the input text file to a list of dictionaries
#it's easier to get the wrong pitch and the extra note info from the match file

def process_match_file(filename):
    keys = [ 'id', 'onset time', 'offset time', 'spelled pitch', 'onset velocity',
    'offset velocity', 'channel', 'match status', 'score time', 'note ID', 'error index', 'skip index']

    with open(filename, 'r') as file:
        #skip the first 4 lines
        file.readline()
        file.readline()
        file.readline()
        file.readline()

        data = []
        for line in file:
            if line.startswith('//'):
                continue #since we'll get the missing note info from the corresp file anyway
            values = line.strip().split('\t')
            record = {}

            for i in range(len(keys)):
                key = keys[i].lower()
                value = values[i]    
                record[key] = value 
            data.append(record)

        return data

#but, it's easier to get the missing note info from the corresp file.
def process_corresp_file(filename):
    #turn the corresp files into key-value pairs
    data = []
    with open(filename, 'r') as file:
        # Read the header line to get the column names
        header = file.readline().strip().split(' ')
        header = header[1:]

        for line in file:

            values = line.strip().split('\t')
            record = {}

            for i in range(len(header)):
                key = header[i].lower()  # Convert keys to lowercase
                value = values[i]

                # Handle special cases for numerical values
                if key.endswith('time') or key.endswith('vel') or key.endswith('ID') or key.endswith('Pitch'):
                    if value == '*':
                        value = -1
                    value = float(value)

                record[key] = value
            data.append(record)

    return data

def adapting_corresp_and_match(corresp_filename, match_filename):
    #check if the file exists
    if not os.path.exists(corresp_filename):
        print(f"File '{corresp_filename}' does not exist.")
        sys.exit(1)

    if not os.path.exists(match_filename):
        print(f"File '{match_filename}' does not exist.")
        sys.exit(1)

    corresp_result = process_corresp_file(corresp_filename)
    match_result = process_match_file(match_filename)

    # Convert into midi files that have annotations on note 0 where a * is reported
    # extra note: when align has a note not in ref
    # missing note: when ref has a note not in align

    #midi_file = MidiFile()
    #track = MidiTrack()

    midi_wrongpitch = pretty_midi.PrettyMIDI()
    midi_extranote = pretty_midi.PrettyMIDI()

    piano_wrongpitch = pretty_midi.Instrument(program=0)
    piano_extranote = pretty_midi.Instrument(program=0)
    piano_missingnote = pretty_midi.Instrument(program=0)
    
    #for i, record in enumerate(match_result):

    #at the end I should check if the number of notes used is the same as the mismatches..
    #get wrong pitches or extra notes
    for i, record in enumerate(corresp_result):
        start_time = float(record['onset time'])
        end_time = time=float(record['offset time'])

        if record['error index'] == '1': #wrong pitch
            #add midi note 1
            note1 = Note(velocity=64, pitch=1, start=start_time, end=end_time)  # Absolute start time: 0 seconds
            piano_wrongpitch.notes.append(note1)

        if record['error index'] == '3': #extra note
            note1 = Note(velocity=64, pitch=3, start=start_time, end=end_time)  # Absolute start time: 2 seconds
            piano_extranote.notes.append(note1)
            
    path_prefix = os.path.split(corresp_filename)[0]

    #midi_file.tracks.append(track)
    midi_wrongpitch.instruments.append(piano_wrongpitch)
    midi_wrongpitch.write(os.path.join(path_prefix, "wrong_pitches.mid"))

    midi_extranote.instruments.append(piano_extranote)
    midi_extranote.write(os.path.join(path_prefix, "extra_notes.mid"))


    #get missing notes (here we just add a default of 0.5 second)
    #for i, record in iter(corresp_result):
    #    if record['alignid'] == '*':
    #        track.append(Message('note_on', note=1, velocity=64, time=1000*float(record[''])))

    #    elif record.alignid == '*':
            #missing note
    #        status = 'missing'
    
        #label start edge cases
        # since notes can be played in parallel.. this whole next note
        # might not make sense to retrieve the end: since the next note might
        # have an end time that is shorter than what we are looking for.
        # an extra note in the align: we can just read the start and end of this id
        # a missing note in the align: we can get the corresponding id start and end in the ref.
        # Solutions: just have a rule of thumb where we start at the end of the previous note
        # (we can get the id of it )

    # Print the first two records as an example

    
if __name__ == '__main__':
# Check if a command-line argument (filename) is provided
    if len(sys.argv) != 3:
        print("Usage: python script.py <corresp> <match>")
        sys.exit(1)

    # Get the filename from the command-line argument
    corresp_filename = sys.argv[1]
    match_filename = sys.argv[2]
    
    adapting_corresp_and_match(corresp_filename, match_filename)

    

import glob
import pretty_midi
import os

def clean_miditrack(infile, outfile):
    midi_data = pretty_midi.PrettyMIDI(os.path.abspath(infile))

    if len(midi_data.instruments) >= 2:
        del midi_data.instruments[1]
        print("Second track removed.")

    midi_data.write(outfile)


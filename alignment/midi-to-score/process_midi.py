import os
import shutil
import subprocess
import glob

def main(input_folder, output_folder, running_folder):
    # Find a MIDI file in the input folder
    midi_files = glob.glob(os.path.join(input_folder, '*.mid'))
    if not midi_files:
        print("No MIDI file found in the input folder")
        return

    score_midifile = 'Chopin_-_Ballade_no._1_in_G_minor_Op._23'
    os.mkdir(output_folder)

    for midi_file in midi_files:
        # Copy the MIDI file to the running folder
        shutil.copy(midi_file, running_folder)
        midi_filename = os.path.basename(midi_file)
        running_midi_file = os.path.join(running_folder, midi_filename)

        # Run the MIDItoMIDIalign.sh script
        script_path = os.path.join(running_folder, 'MIDItoMIDIalign.sh')
        subprocess.run([script_path, score_midifile, os.path.splitext(midi_filename)[0]], check=True)

        # Define the suffixes of the files to be copied
        suffixes = ['match.txt', 'spr.txt', 'corresp.txt']

        # Copy the files with the specified suffixes to the output folder
        for suffix in suffixes:
            matching_files = glob.glob(os.path.join(running_folder, f'*{suffix}'))
            for file in matching_files:
                shutil.copy(file, os.path.join(output_folder, os.path.split(file)[1]))
                os.remove(file)

    #remove the intermediary files that are in the running folder.
    suffixes = ['_fmt3x.txt', '_hmm.txt']
    for suffix in suffixes:
        os.remove('{}{}'.format(score_midifile, suffix))
 
if __name__ == "__main__":
    import sys
    if len(sys.argv) != 4:
        print("Usage: python script.py <input_folder> <output_folder> <running_folder>")
    else:
        input_folder = sys.argv[1]
        output_folder = sys.argv[2]
        running_folder = sys.argv[3]
        main(input_folder, output_folder, running_folder)

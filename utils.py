#code to generate the imshows.
#copy from synmist.
import numpy as np
import glob
import os
import pretty_midi as pm
from scipy.io.wavfile import write #i recall there being another more common library for just writing the audio file...
import matplotlib.pyplot as plt

#synthesize_midi('eval-data/**/*.mid', 'eval-data-synth')
def synthesize_midi(glob_string, output_folder):
    #glob string must end in midi
    print('BE MINDFUL OF THE SPACE available on your device and the number of midi files youd like to synthesize')
    if glob_string[-3:] != 'mid' and glob_string[-4:] != 'midi':
        print('only applicable to midi files. exiting synth function')
        return
    basedir = os.getcwd()
    #if the given file does not have a wav counterpart, synthesize it
    midi_files = glob.glob(glob_string, recursive=True)
    for f in midi_files:
        #get their rel paths, and 
        rel_path = os.path.relpath(f, basedir)
        new_basepath = os.path.join(output_folder, os.path.dirname(rel_path))
        name, ext = os.path.splitext(os.path.basename(f))
        os.makedirs(new_basepath, exist_ok=True)
        if os.path.join(new_basepath, f"{name}.'wav'") not in output_folder:
            midi_data = pm.PrettyMIDI(f)
            audio_data = midi_data.fluidsynth(fs=44100)
            write(os.path.join(new_basepath, f"{name}.wav"), 44100, audio_data)
    

#This is a utility function to chop my piano roll
def get_piano_roll(midi_file, start_time, end_time):
    pr = np.zeros((128, int((end_time - start_time) * 100)))
    for instrument in pm.PrettyMIDI(midi_file).instruments:
        for note in instrument.notes:
            if note.start >= end_time or note.end <= start_time:
                continue
            start = int((note.start - start_time) * 100)
            end = int((note.end - start_time) * 100)
            pr[note.pitch, start:end] = 1
    return pr

def bulk_run(processing_dict, output_folder, glob_strings=['eval-data/**/*.mid']):
    #be sure to match the processor with a suitable globstring in terms of extension.
    #recording_fullpaths = [os.path.join(base_path, pianodiary_path, recording) for recording in recordings]
    recording_fullpaths = []
    for glob_string in glob_strings:
        recording_fullpaths.extend(glob.glob(glob_string, recursive=True))                            
    beat_preds = []
    
    #for saving:
    #output_folder/<label>/<relpath>/<filename>
    for recording in recording_fullpaths:
        for label, processing_obj in processing_dict.items():
            beat_preds.append(processing_obj.process(recording))
            for beat_pred, recording in zip(beat_preds, recording_fullpaths):
                name, ext = os.path.splitext(os.path.basename(recording))
                #relpath without filename
                relpath = os.path.dirname(os.path.relpath(recording, os.getcwd()))
                new_basepath = os.path.join(output_folder, label, relpath)
                os.makedirs(new_basepath, exist_ok=True)
                beat_pred.tofile(os.path.join(new_basepath, f"{name}.csv"), sep='\n')
    return recording_fullpaths, beat_preds


#displays a segment of beat trackings results from a given file. If target is not known pass an empty array
def display(midi_recording, beats_pred, beats_targ, start_time, end_time):
    midi_data = pm.PrettyMIDI(midi_recording)
    beats_targ = midi_data.get_beats()

    beats_pred_seg = beats_pred[np.logical_and(beats_pred >= start_time, beats_pred <= end_time)]
    beats_targ_seg = beats_targ[np.logical_and(beats_targ >= start_time, beats_targ <= end_time)]
    pr_seg = get_piano_roll(midi_recording, start_time, end_time)

    plt.figure(figsize=(20, 5))
    plt.imshow(pr_seg, aspect='auto', origin='lower', cmap='gray')
    for b in beats_pred_seg:
        plt.axvline(x=(b - start_time) * 100, ymin=0.5, ymax=1, color='g')
    for b in beats_targ_seg:
        plt.axvline(x=(b - start_time) * 100, ymin=0, ymax=0.5, color='r')
    plt.title('Green for predicted beats, Red for ground truth beats.')
    plt.show()
    
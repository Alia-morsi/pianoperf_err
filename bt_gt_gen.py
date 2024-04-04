import os, sys, pathlib
import pretty_midi
import partitura as pt
import numpy as np
from BeatNet.BeatNet import BeatNet
import utils
sys.path.append('/Users/aliamorsi/Documents/synthetic-mistake-study/piano-synmist')

def prepare_beat_tracking_gts(input_folder, output_folder):
    #convert xml scores into midi 
    #synthesize midi (be mindful of the space)

    #get the beat tracking results from a bulk run for 
        #all the midi scores with pdprep and pretty midi
        #all the audio with beatnet
    
    return

def process_for_file(midi_score, xml_score, rendered_clean_performance_midi, rendered_perf_w_mistakes, mistake_timemap):
    #dtw between score (which will be synthesized) and clean_midi_performance
    fs = 44100
    pm_score = pretty_midi.PrettyMIDI(midi_score) 
    score_synth = pm_score.fluidsynth(fs=fs)

    pretty_midi_beat_predictions = pm_score.get_beats() #not so bad.. beatnet is less deadpan tho.
    pretty_midi_beat_predictions.tofile('pm_score.csv', sep='\n')
    #will omit the partitura equivalent for now.
    #score_part = pt.load_musicxml(xml_score)
    #score_note_array = score_part.note_array()
  
    #beatnet_beat_predictions 
    processor = BeatNet(1, mode='offline', inference_model='DBN', plot=[], thread=False)
    beatnet_beat_predictions = processor.process(score_synth)

    beatnet_beat_predictions[:, 0].tofile('beatnet_test_score.csv', sep='\n')
    #just run it and see the format of each to save accordingly.
    
    #chroma_wp, D, path = utils.align_chroma(midi_score, rendered_clean_performance_midi, fs=fs)
    #cqt_wp = align_prettymidi(midi_score, rendered_clean_performance_midi, fs=fs, perf_synth=os.path.splitext(rendered_clean_performance_midi)[0])
    
    #Get the warping timemap. i think score is the first col and the perf is the second
    #interpolated_beat_predictions = np.interp(beatnet_beat_predictions[:, 0], chroma_wp[:, 0], chroma_wp[:, 1])
    import pdb
    pdb.set_trace()

    return 
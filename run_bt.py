import os
import sys 
import mir_eval

import numpy as np
import glob
import matplotlib.pyplot as plt
import pathlib
from BeatNet.BeatNet import BeatNet

#replace with abspath of pm2s module
sys.path.append(os.path.abspath('../pdprep/pm2s/PM2S'))
from pm2s.features.beat import RNNJointBeatProcessor

#Multi file processing
#processor = RNNJointBeatProcessor(basepath='/Users/aliamorsi/Documents/Yamaha-Colab/pm2s/')

#Single file processing
#midi_score_path = '/Users/aliamorsi/Documents/Yamaha-Colab/musescore_scores/Chopin_-_Nocturne_Op_9_No_2_E_Flat_Major.mid'
#score_beat_pred = processor.process(midi_score_path)
#score_beat_pred.tofile(os.path.join(outfolder, f"{os.path.basename(midi_score_path)[:-4]}"), sep='\n')


estimator = BeatNet(1, mode='offline', inference_model='DBN', plot=[], thread=False)
output_folder = 'bt_results/BeatNet'
recording_fullpaths, beat_preds = bulk_run({'bnet': estimator}, output_folder, glob_strings=['eval-data-synth/**/*.wav'])

# folder with args: infolder, infile.
#copy from synmist
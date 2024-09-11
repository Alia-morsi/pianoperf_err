import pretty_midi
import mido
import os
import argparse
import copy
import pylcs
import numpy as np
import sys
import pandas as pd

#mostly for comparison so far
import partitura
import parangonar

#ifdef
DEBUG=True

#constants
ALIGNED = 0
MISSING = 1
EXTRA = 2

PERF = 0
SCORE = 1

#constant vars
thrsh = 100 #the ms difference at which we would consider lack of ordering insignificant
#this threshold should be defined based on common bpms and expected time divisions.
BEAT_THRESH = 100 

def main():
    #calculate the diff structure
    return diff

def group_time(timeline, thrsh_ms):
    #function groups onsets occurring within thrsh ms from the first onset of that 'group'
    #return (grouped time, noteobj)
    if len(timeline) == 0:
        return
    i = 0
    qt_timeline = []
    while(i < len(timeline)):
        time, noteobj = timeline[i]
        if i==0: #if the group is starting
            group = []
            group_start = time
            
        else:
            if (time - group_start)*100 >= thrsh_ms: #terminate group, start another
                qt_timeline.extend(group) #group has up to the last iter
                group = []
                group_start = time                
        
        #loop termination
        group.append((time, noteobj))
        i += 1  

    #conclude the last group. group will always have an element if i>0.
    #edit: but since we are no longer adding
    qt_timeline.extend(group)
    return qt_timeline

class C2P():
    'utility class that maps one-to-one between pitches and characters, to allow us to use pylcs'
    'midi is just from 0 - 127 anyway'
    'pitch is input and output as MIDI note numbers'
    'was built into a class in case we will maintain a data structure..'
    '33 is just an arbitrary number to skip some special characters in ascii.'
    
    def __init__(self):
        #build the map
        self.ofst = lambda x: x+33
        self.rev_ofst = lambda x: x-33
        return
    def char2pitch(self, char):
        return self.rev_ofst(ord(char))
    
    def pitch2char(self, pitch):
        return chr(self.ofst(pitch))
    
#TODO: Make TL a base class, and Score TL / Performance TL their subclasses. score TL has 
# self.tl_beats as an addition, which links each tl item to the nearest beat.
#TODO: check the types of all arrays. intention is to always use np for nicer operations
#TODO: check that all the time units are in ms.
class TL(): #TODO: maybe timeline should be what holds snippets in the first place.
    'class to facilitate procesing of timelines, since we will have to order them differently during processing'
    'TODO: if beattimes is per snippet or per whole perf. For now assume snippet'
    def __init__(self, timeline, type=PERF, beattimes=[], beattimes_start=-1, thrsh_ms=100):
        #create a list of tuples, pitch num (converted as per C2P)
        #currently, the type, whether PERF or score, is not really used.. it was needed for the beattimes array
        #but now not anymore..
        if any(beattimes):
            if not isinstance(beattimes, np.ndarray):
                raise TypeError('beattimes must be an numpy ndarray')
        
        self.c2p = C2P()
        self.timeline = timeline
        self.starttime = timeline[0][0]
        self.endtime = timeline[-1][0]

        if len(beattimes) > 0:
            #TODO: check that they indeed match the score     
            if beattimes_start == -1:
                beattimes[:] += self.starttime
            else: #if we are sure that the beattimes fragment start is exactly that as the score fragment
                beattimes[:] += beattimes_start

            #get the earlier beat time nearest to each score onset,tl beats is parallel to timeline
            self.tl_beats = np.zeros(len(self.timeline))
            for i, (onset, noteobj) in enumerate(timeline):
                x = onset-beattimes
                nearest_beattime_i = np.piecewise(x, [x >= 0, x < 0], [lambda x: x, sys.maxsize]).argmin()
                self.tl_beats[i] = beattimes[nearest_beattime_i]

        #quantize according to thrsh. should not affect our nearest beattime calc. 
        self.qt_timeline = group_time(timeline, thrsh_ms)
        #create map:
        _map = []
        for time, noteobj in self.qt_timeline:
            if not noteobj.pitch: #temp fix to skip Control Change objects.
                continue
            _map.append((self.c2p.pitch2char(noteobj.pitch), noteobj))
        self.map = _map #no need for any sorting, since the timeline itself is already sorted by time, and qt_timeline doesn't change its order
            
        #self.map = sorted([(self.c2p.pitch2char(noteobj.pitch), noteobj) for time, noteobj in self.qt_timeline], key=lambda x: x[0])
        self.charseq = "".join([str(i) for i, noteobj in self.map])
        return
    
    def get_char_seq(self):
        return self.charseq

    def __str__(self):
        #print each row as a tuple of the pitch (note-octave), followed by the timeline element
        return str([('%s'%self.c2p.char2pitch(char), '%s'%noteobj) for char, noteobj in self.map])
        
class diff(): #todavia no lo tengo claro..
    def __init__():
        return
    
    def normalize():
        return
    
#this is a short function where we warp the score according to what we believe could be the player's
#intent. But currently it's just linear time scaling.
    
def intent_warp():
    return 

def apply_patch_partial(src_snipt_obj, patch):
    #this applies the patch partially in the areas where the beat displacement is defined. 
    return

def predict_perf_beattimes(nb_src, pre_alignedn_src, pre_alignedn_tgt, n_src, n_tgt):
    #nearest_beat_src: nb_src
    #aligned_note_before_nearest_beat_src: pre_alignedn_src
    #aligned_note_before_nearest_beat_tgt: pre_alignedn_tgt
    #noting that pre_alignedn_src must come before nb_src temporally.
    #source_note: n_src
    #target_note: n_tgt
    return n_tgt - ((n_src - nb_src)*(n_tgt - pre_alignedn_tgt)/(n_src-pre_alignedn_src))

def align_partitura(src_snipt_obj, tgt_snipt_obj):
    allnoteobjs = [] #construct array with same format, but using partitura instead of my approach
    return allnoteobjs

def diff_ms(src_snipt_obj, tgt_snipt_obj):
    if len(src_snipt_obj.timeline) == 0 or len(tgt_snipt_obj.timeline) == 0:
        print('cannot msdiff on empty timelines')
        return
    
    #and, check the format, so that the accesses below do not cause an exception
    src_offset = src_snipt_obj.timeline[0][0]
    tgt_offset = src_snipt_obj.timeline[0][0]

    src_i = 0
    tgt_i = 0

    #nice explanation: https://www.programiz.com/dsa/longest-common-subsequence
    # https://pypi.org/project/pylcs/
    #get the longest common subsequence, ignoring order differences under thresh ms

    #quantize and sort timelines
    src_tlobj = TL(src_snipt_obj.timeline, type=SCORE, beattimes=src_snipt_obj.beattimes, beattimes_start=0)
    tgt_tlobj = TL(tgt_snipt_obj.timeline, type=PERF)

    if DEBUG:
        print('src charseq: {}'.format(src_tlobj.charseq))
        print('tgt charseq: {}'.format(tgt_tlobj.charseq))

    #align from target onto source. lcseq will have the same length as target, and assumptions
    #on the return value based on this ordering will carry fwd till the end of the function.
    lcseq = pylcs.lcs_sequence_idx(tgt_tlobj.get_char_seq(), src_tlobj.get_char_seq())
    #to print the lcseq in terms of the target string
    #print('\n')
    #print(''.join([src_tlobj.charseq[i] if i != -1 else ' ' for i in lcseq]))

    #construct the events that happen in sequence.
    #make a list of:
    #[(type, (src_note, src_tl_i), (target_note, tgt_tl_i)]. 
    #where type indicates if it's a missing note (1), extra note (2), or none (0)
    #none means that both occur. Each list element will always have a tuple of 3.
    #in case a note doesn't exist from the source or the target, None will be placed instead.
    src_ctr = 0         #I think the indexes are from 0. 
    all_noteobjs = []
    tgt_tl_beats = np.full(len(tgt_snipt_obj.timeline), -1.0) #Predicted performance beattimes only for the aligned portions

    for tgt_ctr, res in enumerate(lcseq):
        while(res > src_ctr): #some notes in source missing, put them all.
            all_noteobjs.append((MISSING, (src_tlobj.qt_timeline[src_ctr][1], src_ctr), None)) #to get the note obj only. 
            src_ctr += 1

        #afaik, res should never be less than src_ctr unless it's -1
        if res == -1:
            all_noteobjs.append((EXTRA, None, (tgt_tlobj.qt_timeline[tgt_ctr][1], tgt_ctr)))
        
        elif src_ctr < len(src_tlobj.qt_timeline): #here, res should == src_ctr, unless src_ctr is out of range
            src_noteobj = src_tlobj.qt_timeline[src_ctr][1]
            tgt_noteobj = tgt_tlobj.qt_timeline[tgt_ctr][1]
            all_noteobjs.append((ALIGNED, (src_noteobj, src_ctr), (tgt_noteobj, tgt_ctr)))

            #if the source note is on its nearest beat within thresh, consider it on the beat
            #Which might not be the case because the note was played a bit later than it should have beatwise.
            #But this is actually a big question for such cases: where is the beat when there are temporal mistakes
            #In hindsight this makes no sense because if it's not exactly on the beat in the src, then it's not
            #Only the performance should be afforded this 'beat threshold' thing.
            #if abs(nb_src - src_noteobj.start)*1000.0 <= BEAT_THRESH:              
            src_ctr += 1

    #interm_patch = construct_patch(all_noteobjs, src_tlobj.tl_beats, tgt_tl_beats)
    return all_noteobjs 



def construct_patch(all_noteobjs, src_tl_beats, tgt_tl_beats):
    #the tlbeats array give the nearest prior beat given any timeline index. 
    #the nearest prior beat is defined for each src_tl_beats, but for the tgt_tl_beats it depends..

    #status: 0 if matched note, 0 if extra note.
    #abs_disp_from_beat: displacement in absolute time from nearest beat
    #normalized_disp: the displacement value normalized according to percentage of time till next
    #beat. This is the only part of the patch that will consult ahead in time. 
            
    interm_patch = {'status': np.zeros(len(all_noteobjs)), 
             'nearest_score_beattime': np.zeros(len(all_noteobjs)),
             'nearest_perf_beattime': np.zeros(len(all_noteobjs)), 
             'actual_perf_time':np.zeros(len(all_noteobjs)), 
             'abs_disp_from_beat':np.zeros(len(all_noteobjs))}
    
    final_patch = {} #tbd
    last_aligned = None #to keep track of the last aligned note processed. 

    for i, (status, src_tlobj_tup, tgt_tlobj_tup) in enumerate(all_noteobjs):
        interm_patch['status'][i] = status
        if status == ALIGNED:
            #Here the time prediction should work.. 
            src_tlobj_note, src_tl_i = src_tlobj_tup
            tgt_tlobj_note, tgt_tl_i = tgt_tlobj_tup
            interm_patch['nearest_score_beattime'][i] = src_tl_beats[src_tl_i]
            interm_patch['nearest_perf_beattime'][i] = tgt_tl_beats[tgt_tl_i]
            interm_patch['actual_perf_time'][i] = tgt_tlobj_note.start
            interm_patch['abs_disp_from_beat'][i] = tgt_tlobj_note.start - tgt_tl_beats[tgt_tl_i] # actual_perf_time - nearest_perf_beattimes
            last_aligned = i

        if status == EXTRA:
            tgt_tlobj_note, tgt_tl_i = tgt_tlobj_tup
            #since it has no score ref, then there is no nearest score beattime nor nearest perf beattime 
            #but, we can get its displacement from the nearest aligned beattime if it exists
            nearest_score_beattime = -1 if not last_aligned else interm_patch['nearest_score_beattime'][i]
            nearest_perf_beattime = -1 if not last_aligned else interm_patch['nearest_perf_beattime'][i]
            interm_patch['nearest_score_beattime'][i] = nearest_score_beattime
            interm_patch['nearest_perf_beattime'][i] = nearest_perf_beattime
            interm_patch['actual_perf_time'][i] = tgt_tlobj_note.start
            interm_patch['abs_disp_from_beat'][i] = tgt_tlobj_note.start - tgt_tl_beats[tgt_tl_i] 
            # actual_perf_time - nearest_perf_beattimes

        if status == MISSING:
            src_tlobj_note, src_tl_i = src_tlobj_tup
            # Missing would also have a src_noteobj
            nearest_score_beattime = -1 if not last_aligned else interm_patch['nearest_score_beattime'][i]
            nearest_perf_beattime = -1 if not last_aligned else interm_patch['nearest_perf_beattime'][i]
            interm_patch['nearest_score_beattime'][i] = nearest_score_beattime
            interm_patch['nearest_perf_beattime'][i] = nearest_perf_beattime
            interm_patch['actual_perf_time'][i] = -1
            interm_patch['abs_disp_from_beat'][i] = -1 #does not exist since the note has not been performed
 
    return interm_patch


def construct_midiroll_from_nakamura():
    #use the output of the match corresp and sps file to construct a midi_roll
    return

def construct_midiroll(all_noteobjs, src_snippet, tgt_snippet):
    timegrid_score = np.linspace(src_snippet.s_start, src_snippet.s_end, 20*(int(src_snippet.s_end) - int(src_snippet.s_start)))
    timegrid_perf = np.linspace(tgt_snippet.s_start, tgt_snippet.s_end, 20*(int(tgt_snippet.s_end) - int(tgt_snippet.s_start)))
    
    aligned_score = np.zeros((120, len(timegrid_score)))
    aligned_perf = np.zeros((120, len(timegrid_perf)))

    #extra is on perf timeline
    extra = np.zeros((120, len(timegrid_perf)))
    #missing is on score timeline
    missing = np.zeros((120, len(timegrid_score)))

    score_beats = []
    perf_beats = []
    for beat in src_snippet.beattimes:
        score_beats.append((np.fabs(beat - timegrid_score)).argmin())
    for beat in tgt_snippet.beattimes:
        perf_beats.append((np.fabs(beat - timegrid_perf)).argmin())

    for i, (status, src_tlobj_tup, tgt_tlobj_tup) in enumerate(all_noteobjs):
        if status == ALIGNED or status == MISSING:
            #Here the time prediction should work.. 
            src_tlobj_note, src_tl_i = src_tlobj_tup
            nearest_score_time_onset_i = (np.fabs(src_tlobj_note.start - timegrid_score)).argmin()
            nearest_score_time_offset_i = (np.fabs(src_tlobj_note.end - timegrid_score)).argmin()
            if status == ALIGNED:
                aligned_score[src_tlobj_note.pitch, nearest_score_time_onset_i:nearest_score_time_offset_i+1] = src_tlobj_note.velocity
            if status == MISSING:
                missing[src_tlobj_note.pitch, nearest_score_time_onset_i:nearest_score_time_offset_i+1] = src_tlobj_note.velocity

        if status == EXTRA or status == ALIGNED:
            tgt_tlobj_note, tgt_tl_i = tgt_tlobj_tup
            nearest_perf_time_onset_i = (np.fabs(tgt_tlobj_note.start - timegrid_perf)).argmin()
            nearest_perf_time_offset_i = (np.fabs(tgt_tlobj_note.end - timegrid_perf)).argmin()
            if status == ALIGNED:
                aligned_perf[tgt_tlobj_note.pitch, nearest_perf_time_onset_i:nearest_perf_time_offset_i+1] = tgt_tlobj_note.velocity
            if status == EXTRA:
                extra[tgt_tlobj_note.pitch, nearest_perf_time_onset_i:nearest_perf_time_offset_i+1] = tgt_tlobj_note.velocity

    return aligned_score, aligned_perf, extra, missing, score_beats, perf_beats

def allnoteobjs_2_df(all_noteobjs):
    #returns pandas dataframe to ease browsing the missing notes, extra notes, etc.
    #(status, src_tlobj_tup, tgt_tlobj_tup) in enumerate(all_noteobjs)
    # src_tlobj_note, src_tl_i = src_tlobj_tup
    # tgt_tlobj_note, tgt_tl_i = tgt_tlobj_tup

    columns=['status', 'src_note_index', 'src_note_start', 'src_note_pitch', 
                                           'tgt_note_index', 'tgt_note_start', 'tgt_note_pitch']
    d = {col:i for i, col in enumerate(columns)}

    data = np.full((len(all_noteobjs, len(columns))), -1)
    for i, (status, (src_tlobj_note, src_tl_i), (tgt_tlobj_note, tgt_tl_i)) in enumerate(all_noteobjs):
        data[i][d['status']] = status
        data[i][d['src_note_index']] = src_tl_i
        data[i][d['src_note_start']]= src_tlobj_note.start
        data[i][d['src_note_pitch']]= src_tlobj_note.pitch
        data[i][d['tgt_note_index']]= tgt_tl_i
        data[i][d['tgt_note_start']]= tgt_tlobj_note.start
        data[i][d['tgt_note_pitch']]= tgt_tlobj_note.pitch
    
    #create in bulk:
    allnoteobjs_df = pd.DataFrame(columns = columns, data=data)
    return allnoteobjs_df

def patch_ms(patch_obj, src_score):
    patched = 0
    return patched

def slice_midi(start_s, end_s, mobj): #TODO: pass in the beat annot through kwargs, either for snippet or whole.
    sliced_mobj = pretty_midi.PrettyMIDI() 
    for instrument in mobj.instruments:
        sliced_instrument = pretty_midi.Instrument(program=instrument.program)
        for note in instrument.notes:
            if start_s <= note.start < end_s or start_s < note.end <= end_s:
                sliced_start = max(start_s, note.start)
                sliced_end = min(end_s, note.end)
                sliced_instrument.notes.append(pretty_midi.Note(
                        start = sliced_start,
                        end = sliced_end,
                        pitch = note.pitch,
                        velocity = note.velocity))
                
        for cc in instrument.control_changes:
            if start_s <= cc.time:
                sliced_instrument.control_changes.append(copy.deepcopy(cc))
                
        sliced_mobj.instruments.append(sliced_instrument)
    return sliced_mobj

class snippet():
    def __init__(self, s_start, s_end, filename, beat_annot_file=None): #TODO: here also, pass the beat annot, to pass it to slice midi
        mobj = pretty_midi.PrettyMIDI(str(filename))
        self.s_start = s_start
        self.s_end = s_end
        self.beat_annot_file = beat_annot_file
        self.beattimes = []
        if beat_annot_file:
            self.beattimes = np.loadtxt(beat_annot_file, usecols=[0])
        
        #src_ticks = (mobj.time_to_tick(ms_start), mobj.time_to_tick(ms_end))
        self.snipt_mobj = slice_midi(s_start, s_end, mobj)
        self.timeline = self.make_timeline()
        return
    
    def make_timeline(self):
        #timeline only includes onsets.
        #notes = self.snipt_mobj.get_onsets()
        all_events = []
        for _, inst in enumerate(self.snipt_mobj.instruments):
            inst: pretty_midi.Instrument = inst
            all_events.extend([(_e.start, _e) for _e in inst.notes])
            #all_events.extend([(_e.end, _e) for _e in inst.notes])
            #all_events.extend([(_e.time, _e) for _e in inst.control_changes])
            #temporary removal of control changes until we can have a functional v1.
            #not sure if end should be considered as a different event than start. for now yes. 
            #the other alternative is to make an event as
            #all_events.extend([(_e.start, _e, _e.end) for _e in inst.notes])
            #this would allow the sorting and the subseq matching to not take into account the end time as an 'event'
            
        all_events = sorted(all_events, key=lambda x: x[0])
        return all_events
    

#this function should be applied to score pairs rather than scores and performances
# because we should want two check if 2 source 
def is_diffable(score1_snipt_obj, score2_snipt_obj):
    #check it they have the same number of beats?
    #this function will be a bit clearer when one example is implemented.
    #also this would be a great candidate to learn.
    return True

def main():
    #todo: argparse thing and file checks
    score_path = '/Users/aliamorsi/Downloads/tude_Op._100_No._10_Tender_Flower.mid'
    perf_path = '/Users/aliamorsi/Documents/Yamaha Internship/burgmuller with no annotations/b-10-annot.mid'

    score_beat_annotation_file = '/Users/aliamorsi/Documents/synthetic-mistake-study/piano-synmist/score_beat_annotations/b-10-score-beats-7-12.txt'

    score_start = 8.333
    score_end = 12.376
    perf_start = 14.500
    perf_end = 21.900

    src_snippet = snippet(score_start, score_end, score_path, score_beat_annotation_file)
    tgt_snippet = snippet(perf_start, perf_end, perf_path)

    patch = diff_ms(src_snippet, tgt_snippet)

def __main__():
    #Pending Todo.
    perf_path = '/Users/aliamorsi/Documents/Yamaha Internship/burgmuller with no annotations/b-05-annot.mid'
    score_path = '/Users/aliamorsi/Downloads/Etude_faciles_et_progressives_Opus_100_No._5_Innocence.mid'

    #check if the files exist
    try:
        #load the snippets
        print('test')
        #must check that the start time is lower than the endtime otherwise no timeline is built

        #fn_out = pathlib.Path(p.run_id) / (fn_mid.stem + '.synerr.mid')
        #mobj_aug.write(str(fn_out))

    except OSError:
        pass

    main()
    return

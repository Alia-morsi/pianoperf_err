#file might change location later.
import os
import partitura.io.importnakamura as nk
import numpy as np

ALIGNED = 0
MISSING = 1
EXTRA = 2

PERF = 0
SCORE = 1

#expects each alignment result for a piece to be placed in a folder with the piecename, and this folder to include the score, performance, and an additional folder called 'Results'

def get_pieces(alignments_basepath):
    #todo: remove the ds store result
    return [i for i in os.listdir(alignments_basepath) if not os.path.isfile(i)]

def get_aligned_pieces(piecename):
    return os.listdir(os.path.join(alignments_basepath, piecename, 'Results'))

#returns the expected paths for the pd alignments. both the results folder (which has the scores) the results for all peperformances of that piece
def create_pd_dir_paths(alignments_basepath, piece_name, performance_id):
    results_folder = os.path.join(alignments_basepath, piece_name, 'Results')
    return results_folder, os.path.join(results_folder, performance_id) 

def get_alignment_results(results_folder, performance_id): #in the pd case, the filestem is the performance id

    corresp_file = os.path.join(results_folder,
                                '{}_corresp.txt'.format(performance_id))
    
    match_file = os.path.join(results_folder,
                                '{}_match.txt'.format(performance_id))
    
    spr_file = os.path.join(results_folder,
                                '{}_spr.txt'.format(performance_id))
    
    corresp = nk.load_nakamuracorresp(corresp_file)
    match = nk.load_nakamuramatch(match_file)
    spr = nk.load_nakamuraspr(spr_file)

    return corresp, match, spr


def construct_allnoteobjs(corresp, match, spr):
    perf, ref, alignment = match

    corresp_ref = corresp[1] #cuz it has the seconds

    perf_dict = {el['id']: el for el in perf}
    ref_dict = {el['id']: el for el in ref}
    ref_dict_corresp = {el['id']: el_corr for el, el_corr in zip(ref, corresp_ref)}

    #info from match
    #dtype=[('onset_div', '<i4'), ('pitch', '<i4'), ('step', '<U256'), ('alter', '<i4'), ('octave', '<i4'), ('id', '<U256')])
    #info from align
    #dtype=[('onset_sec', '<f4'), ('pitch', '<i4'), ('id', '<U256')])
    #it's always pitch then velocity

    all_noteobjs = []

    extra_note_idxs = []
    missing_note_idxs = []
    aligned_note_idxs = []

    num_missing = 0
    num_extra = 0
    num_aligned = 0

    for index, element in enumerate(alignment):
        in_ref = False
        in_perf = False

        if element['label'] == 'insertion':
            perf_index = np.where(perf['id'] == element['performance_id'])[0][0]
            all_noteobjs.append((EXTRA, None, (perf_dict[element['performance_id']], perf_index)))
            num_extra +=1
            extra_note_idxs.append(index)

        if element['label'] == 'deletion':
            ref_index = np.where(ref['id'] == element['score_id'])[0][0]
            all_noteobjs.append((MISSING, (ref_dict_corresp[element['score_id']], ref_index), None)) #to get the note obj only. 
            num_missing +=1
            missing_note_idxs.append(index)

        if element['label'] == 'match':
            perf_index = np.where(perf['id'] == element['performance_id'])[0][0]
            ref_index = np.where(ref['id'] == element['score_id'])[0][0]
            all_noteobjs.append((ALIGNED, (ref_dict_corresp[element['score_id']], ref_index), (perf_dict[element['performance_id']], perf_index)))
            num_aligned +=1
            aligned_note_idxs.append(index)
            #maybe here we will need to have the case of 'replaced' or aligned by checking
            # the pitch value between the ref and the perf

    print('missing: {}'.format(num_missing))
    print('extra: {}'.format(num_extra))
    print('aligned: {}'.format(num_aligned))

    return all_noteobjs, aligned_note_idxs, extra_note_idxs, missing_note_idxs


#goal of these functions is to get in score where are mistakes to try and look at mistake patterns
def get_extra_notes(all_noteobjs):
    return

def get_missing_notes(all_noteobjs):
    return

def get_misaligned_portions(all_noteobjs, window_length):
    #if a section has extra notes or deleted notes but then has some aligned notes
        #copy the region between the contiguous 0s
    return    

def get_mistake_stats(all_noteobjs):
    #how often is it an isolated note and then we resume
    return

def create_midi_viz(): #not sure what the input is
    #this function should:
    #return a midi track for the duration of alignment before a loss
    #return short midi tracks in the areas where some misalignments happened (that did not affect recovery)
    #try to quantify these recoverable mistakes from the non recoverable ones. 
    return

def get_and_write_alignment_info(results_folder, perf_id):
    corresp, match, spr = get_alignment_results(results_folder, perf_id)
    all_noteobjs, aligned_note_idxs, extra_note_idxs, missing_note_idxs = construct_allnoteobjs(corresp, match, spr)
    os.mkdir(os.path.join(results_folder, 'alignment_meta'))
    writepath = '{}.txt'.format(os.path.join(results_folder, 'alignment_meta', perf_id))
    with open(writepath, 'w') as file:
        file.write(str(all_noteobjs))
    return all_noteobjs

#understand what the difference is
#get a list of windows (in score and performance) where there are deviations
# show them our viewer (The Interpreting patches code)
#Then, see if I can incorporate mididiff later.

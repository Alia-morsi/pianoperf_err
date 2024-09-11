import os
import glob
import re
from loading_alignments import get_and_write_alignment_info
import numpy as np

def get_unique_fileids(output_folder):
    # Find all files in the output folder with the specified pattern
    file_pattern = os.path.join(output_folder, '*_*.txt')
    files = glob.glob(file_pattern)

    # Extract unique fileids from the filenames
    fileids = set()
    for file in files:
        match = re.match(r'(.+?)_.*\.txt', os.path.basename(file))
        if match:
            fileids.add(match.group(1))

    return list(fileids)

def process_files(output_folder):
    payload_dtype = [('file_id', 'U10'), ('missing_notes', 'i4'), ('extra_notes', 'i4'), ('aligned_notes', 'i4')]
    fileids = get_unique_fileids(output_folder)
    result_dict = {}
    result_stats = []

    for fileid in fileids:
        all_noteobjs, file_stats = get_and_write_alignment_info(output_folder, fileid)
        result_dict[fileid] = [all_noteobjs]
        result_stats.append((fileid, file_stats['missing_notes'], file_stats['extra_notes'], file_stats['aligned_notes'])) 

    result_stats = np.array(result_stats, dtype=payload_dtype) 
    return result_dict, result_stats

if __name__ == "__main__":
    output_folder = "alignment_output"
    result_dict, note_stats = process_files(output_folder)


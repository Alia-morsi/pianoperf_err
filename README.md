# pianoperf_err

The go-to directory for all things performance assessment. 

Will have alignment, beat tracking, mistake detection, and progress detection. 

within each repository there are whatever things are relating to it (training/validation/test data, checkpoints)

However, for resources that would be used across folders, they would be placed in eval_data or train_data folders outside. Also, for data that has not been gathered by us (whether it is part of a public or private dataset), we will create afolder for it with instructions on how to obtain it. This includes code or models too. 

Then at the top level, are things relating to using whatever techniques were created for performance assessment. eval_data in this case is the evaluation data for performance assessment itself. Currently it has a bunch of datasets but it needs to have the evaluation levels that are currently being developed. 

TODO: The place for mididiff might be better under alignment.

Also utils.py will need to be reorganized as such. 

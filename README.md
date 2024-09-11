# pianoperf_err

You will need to install Beatnet
This should be the go-to directory for all things performance assessment. 


Will have alignment, beat tracking, and mistake detection. 


within each repository there are whatever things are relating to it (training/validation/test data, checkpoints)

Then at the top level, are things relating to using whatever techniques were created for performance assessment. eval_data in this case is the evaluation data for performance assessment itself. Currently it has a bunch of datasets but it needs to have the evaluation levels that will be the core of the TISMIR paper. 

The place for mididiff might be better under alignment.

Also utils.py will need to be reorganized as such. 

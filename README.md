# Sopro-Adapt-the-Voice
### Anastasia Borisenkov, Urs Peter, Annegret Janzso, Joanna Dietinger
This github repository contains all the files we modified or added for the software project **Implementation of a personalized chatbot** in the summer semester of 2021 at the University of Saarland.  
How to use these files and reproduce our results is explained in our report in detail. There you will find instructions on how to handle the files and what parameters to set.

## Instructions
These files are necessary for our implementation of flowtron. Follow the rough instructions below if you want to setup Flowtron the same way we did.  
In utils you will find some useful scripts that can help with data conversion and cleaning; <br/>main_resample.py resamples the audio file based on the specified sampling rate and while rm_silence.py removes leading and trailing silences from the audio files.

## Setup
1. Clone the repository ![Flowtron](https://github.com/NVIDIA/flowtron.git)
2. Paste the files from this repository into the Flowtron directory and overwrite
3. Follow the setup instructions from Flowtron
4. Paste the data for your speaker into the data directory
5. Create a fileslist for your data as seen in the filelist directory
6. Adapt the paths in run_inf.sh to your needs and update the parameters based on your model and needs

## Training
Training and fine-tuning can be done as described in our report.
The commands we used are the following:
- Initially:
 	- python train.py -c config_dir/harvard_libritts/config_louisa.json -p train_config.finetune_layers=["speaker_embedding.weight"] train_config.warmstart_checkpoint_path="models/flowtron_libritts2k.pt" data_config.use_attn_prior=1 train_config.output_directory=outdir2_1841

- After good looking attention:
	- python train.py -c config_dir/harvard_libritts/config_louisa.json -p train_config.finetune_layers=["speaker_embedding.weight"] train_config.warmstart_checkpoint_path="outdir2_1841/model_221000" data_config.use_attn_prior=0 train_config.output_directory=1841_attn0
## Inference
For inference use the provided shell script run_inference.sh. It will infer sentences given in the format of the filelist. You can adapt this script easily. <br/>
It initiates the inference and saves them to the specified location.

## Eval 
For evaluation we used streamlit with the human_eval.py script, simply put respective data in the synthesized and the original directories and execute human_eval.py to collect the necessary data.
<br/>The interpretation is done by the eval_interpretation file. It takes the generated .db files from the human_eval script and visualises the results as graphs.
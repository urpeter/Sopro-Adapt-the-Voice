import json
import os
import librosa
from tqdm import tqdm
import soundfile as sf
import numpy as np
def rewrite(file, wavs, train):
    with open(file) as f:
        jobj = json.load(f)
        txts = jobj["data"]
        #for wav_path in wavs:       
         #   audio_data = os.listdir(wav_path)
          #  aug_audio_data = [wav_path.join(x) for x in audio_data] 
        
        #print(len(aug_audio_data))
        
        if train:
            with open("harvard_audiopaths_text_sid_train_fileslist.txt", "w") as t:
                for i in range(0, 575):
                    t.write(wavs[i] + "|" + txts[i] + "|0\n")
        else:
            with open("harvard_audiopaths_text_sid_val_fileslist.txt", "w") as t:
                for i in range(576, 720):
                    t.write(wavs[i] + "|" + txts[i] + "|0\n")


if __name__ == '__main__':
    path = "/local/anasbori/sopro_tts/flowtron/data/havard/"
    wav_list = []
    for files in os.listdir(path):
        some_list = os.listdir(path + files)
        wav_irgendwie = [files+"/"+x for x in some_list]
        wav_list.extend(wav_irgendwie)

    augmented_wavs = [path+x for x in wav_list]
    for elem in tqdm(augmented_wavs):
        data, sar = librosa.load(elem, sr=24000)
        # data2 = data.astype(np.int16, order='C')
        # sf.write(elem,data=data2,samplerate=sar)
        # librosa.output.write_wav(elem, data, sar)
        sf.write(elem, data, sar, subtype='PCM_16')
        
    print(augmented_wavs[0])
    rewrite("./harvard_sentences.json", augmented_wavs, train=True)
    rewrite("./harvard_sentences.json", augmented_wavs, train=False)

import streamlit as st
import os
import sys
import sqlite3
import random

st.title("TTS Evaluation")

original_path = "louisa_trim_eval/"
# model_path = "model/"
model_path = "synth_eval/"
# maybe add more pathes for different models
original_files = os.listdir(original_path) # assuming that the names of the original files and the names of the model-files are the same but in different folders
# for testing
# path = "data/"
# audio_1 = open(path + "SomeHarvardSentencesForEval.wav","rb") # testfile 1
# audio_2 = open(path + "MoreHarvSentForEv.wav","rb") # testfile 2

original = dict()
model = dict()
for item in original_files:
    # print(item)
    for sample in os.listdir(original_path + item):
        # print(sample)
        original[original_path + item + sample] = open(original_path + item + "/" + sample,"rb")
        model[original_path + item + sample] = open(model_path + item + "/" + sample,"rb")
# print(len(original.keys()))
# for i in range(20): # get 10 random samples
#     random_item = random.choice(original_files)
#     random_sample = random.choice(original_files + random_item)
#     while not random_sample.endswith(".wav"): # try until you find a random sample that is a .wav file
#         random_sample = random.choice(original_files + random_item)
#     # issue: a person might get the same sample twice!
#     original[random_item + random_sample] = open(original_path + random_item + random_sample,"rb")
#     model[random_item + random_sample] = open(model_path + random_item + random_sample,"rb")
    # original_files.remove(random_item)

# for testing
# model["TestFile"] = audio_1
# original["TestFile"] = audio_2


connection = sqlite3.connect("results.db")
cursor = connection.cursor()
q_sql = "CREATE TABLE IF NOT EXISTS Quality( " \
    "File TEXT, " \
    "Score INTEGER, " \
    "Phrase TEXT, " \
    "Comments TEXT )"
cursor.execute(q_sql)

s_sql = "CREATE TABLE IF NOT EXISTS Similarity(" \
    "File TEXT, " \
    "Score INTEGER, " \
    "Comments TEXT)"
cursor.execute(s_sql)

form = st.form(key="eval")
form.title("Evaluation of Quality")
form.write("Listen to the following audio files.\nFor each file, assign a value on the slider between 1 and 5 for the quality of the audio (how well can it be understood?) according to the following:\n\n")

form.write("5: Perfect. Like face-to-face conversation or radio reception.")
form.write("4: Fair. Imperfections can be perceived, but sound form is clear. This is (supposedly) the range for cell phones.")
form.write("3: Annoying.")
form.write("2: Very annoying. Nearly impossible to communicate.")
form.write("1: Impossible to communicate.\n\n")

form.write("After that, you will be asked to transcribe what the voice in the audio file was saying. You will also have space for any additional comments.")
form.write("Thank you for your help in this evaluation.")

for n,item in enumerate(model.keys()):
    form.audio(model[item])
    score = form.slider("Rate the Quality of this audio file",1,5,key=f'quality{n}')
    phrase = form.text_input(label="What was said?",key=f'qualityt{n}')
    comments = ""
    # comments = form.text_input(label="Additional comments on quality",key=f'qualityt2{n}')
    params = (str(item), str(score), phrase, comments)
    cursor.execute("INSERT INTO Quality VALUES (?, ?, ?, ?)", params)
with open("Quality-Comments.txt","a") as qc:
    comment = form.text_input(label="Additional comments on quality",key="comment")
    qc.write(comment + "\n")

form.title("Evaluation of Voice Similarity")
form.write("Listen to the following pairs of audio files.\nFor each file pair, assign a value on the slider between 1 and 5 for how similar the two voices are (regardless of the sound quality - could both audios come from the same speaker?) according to the following:\n\n")

form.write("5: Perfect. Both audio-files are recordings of the same voice.")
form.write("4: Fair. Imperfections can be perceived, but voice form is very similar (e.g. a voice in-person compared to the same voice over the phone).")
form.write("3: Differences of the two voices are recognizable.")
form.write("2: Rather huge differences between the two voices.")
form.write("1: The voices are completely different to each other (e.g. a female speaker compared to a male speaker).\n\n")

form.write("After that, you will have space for any additional comments.")
form.write("Thank you for your help in this evaluation.")

# present each random file-pair and ask for evaluation
for n,item in enumerate(model.keys()):
    col1,col2 = form.beta_columns(2) # present audio files next to one another
    with col1:
        # form.audio(audio_1) # present audio of testfile 1
        form.audio(original[item])
    with col2:
        # form.audio(audio_2) # present audio of testfile 2
        form.audio(model[item])
    
    score = form.slider("Rate the Similarity of the Voices in these two audio files",1,5,key=f'similarity{n}')
    # comments = form.text_input(label="Additional comments on voice similarity",key=f'similarityt{n}')
    comments = ""
    params = (str(item), str(score), comments)
    cursor.execute("INSERT INTO Similarity VALUES (?, ?, ?)", params)
with open("Similarity-Comments.txt","a") as sc:
    comment = form.text_input(label="Additional comments on similarity",key="comment2")
    sc.write(comment + "\n")

submit = form.form_submit_button("Submit")

if submit:
    st.write("Thank you for your participation!")
    connection.commit()
    connection.close()
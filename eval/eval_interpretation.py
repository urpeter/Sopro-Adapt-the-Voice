import pandas as pd
import pickle
import matplotlib.pyplot as plt
import numpy as np
# from jiwer import wer # for word error rate
from collections import defaultdict
import sqlite3

def get_mean_score(df,sample):
    all_rows = df.loc[df["File"] == sample]
    return all_rows["Score"].sum() / len(all_rows) # get mean score for current sample

def get_comments(df,sample):
    all_rows = df.loc[df["File"] == sample]
    all_comments = [] # store all comments for each sample in one place to be evaluated in person
    for item in all_rows["Comments"]:
        all_comments.append(item)
    return all_comments


def wer(r, h):
    """
    from https://martin-thoma.com/word-error-rate-calculation/
    Calculation of WER with Levenshtein distance.
    Works only for iterables up to 254 elements (uint8).
    O(nm) time ans space complexity.
    Parameters
    ----------
    r : list
    h : list
    Returns
    -------
    int
    Examples
    --------
    >>> wer("who is there".split(), "is there".split())
    1
    >>> wer("who is there".split(), "".split())
    3
    >>> wer("".split(), "who is there".split())
    3
    """
    d = np.zeros((len(r) + 1) * (len(h) + 1), dtype=np.uint8)
    d = d.reshape((len(r) + 1, len(h) + 1))
    for i in range(len(r) + 1):
        for j in range(len(h) + 1):
            if i == 0:
                d[0][j] = j
            elif j == 0:
                d[i][0] = i

    # computation
    for i in range(1, len(r) + 1):
        for j in range(1, len(h) + 1):
            if r[i - 1] == h[j - 1]:
                d[i][j] = d[i - 1][j - 1]
            else:
                substitution = d[i - 1][j - 1] + 1
                insertion = d[i][j - 1] + 1
                deletion = d[i - 1][j] + 1
                d[i][j] = min(substitution, insertion, deletion)

    return d[len(r)][len(h)]

def get_phrase_correctness(df,sample,score):
    original_text_path = "original_text/"
    all_file_rows = df.loc[df["File"] == sample]# and df["Score"] == score]
    all_rows = all_file_rows.loc[all_file_rows["Score"] == score]
    # all_rows = all_rows.T
    # print(all_rows.columns)
    # print(type(all_file_rows))
    # print(all_file_rows)
    # exit()
    with open(original_text_path + sample[-21:] + ".txt","r") as current:
        original_phrase = current.readlines()
        total = 0
        n = 0
        for item in all_rows["Phrase"]:
            # print(type(item))
            # print(type(original_phrase))
            # print(item)
            n += 1
            total += wer(original_phrase[0].lower().split(),item.lower().split())
    return total/n # get mean word error rate

def get_ratings(d,df,sample,mode):
    d["1"] = 0
    d["2"] = 0
    d["3"] = 0
    d["4"] = 0
    d["5"] = 0
    all_rows = df.loc[df["File"] == sample]
    for item in all_rows["Score"]:
        d[str(item)] += 1
        if mode == "q":
            d["mean-wer"][str(item)] = get_phrase_correctness(df,sample,item)
    return d

connection = sqlite3.connect("results.db")
connection2 = sqlite3.connect("results2.db")
connection3 = sqlite3.connect("results3.db")
quality = pd.read_sql("SELECT * from Quality",connection,columns=["File","Score","Phrase","Comments"])
quality2 = pd.read_sql("SELECT * from Quality",connection2,columns=["File","Score","Phrase","Comments"])
quality3 = pd.read_sql("SELECT * from Quality",connection3,columns=["File","Score","Phrase","Comments"])
similarity = pd.read_sql("SELECT * from Similarity",connection,columns=["File","Score","Comments"])
similarity2 = pd.read_sql("SELECT * from Similarity",connection2,columns=["File","Score","Comments"])
similarity3 = pd.read_sql("SELECT * from Similarity",connection3,columns=["File","Score","Comments"])
quality = pd.concat([quality, quality2], ignore_index=True)
quality = pd.concat([quality, quality3], ignore_index=True)
similarity = pd.concat([similarity,similarity2],ignore_index=True)
similarity = pd.concat([similarity,similarity3],ignore_index=True)

quality_dict = dict()
similarity_dict = dict()

total_quality = 0
total_similarity = 0
length = 0
for i,row in quality.iterrows():
    sample = row["File"]
    if sample in quality_dict.keys():
        continue
    quality_dict[sample] = dict()
    similarity_dict[sample] = dict()
    quality_dict[sample]["mean-wer"] = defaultdict(int)
    similarity_dict[sample]["mean-wer"] = defaultdict(int)
    quality_dict[sample] = get_ratings(quality_dict[sample],quality,sample,"q")
    similarity_dict[sample] = get_ratings(similarity_dict[sample],similarity,sample,"s")
    quality_dict[sample]["mean"] = get_mean_score(quality,sample)
    total_quality += quality_dict[sample]["mean"]
    # add checking phrase given by user to actual phrase in textfile
    quality_dict[sample]["comments"] = get_comments(quality,sample)
    similarity_dict[sample]["mean"] = get_mean_score(similarity,sample)
    total_similarity += similarity_dict[sample]["mean"]
    similarity_dict[sample]["comments"] = get_comments(similarity,sample)
    length += 1
total_quality_average = total_quality/length
total_similarity_average = total_similarity/length

with open("quality.pkl","wb") as q:
    pickle.dump(quality_dict,q)
with open("similarity.pkl","wb") as s:
    pickle.dump(similarity_dict,s)
# TODO:  create plots
# TODO: barcharts for phrase correctness

all_means_qual = 0
all_means_sim = 0
all_mean_wer = 0
scores = ("1","2","3","4","5")
x_pos = np.arange(len(scores))
for sample in quality_dict.keys():
    q_performance = [quality_dict[sample]["1"],quality_dict[sample]["2"],quality_dict[sample]["3"],quality_dict[sample]["4"],quality_dict[sample]["5"]]
    plt.bar(x_pos, q_performance, align="center",alpha=0.5)
    plt.xticks(x_pos, scores)
    plt.ylabel("Amount of Ratings")
    plt.xlabel('Score')
    plt.title('Amount of Ratings in Quality for ' + sample + "(Mean = " + str(quality_dict[sample]["mean"]) + ")")
    plt.tight_layout()
    plt.savefig(sample[-21:] + 'quality.png')
    plt.close()

    w_performance = [quality_dict[sample]["mean-wer"]["1"],quality_dict[sample]["mean-wer"]["2"],quality_dict[sample]["mean-wer"]["3"],quality_dict[sample]["mean-wer"]["4"],quality_dict[sample]["mean-wer"]["5"]]
    plt.bar(x_pos, w_performance, align="center", alpha=0.5)
    plt.xticks(x_pos,scores)
    plt.ylabel("Mean Word Error Rate")
    plt.xlabel("Score")
    plt.title("Mean Word Error Rate by Score for " + sample)
    plt.tight_layout()
    plt.savefig(sample[-21:] + "wer.png")
    plt.close()

    s_performance = [similarity_dict[sample]["1"],similarity_dict[sample]["2"],similarity_dict[sample]["3"],similarity_dict[sample]["4"],similarity_dict[sample]["5"]]
    plt.bar(x_pos, s_performance, align='center', alpha=0.5)
    plt.xticks(x_pos, scores)
    plt.ylabel("Amount of Ratings")
    plt.xlabel('Score')
    plt.title('Amount of Ratings in Similarity for ' + sample + "(Mean = " + str(similarity_dict[sample]["mean"]) + ")")
    plt.tight_layout()
    plt.savefig(sample[-21:] + "similarity.png")
    plt.close()

    all_means_qual += quality_dict[sample]["mean"]
    all_means_sim += similarity_dict[sample]["mean"]
    all_mean_wer += sum(quality_dict[sample]["mean-wer"].values())

oq_performance = [sum([quality_dict[sample]["1"] for sample in quality_dict.keys()]),sum([quality_dict[sample]["2"] for sample in quality_dict.keys()]),sum([quality_dict[sample]["3"] for sample in quality_dict.keys()]),sum([quality_dict[sample]["4"] for sample in quality_dict.keys()]),sum([quality_dict[sample]["5"] for sample in quality_dict.keys()])]
plt.bar(x_pos,oq_performance,align="center",alpha=0.5)
plt.xticks(x_pos, scores)
plt.ylabel("Amount of Ratings")
plt.xlabel('Score')
plt.title('Amount of Ratings in Quality overall (Mean = ' + str(all_means_qual/len(quality_dict.keys())) + ")")
plt.tight_layout()
plt.savefig("overall_quality.png")
plt.close()

os_performance = [sum([similarity_dict[sample]["1"] for sample in similarity_dict.keys()]),sum([similarity_dict[sample]["2"] for sample in similarity_dict.keys()]),sum([similarity_dict[sample]["3"] for sample in similarity_dict.keys()]),sum([similarity_dict[sample]["4"] for sample in similarity_dict.keys()]),sum([similarity_dict[sample]["5"] for sample in similarity_dict.keys()])]
plt.bar(x_pos,os_performance,align="center",alpha=0.5)
plt.xticks(x_pos, scores)
plt.ylabel("Amount of Ratings")
plt.xlabel('Score')
plt.title('Amount of Ratings in Similarity overall (Mean = ' + str(all_means_sim/len(similarity_dict.keys())) + ")")
plt.tight_layout()
plt.savefig("overall_similarity.png")
plt.close()

ow_performance = [sum([quality_dict[sample]["mean-wer"]["1"] for sample in quality_dict.keys()]),
sum([quality_dict[sample]["mean-wer"]["2"] for sample in quality_dict.keys()]),
sum([quality_dict[sample]["mean-wer"]["3"] for sample in quality_dict.keys()]),
sum([quality_dict[sample]["mean-wer"]["4"] for sample in quality_dict.keys()]),
sum([quality_dict[sample]["mean-wer"]["5"] for sample in quality_dict.keys()])]
plt.bar(x_pos, ow_performance, align="center", alpha=0.5)
plt.xticks(x_pos,scores)
plt.ylabel("Mean Word Error Rate")
plt.xlabel("Score")
plt.title("Mean Word Error Rate by Score overall")
plt.tight_layout()
plt.savefig("overall_wer.png")
plt.close()

print("Overall Mean of Quality: " + str(all_means_qual/len(quality_dict.keys())))
print("Overall Mean of Similarity: " + str(all_means_sim/len(similarity_dict.keys())))
print("Overall Mean Word Error Rate: " + str(all_mean_wer/len(quality_dict.keys())))
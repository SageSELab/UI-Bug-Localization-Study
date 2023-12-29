#https://github.com/microsoft/CodeBERT/tree/master/UniXcoder#2-similarity-between-code-and-nl

import torch
from unixcoder import UniXcoder

import torch.nn.functional as F
import os
import re
from nltk.tokenize import wordpunct_tokenize
import json
import csv
import pandas as pd
import math
import numpy as np

def get_file_content(file_name):
    # Read the file
    file_content = open(file_name, "r")
    file_content = file_content.read()
    return file_content

def rank_files(sorted_similarity_scores, original_buggy_locations):
	ranks = []
	unique_file_names = set()
	for bug_location in original_buggy_locations["bug_location"]:
		buggy_file = bug_location["file_name"]
		if buggy_file not in unique_file_names:
			unique_file_names.add(buggy_file)
			order_number = 1
			for key in sorted_similarity_scores:
				if buggy_file in key:
					ranks.append(order_number)
					break
				order_number += 1
	ranks.sort()
	return ranks

def get_bug_report_contents_preprocessed(bug_id, query_type, query):
	bug_report_file = "/Users/junayed/Documents/NecessaryDocs/GeorgeMasonUniversity/Research/Projects/BugLocalization/FaultLocalizationCode/data/PreprocessedData/Preprocessed_with_" + query_type + "/Preprocessed_" + query + "/bug_report_" + bug_id + ".txt"
	bug_report_contents = get_file_content(bug_report_file)
	if bug_report_contents is None or len(bug_report_contents)<1:
		bug_report_contents = ""

	return bug_report_contents


#Encode text
def encode(texts):
	# Tokenize sentences
	tokens_ids = model.tokenize([texts],max_length=512,mode="<encoder-only>")
	source_ids = torch.tensor(tokens_ids)

	tokens_embeddings,max_func_embedding = model(source_ids)

	norm_max_func_embedding = torch.nn.functional.normalize(max_func_embedding, p=2, dim=1)

	return norm_max_func_embedding

def get_code_processed(bug_id, codeFilepath):
	filename = "/Users/junayed/Documents/NecessaryDocs/GeorgeMasonUniversity/Research/Projects/BugLocalization/FaultLocalizationCode/data/PreprocessedData/Preprocessed_code/bug-" + bug_id + ".csv"
	file_list_df = pd.read_csv(filename)
	files_for_bug_id = file_list_df.loc[file_list_df['FilePath']==codeFilepath, 'PreprocessedCode'].values.tolist()
	
	if len(files_for_bug_id)<1:
		return ""
	return files_for_bug_id[0]

def calculate_similarity_score(code_processed, bug_report_emb):
	number_of_segments = math.floor(len(code_processed)/512)+1
	#print("sengment")
	#print(number_of_segments)
	sim_scores = []
	start_ind = 0
	end_ind = 512
	for i in range(number_of_segments-1):
		cur_code_segment = code_processed[start_ind:end_ind]
		code_emb = encode(cur_code_segment)
		score = torch.einsum("ac,bc->ab", code_emb, bug_report_emb)[0].cpu().tolist()
		#print(score)
		sim_scores.append(score[0])
		start_ind+=512
		end_ind+=512

	cur_code_segment = code_processed[start_ind:len(code_processed)]
	code_emb = encode(cur_code_segment)
	score = torch.einsum("ac,bc->ab", code_emb, bug_report_emb)[0].cpu().tolist()
	#print(score)
	sim_scores.append(score[0])

	return np.max(sim_scores)

# The method for calculating the similarity scores
def calc_max_similarity_scores(files_list, bug_id):
	similarity_scores = {}
	already_computed_scores = {}
	#bug_report_tokens = []

	query_name = "GUI_State"
	bug_report_content = get_bug_report_contents_preprocessed(bug_id, query_name, "bug_report_original")
	
	bug_report_emb = encode(bug_report_content)
	#print(len(files_list))
	all_file_tokens = []
	file_count = 0
	for file_name in files_list:
		code_processed = get_code_processed(bug_id, file_name)
		#print("len " + str(len(code_processed)))

		# code_emb = encode(code_processed)
		# #print(code_emb.shape)
		# score = torch.einsum("ac,bc->ab", code_emb, bug_report_emb)
		# # print("score")
		# # print(score)
		# score = score[0].cpu().tolist()
		# print(score)
		file_count += 1
		#print("file count " + str(file_count))
		similarity_scores[file_name] = calculate_similarity_score(code_processed, bug_report_emb)
	return similarity_scores

def write_to_csv(write_file, row):
	with open(write_file, 'a') as file:
		writer = csv.writer(file)
		writer.writerow(row)

# Load model from HuggingFace Hub
#tokenizer = AutoTokenizer.from_pretrained("microsoft/codebert-base")
model = UniXcoder("microsoft/unixcoder-base")

class_result_output_file = "results/unixcoder.csv"

with open(class_result_output_file, 'w') as file:
	writer = csv.writer(file)
	writer.writerow(["Bug Report ID", "#Files (.java)", "#BuggyFiles", "Ranks"])

# List of bug reports

# bug_issue_ids = ["2", "8", "10", "18", "19", "44",
#                 "53", "71", "117", "128", "129", "130",
#                 "135", "191", "201", "206", "209", "256",
#                 "1073", "1096", "1146",
#                 "1147", "1151", "1202", "1205", "1207",
#                 "1214", "1215", "1223", "1224",
#                 "1226", "1299", "1399", "1406", "1430", "1441",
#                 "1445", "1481", "1645", "45", "54", "76", "92", "101", "106", "110", "158", "160", "162", "168",
#                  "192", "198", "199", "200", "248", "1150", "1198", "1228",
#                 "1389", "1425", "1446", "1563", "1568", "1641"]

bug_issue_ids = ["10", "18", "19", "44",
                "53", "71", "117", "128", "129", "130",
                "135", "191", "201", "206", "209", "256",
                "1073", "1096", "1146",
                "1147", "1151", "1202", "1205", "1207",
                "1214", "1215", "1223", "1224",
                "1226", "1299", "1399", "1406", "1430", "1441",
                "1445", "1481", "1645", "45", "54", "76", "92", "101", "106", "110", "158", "160", "162", "168",
                 "192", "198", "199", "200", "248", "1150", "1198", "1228",
                "1389", "1425", "1446", "1563", "1568", "1641"]

#bug_issue_ids = ["10"]

for bug_issue_id in bug_issue_ids:
	data_row = []
	data_row.append(bug_issue_id)
	print("---------------- Bug Report ID: " + str(bug_issue_id) + " ----------------")
	# Android project folder
	path = "/Users/junayed/Documents/NecessaryDocs/GeorgeMasonUniversity/Research/Projects/BugLocalization/Backup/CodeUnused/BuggyProjects/bug-" + str(bug_issue_id)

	# Finding all .java files
	files_list = []
	for root, subdirs, files in os.walk(path):
		for file_name in files:
			#if (".java" in file_name) or (".xml" in file_name):
			if ".java" in file_name:
				files_list.append(os.path.join(root, file_name))
	data_row.append(len(files_list))

	# Calculate the similarity score for each source code file
	#print("Calculating the similarity scores...")
	#similarity_scores = {}
	similarity_scores = calc_max_similarity_scores(files_list, bug_issue_id)

	# print the similarity scores in descending order
	order_number = 1;
	sorted_similarity_scores = sorted(similarity_scores, key=similarity_scores.get, reverse=True)
	for key in sorted_similarity_scores:
		order_number += 1

		######## Read json file containing the correct bug locations ###########
	json_file = "../data/JSON-Files-All/" + str(bug_issue_id) + ".json"
	with open(json_file, 'r') as jfile:
		json_data = jfile.read()
	original_buggy_locations = json.loads(json_data)
	data_row.append(len(original_buggy_locations["bug_location"]))

	# Ranks of correct bug locations in the result
	ranks = rank_files(sorted_similarity_scores, original_buggy_locations)
	#ranks = [1, 2]
	print("Ranks in results:", ranks)
	data_row.append(ranks)
		
	write_to_csv(class_result_output_file, data_row)

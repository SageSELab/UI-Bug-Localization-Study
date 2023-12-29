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
import sys
import getopt
import argparse
import numpy as np
import math

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

# def get_embedded_code_list(bug_id, files_list):
# 	emb_dict = {}
# 	for file_name in files_list:
# 		code_processed = get_code_processed(bug_id, file_name)
# 		code_emb = encode(code_processed)
# 		emb_dict[file_name] = code_emb
# 	return emb_dict

# The method for calculating the similarity scores
# def calc_max_similarity_scores(files_list, bug_id, query_name, query):
# 	similarity_scores = {}

# 	bug_report_content = get_bug_report_contents_preprocessed(bug_id, query_name, query)
	
# 	bug_report_emb = encode(bug_report_content)
# 	all_file_tokens = []
# 	file_count = 0
# 	for file_name in files_list:
# 		code_emb = emb_dict[file_name]
# 		score = torch.einsum("ac,bc->ab", code_emb, bug_report_emb)
# 		score = score[0].cpu().tolist()
# 		file_count += 1
# 		print("file count " + str(file_count))
# 		similarity_scores[file_name] = score[0]
# 	return similarity_scores

def write_to_csv(write_file, row):
	with open(write_file, 'a') as file:
		writer = csv.writer(file)
		writer.writerow(row)

def write_ranks_to_csv(bug_issue_id, number_of_files, similarity_scores, class_result_output_file):
	data_row = []
	data_row.append(bug_issue_id)
	data_row.append(number_of_files)
	
	#print("Calculating the similarity scores...")

	# print the similarity scores in descending order
	order_number = 1;
	sorted_similarity_scores = sorted(similarity_scores, key=similarity_scores.get, reverse=True)
	for key in sorted_similarity_scores:
		#print(order_number, key, similarity_scores[key])
		order_number += 1

	######## Read json file containing the correct bug locations ###########
	json_file = "../data/JSON-Files-All/" + str(bug_issue_id) + ".json"
	with open(json_file, 'r') as jfile:
		json_data = jfile.read()
	original_buggy_locations = json.loads(json_data)
	data_row.append(len(original_buggy_locations["bug_location"]))

	# Ranks of correct bug locations in the result
	ranks = rank_files(sorted_similarity_scores, original_buggy_locations)
	print("Ranks in results:", ranks)
	data_row.append(ranks)
	write_to_csv(class_result_output_file, data_row)

def calculate_similarity(code_emb_list, query_emb):
	sim_score_list = []
	for code_emb in code_emb_list:
		score = torch.einsum("ac,bc->ab", code_emb, query_emb)
		score = score[0].cpu().tolist()
		sim_score_list.append(score[0])
	return np.max(sim_score_list)

def get_code_segment_embedding(code_processed):
	number_of_segments = math.floor(len(code_processed)/512)+1
	#print("segment: " + str(number_of_segments))
	code_emb_list = []
	sim_scores = []
	start_ind = 0
	end_ind = 512
	for i in range(number_of_segments-1):
		cur_code_segment = code_processed[start_ind:end_ind]
		code_emb = encode(cur_code_segment)
		code_emb_list.append(code_emb)

		start_ind+=512
		end_ind+=512

	cur_code_segment = code_processed[start_ind:len(code_processed)]
	code_emb = encode(cur_code_segment)
	code_emb_list.append(code_emb)

	return code_emb_list

def compute_result(bug_id, files_list, query_name, 
	class_result_output_file, replaced_query_output_file, query_expansion1_output_file, query_expansion2_output_file, query_expansion3_output_file):
	#similarity_scores = calc_max_similarity_scores(files_list, bug_issue_id, query_name, query)

	original_bug_report_similarity_scores = {}
	original_bug_report = get_bug_report_contents_preprocessed(bug_id, query_name, "bug_report_original")
	original_bug_report_emb = encode(original_bug_report)

	replaced_query_similarity_scores = {}
	replaced_query = get_bug_report_contents_preprocessed(bug_id, query_name, "replaced_query")
	replaced_query_emb = encode(replaced_query)

	query_expansion_1_similarity_scores = {}
	query_expansion_1 = get_bug_report_contents_preprocessed(bug_id, query_name, "query_expansion_1")
	query_expansion_1_emb = encode(query_expansion_1)

	query_expansion_2_similarity_scores = {}
	query_expansion_2 = get_bug_report_contents_preprocessed(bug_id, query_name, "query_expansion_2")
	query_expansion_2_emb = encode(query_expansion_2)

	query_expansion_3_similarity_scores = {}
	query_expansion_3 = get_bug_report_contents_preprocessed(bug_id, query_name, "query_expansion_3")
	query_expansion_3_emb = encode(query_expansion_3)

	file_count = 0
	for file_name in files_list:
		file_count += 1
		#print("file count " + str(file_count))
		code_processed = get_code_processed(bug_id, file_name)
		code_emb_list = get_code_segment_embedding(code_processed)

		orginal_bug_report_sim_score = calculate_similarity(code_emb_list, original_bug_report_emb)
		original_bug_report_similarity_scores[file_name] = orginal_bug_report_sim_score

		replaced_query_sim_score = calculate_similarity(code_emb_list, replaced_query_emb)
		replaced_query_similarity_scores[file_name] = replaced_query_sim_score

		query_expansion_1_sim_score = calculate_similarity(code_emb_list, query_expansion_1_emb)
		query_expansion_1_similarity_scores[file_name] = query_expansion_1_sim_score

		query_expansion_2_sim_score = calculate_similarity(code_emb_list, query_expansion_2_emb)
		query_expansion_2_similarity_scores[file_name] = query_expansion_2_sim_score

		query_expansion_3_sim_score = calculate_similarity(code_emb_list, query_expansion_3_emb)
		query_expansion_3_similarity_scores[file_name] = query_expansion_3_sim_score

	write_ranks_to_csv(bug_id, len(files_list), original_bug_report_similarity_scores, class_result_output_file)
	write_ranks_to_csv(bug_id, len(files_list), replaced_query_similarity_scores, replaced_query_output_file)
	write_ranks_to_csv(bug_id, len(files_list), query_expansion_1_similarity_scores, query_expansion1_output_file)
	write_ranks_to_csv(bug_id, len(files_list), query_expansion_2_similarity_scores, query_expansion2_output_file)
	write_ranks_to_csv(bug_id, len(files_list), query_expansion_3_similarity_scores, query_expansion3_output_file)
	

def create_header(class_result_output_file):
	with open(class_result_output_file, 'w') as file:
		writer = csv.writer(file)
		writer.writerow(["Bug Report ID", "#Files (.java)", "#BuggyFiles", "Ranks"])

# Load model from HuggingFace Hub
#tokenizer = AutoTokenizer.from_pretrained("microsoft/codebert-base")
model = UniXcoder("microsoft/unixcoder-base")


def main(args):
	bug_issue_ids = ["2", "8", "10", "18", "19", "44",
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

	class_result_output_file = args['result'] + "/original.csv"
	create_header(class_result_output_file)

	replaced_query_output_file = args['result'] + "/replaced-query.csv"
	create_header(replaced_query_output_file)

	query_expansion1_output_file = args['result'] + "/query-expansion-1.csv"
	create_header(query_expansion1_output_file)

	query_expansion2_output_file = args['result'] + "/query-expansion-2.csv"
	create_header(query_expansion2_output_file)

	query_expansion3_output_file = args['result'] + "/query-expansion-3.csv"
	create_header(query_expansion3_output_file)

	for bug_issue_id in bug_issue_ids:
		data_row = []
		data_row.append(bug_issue_id)
		print("---------------- Bug Report ID: " + str(bug_issue_id) + " ----------------")		
		path = args['corpus'] + "/bug-" + str(bug_issue_id)

		# Finding all .java files
		files_list = []
		for root, subdirs, files in os.walk(path):
			for file_name in files:
				#if (".java" in file_name) or (".xml" in file_name):
				if ".java" in file_name:			
					fullpath = os.path.join(root, file_name)
					#fullpath = fullpath.replace(args['truncated_path'], 'BuggyProjects')
					#print(fullpath)
					files_list.append(fullpath)

		query_name = args['query']

		# emb_dict = get_embedded_code_list(bug_issue_id, files_list)
		
		compute_result(bug_issue_id, files_list, query_name, 
			class_result_output_file, replaced_query_output_file, query_expansion1_output_file, query_expansion2_output_file, query_expansion3_output_file)
		# compute_result(bug_issue_id, files_list, replaced_query_output_file, query_name, "replaced_query")
		# compute_result(bug_issue_id, files_list, query_expansion1_output_file, query_name, "query_expansion_1")
		# compute_result(bug_issue_id, files_list, query_expansion2_output_file, query_name, "query_expansion_2")	
		# compute_result(bug_issue_id, files_list, query_expansion3_output_file, query_name, "query_expansion_3")
		# emb_dict.clear()

if __name__ == "__main__":
	# https://stackoverflow.com/questions/7427101/simple-argparse-example-wanted-1-argument-3-results
	parser = argparse.ArgumentParser()
	parser.add_argument('-rf','--result', help='Description for result', required=True)
	parser.add_argument('-q','--query', help='Description for query', required=True)
	parser.add_argument('-c','--corpus', help='Description for corpus', required=True)
	parser.add_argument('-tp','--truncated_path', help='Description for corpus', required=False)
	args = vars(parser.parse_args())
	main(args)
 

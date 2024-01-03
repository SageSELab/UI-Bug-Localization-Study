import pandas as pd
import argparse
from ast import literal_eval
import csv
import json
import numpy as np
import os
import glob
import re

def write_to_csv(write_file, row):
	with open(write_file, 'a') as file:
		writer = csv.writer(file)
		writer.writerow(row)

def write_rankings_row(filename, approach, ranklist_br_best_avg, ranklist_rq_best_avg, ranklist_qe1_best_avg,
				ranklist_qe2_best_avg, ranklist_qe3_best_avg):
	result_row=[]
	result_row.append(approach)
	result_row.append(ranklist_br_best_avg)
	result_row.append(ranklist_rq_best_avg)
	result_row.append(ranklist_qe1_best_avg)
	result_row.append(ranklist_qe2_best_avg)
	result_row.append(ranklist_qe3_best_avg)
	write_to_csv(filename, result_row)

def get_java_file_count(bug_id):
	filename = "Statistics/java_file_count.csv"
	ranklist_df = pd.read_csv(filename)

	java_file_count = ranklist_df.loc[ranklist_df['Bug_Id']==int(bug_id), "Number of Java files"].values.tolist()
	if java_file_count is None or len(java_file_count)<1 or java_file_count!=java_file_count:
		return 0
	return java_file_count[0]


def get_ranklist_len(ranklist):
	len_ranks_list = []
	for ranks in ranklist:
		len_ranks_list.append(len(ranks))
	return len_ranks_list

def calculate_final_metric_values_file_level_for_bug_id(ranks, K, bug_id):
	hit_K = calculate_hitK(ranks, K)
	return hit_K


# Calculate hit@K
def calculate_hitK(ranks, K):
	hit = 0
	for rank in ranks:
		if rank <= K:
			hit = 1 
			break
	return hit


def calulate_file_metrics_for_all_K(rankList, bug_report_ids, K_values):
	hit_list = []

	for i in range(len(bug_report_ids)):
		ranks = rankList[i]
		bug_id = bug_report_ids[i]

		hit_K_values = []
		for k in K_values:
			hit_K= calculate_final_metric_values_file_level_for_bug_id(ranks, k, bug_id)
			hit_K_values.append(hit_K)

		java_file_count = get_java_file_count(bug_id)
		hit_K = calculate_final_metric_values_file_level_for_bug_id(ranks, java_file_count, bug_id)
		hit_K_values.append(hit_K)
		hit_list.append(hit_K_values)

	return hit_list

def get_file_content(file_name):
	# Read the file
	file_content = open(file_name, "r")
	file_content = file_content.read()
	return file_content

def remove_ranks_blank_text(bug_id, query_reformulation_gui, col_name, screen, prep_query_dataset, prepocessed_data_dir):
	query_reformulation_type_name = ""
	if col_name=="Ranks (Query-Bug Report)" or col_name=="Ranks-unsorted (Query-Bug Report)" or col_name=="Files (Query-Bug Report)":
		query_reformulation_type_name = "bug_report_original"
	elif col_name=="Ranks (Query Replacement)" or col_name=="Ranks-unsorted (Query Replacement)" or col_name=="Files (Query Replacement)":
		query_reformulation_type_name = "replaced_query"
	elif col_name=="Ranks (Query Expansion 1)" or col_name=="Ranks-unsorted (Query Expansion 1)" or col_name=="Files (Query Expansion 1)":
		query_reformulation_type_name = "query_expansion_1"

	bug_report_contents_file = prepocessed_data_dir + "/" + prep_query_dataset + "/Screen-" + screen + "/Preprocessed_with_" + query_reformulation_gui + "/" + query_reformulation_type_name + "/bug_report_" + bug_id + ".txt"

	bug_report_contents = get_file_content(bug_report_contents_file)
	if bug_report_contents is None or len(bug_report_contents)<1:
		return True

	return False

def get_ranks(bug_id, filename, query_reformulation_gui, col_name, screen, prep_query_dataset, prepocessed_data_dir):
	ranklist_df = pd.read_csv(filename)
	if not ranklist_df['Bug Report ID'].isin([int(bug_id)]).any():
		print(f'Bug Id: {bug_id} does not exist in {filename}')
	ranks_for_bug_id = ranklist_df.loc[ranklist_df['Bug Report ID']==int(bug_id), col_name].values.tolist()
	if ranks_for_bug_id is None or len(ranks_for_bug_id)<1 or ranks_for_bug_id!=ranks_for_bug_id:
		return "[]"
	if remove_ranks_blank_text(bug_id, query_reformulation_gui, col_name, screen, prep_query_dataset, prepocessed_data_dir):
		return "[]"
	return ranks_for_bug_id[0]

def get_ranklist(bug_report_ids, filename, query_reformulation_gui, col_name, screen, prep_query_dataset, prepocessed_data_dir):
	ranklist = []
	identified_bugs_count = 0
	for bug_id in bug_report_ids:
		ranks = get_ranks(bug_id, filename, query_reformulation_gui, col_name, screen, prep_query_dataset, prepocessed_data_dir)
		if ranks is None or ranks!=ranks:
			ranklist.append([])
		else:
			ranklist.append(literal_eval(ranks))
			if len(literal_eval(ranks))>0:
				identified_bugs_count += 1
	return identified_bugs_count, ranklist

def get_buggy_files_for_lucene(bug_report_ids, filename, query_reformulation_gui, col_name, screen, prep_query_dataset, prepocessed_data_dir):
	ranklist = []
	for bug_id in bug_report_ids:
		ranks = get_ranks(bug_id, filename, query_reformulation_gui, col_name, screen, prep_query_dataset, prepocessed_data_dir)
		if ranks is None or ranks!=ranks:
			ranklist.append([])
		else:
			ranklist.append(list(filter(None,re.split(r"[\[\], ]", ranks))))
			#print(ranklist)
	return ranklist

def get_bug_report_ids():
	bug_report_ids = ["2", "8", "10", "11", 
                "18", "19", "44", "45", "53", "54", "55", "56", "71", "76", "84", "87", "92", "106", "110",
                "117", "128", "129", "130", "135", "158", "159", "160", "162", "168", "191", "192", "193",
                "199", "200", "201", "206", "209", "227", "248", "256", "271", "275", "1028", "1073", 
                "1089", "1096", "1130", "1146", "1147", "1150", "1151", "1198", "1202", "1205", "1207",
                "1213", "1214", "1215", "1222", "1223", "1224", "1228", "1299", "1389", "1399", "1402",
                "1403", "1406", "1425", "1428", "1430", "1441", "1445", "1446", "1481", "1563", "1568", 
                "1640", "1641", "1645"]
	return bug_report_ids

def total_number_of_ranked_files(ranklist):
	len_ranks_list = get_ranklist_len(ranklist)
	return np.sum(len_ranks_list)

def get_average_metrics(metrics):
	metric_values = [np.array(item) for item in metrics]
	return [np.mean(m_val) for m_val in zip(*metric_values)]

def get_result_row(hit_list, bug_report_ids):
	hit = get_average_metrics(hit_list)

	number_of_hits_10=0
	hit_10_list=[]
	for i in range(len(hit_list)):
		if hit_list[i][2]==1:
			number_of_hits_10+=1
			hit_10_list.append(bug_report_ids[i])

	result_row = []
	result_row.append(hit[2])
	result_row.append(number_of_hits_10)
	return result_row

def metrics_result(rankList, bug_report_ids, K_values):
	hit_list = calulate_file_metrics_for_all_K(rankList, bug_report_ids, K_values)
	mertic_values = get_result_row(hit_list, bug_report_ids)
	return mertic_values

def write_to_ranks_file_baseline(filename, bug_report_ids, ranklist):
	for i in range(len(bug_report_ids)):
		write_to_csv(filename, [bug_report_ids[i], ranklist[i]])

def write_to_ranks_file_baseline_filtering_boosting(filename, bug_report_ids, ranklist_br, rank_col_rq,
	rank_col_qe1, rank_col_qe2, rank_col_qe3):
	for i in range(len(bug_report_ids)):
		write_to_csv(filename, [bug_report_ids[i], ranklist_br[i], 
			rank_col_rq[i], rank_col_qe1[i], rank_col_qe2[i], rank_col_qe3[i]])

def get_filename(result_dir, screens, operations, filtering_gui, boosting_gui, query_reformulation_gui):
	final_ranks_file = ""
	if operations == "Filtering":
		final_ranks_file = result_dir + "/" + operations + "#Screen-" + screens + "#Filtering-" + filtering_gui + "#Query_Reformulation-" + query_reformulation_gui + ".csv"
	elif operations=="Boosting":
		final_ranks_file = result_dir + "/" + operations + "#Screen-" + screens + "#Boosting-" + boosting_gui + "#Query_Reformulation-" + query_reformulation_gui + ".csv"
	elif operations=="Filtering+Boosting":
		final_ranks_file = result_dir + "/" + operations + "#Screen-" + screens + "#Filtering-" + filtering_gui + "#Boosting-" + boosting_gui + "#Query_Reformulation-" + query_reformulation_gui + ".csv"
	elif operations=="QueryReformulation":
		final_ranks_file = result_dir + "/" + operations + "#Screen-" + screens + "#Query_Reformulation-" + query_reformulation_gui + ".csv"
	return final_ranks_file

# This function will delete rank such as 0 from the list. This case happens for Lucene. 
# When a buggy file exist in the corpus but Lucene cannot identify it this case happens.
def remove_invalid_ranks(rankList_query, rankList_unsorted_query, rankList_buggy_files):
	filtered_ranklist = []
	filtered_ranklist_unsorted = []
	filtered_ranklist_buggy_files = []

	for i in range(len(rankList_unsorted_query)):
		if rankList_unsorted_query[i]!=0:
			filtered_ranklist_unsorted.append(rankList_unsorted_query[i])
			filtered_ranklist_buggy_files.append(rankList_buggy_files[i])

	for ranks in rankList_query:
		filtered_ranklist.append(list(filter(lambda item: item!=0, ranks)))

	return filtered_ranklist, filtered_ranklist_unsorted, filtered_ranklist_buggy_files

def write_header_for_approach_rankings(filename):
	os.makedirs(os.path.dirname(filename), exist_ok=True)
	with open(filename, 'w') as file:
		writer = csv.writer(file)
		writer.writerow(["Task", "GUI Info for Filtering", "GUI Info for Boosting", "GUI Info for Query Expansion", "GUI Info for Query Replacement", "Number of Screens",
					"Number of Identified Bugs", "Number of identified buggy files", 
					"Hit@10", "Number of hits@10"])

def compute_ranklist_for_bug_report_ids(result_dir, operation, screen, filtering_gui, boosting_gui, query_reformulation_gui, 
	bug_report_ids, ref_type, reformulation_unsorted_rank_type, files_col_name, prep_query_dataset, approach_name, prepocessed_data_dir):
	filename = get_filename(result_dir, screen, operation, filtering_gui, boosting_gui, query_reformulation_gui)
	print(filename)
	identified_bugs_count, rankList_query = get_ranklist(bug_report_ids, filename, query_reformulation_gui, ref_type, screen, prep_query_dataset, prepocessed_data_dir)
	_, rankList_unsorted_query = get_ranklist(bug_report_ids, filename, query_reformulation_gui, reformulation_unsorted_rank_type, screen, prep_query_dataset, prepocessed_data_dir)
	
	rankList_buggy_files = []
	if approach_name!="Lucene":
		_, rankList_buggy_files = get_ranklist(bug_report_ids, filename, query_reformulation_gui, files_col_name, screen, prep_query_dataset, prepocessed_data_dir)
	else:
		rankList_buggy_files = get_buggy_files_for_lucene(bug_report_ids, filename, query_reformulation_gui, files_col_name, screen, prep_query_dataset, prepocessed_data_dir)

	rankList_query, rankList_unsorted_query, rankList_buggy_files = remove_invalid_ranks(rankList_query, rankList_unsorted_query, rankList_buggy_files)

	return identified_bugs_count, rankList_query, rankList_unsorted_query, rankList_buggy_files

def ranks_header(filename):
	os.makedirs(os.path.dirname(filename), exist_ok=True)
	with open(filename, 'w') as file:
		writer = csv.writer(file)
		writer.writerow(["Bug Report ID", "Ranks-unsorted", "Ranks", "Files"])

def write_ranks_for_each_config(ranks_folder, filename_info, bug_report_ids, rankList_unsorted, rankList, rankList_buggy_files):
	result_file = ranks_folder + "/" + filename_info[0] + "#Filtering-" + filename_info[1] + "#Boosting-" + filename_info[2] + "#Query_Expansion-" + filename_info[3] + "#Query_Replacement-" + filename_info[4] + "#Screen-" + filename_info[5] + ".csv"
	ranks_header(result_file)

	for i in range(len(bug_report_ids)):
		ranks_row = []
		ranks_row.append(bug_report_ids[i])
		ranks_row.append(rankList_unsorted[i])
		ranks_row.append(rankList[i])
		ranks_row.append(rankList_buggy_files[i])
		write_to_csv(result_file, ranks_row)

def file_ranks_header(filename):
	os.makedirs(os.path.dirname(filename), exist_ok=True)
	with open(filename, 'w') as file:
		writer = csv.writer(file)
		writer.writerow(["Bug Report ID", "File", "Rank"])

def write_individual_files_ranks(file_ranks_folder, filename_info, bug_report_ids, rankList_unsorted, rankList_buggy_files):
	result_file = file_ranks_folder + "/" + filename_info[0] + "#Filtering-" + filename_info[1] + "#Boosting-" + filename_info[2] + "#Query_Expansion-" + filename_info[3] + "#Query_Replacement-" + filename_info[4] + "#Screen-" + filename_info[5] + ".csv"
	file_ranks_header(result_file)

	for i in range(len(bug_report_ids)):
		for j in range(len(rankList_unsorted[i])):
			rank_row = []
			rank_row.append(bug_report_ids[i])
			rank_row.append(rankList_buggy_files[i][j])
			rank_row.append(rankList_unsorted[i][j])
			write_to_csv(result_file, rank_row)

def get_result_for_each_row(operation,filtering_gui, boosting_gui, query_reformulation_gui, screen, 
	reformulation_rank_type, reformulation_unsorted_rank_type, files_col_name, reformulation_type, result_dir, final_ranks_folder, file_ranks_folder, approach_name, prepocessed_data_dir):
	K_values = [1, 5, 10]
	bug_report_ids = get_bug_report_ids()
	all_bug_report_ids = bug_report_ids

	row = []
	if filtering_gui=="" and boosting_gui=="" and reformulation_type == "BR":
		row.append("Baseline")
		row.append("")
		row.append("")
		row.append("")
		row.append("")
		row.append("")
	else:
		row.append(operation)

		if filtering_gui=="":
			row.append("NO")
		else:
			row.append(filtering_gui)

		if boosting_gui=="":
			row.append("NO")
		else:
			row.append(boosting_gui)

		if reformulation_type == "QE":
			row.append(query_reformulation_gui)
			row.append("None")
		elif reformulation_type == "QR":
			row.append("None")
			row.append(query_reformulation_gui)
		elif reformulation_type == "BR":
			row.append("None")
			row.append("None")

		if screen=="":
			row.append("NA")
		else:
			row.append(screen)

	filename_info = row

	identified_bugs_count_1st, rankList_query_1st, rankList_unsorted_query_1st, rankList_buggy_files_1st = compute_ranklist_for_bug_report_ids(result_dir, operation, screen, filtering_gui, 
		boosting_gui, query_reformulation_gui, bug_report_ids, reformulation_rank_type, reformulation_unsorted_rank_type, files_col_name, "PreprocessedBugReports", approach_name, prepocessed_data_dir)

	rankList_query = rankList_query_1st

	rankList_unsorted_query = rankList_unsorted_query_1st

	rankList_buggy_files = rankList_buggy_files_1st
	write_ranks_for_each_config(final_ranks_folder, filename_info, all_bug_report_ids, rankList_unsorted_query, rankList_query, rankList_buggy_files)
	write_individual_files_ranks(file_ranks_folder, filename_info, all_bug_report_ids, rankList_unsorted_query, rankList_buggy_files)

	total_identified_bugs = identified_bugs_count_1st
	total_ranked_files = total_number_of_ranked_files(rankList_query)
	metric_values = metrics_result(rankList_query, all_bug_report_ids, K_values)

	row.append(total_identified_bugs)
	row.append(total_ranked_files)
	row.extend(metric_values)
	return row

def main():
	approach_name = "Lucene" # BugLocator or Lucene or SentenceBERT or UniXCoder
	data_dir = "/Users/sagelab/Documents/Projects/BugLocalization/Artifact-ICSE24/GUI-Bug-Localization-Data"
	package_dir = "/Users/sagelab/Documents/Projects/BugLocalization/Artifact-ICSE24/UI-Bug-Localization-Study"

	prepocessed_data_dir = data_dir + "/PreprocessedData"
	
	result_dir = package_dir + "/Results/" + approach_name 
	calc_dir = package_dir + "/Results/Lucene/OtherResults"
	final_ranks_folder = calc_dir + "/RanksAll/" + approach_name 
	file_ranks_folder = calc_dir + "/FileRanksAll/" + approach_name
	
	screen_list=["4"]
	filtering_list=["GUI_States", "GUI_State_and_All_GUI_Component_IDs"]
	boosting_list=["GUI_States"]
	query_reformulation_list=["GUI_States"]
	reformulation_types =["Ranks (Query-Bug Report)", "Ranks (Query Replacement)", "Ranks (Query Expansion 1)"]
	reformulation_cols = ["BR", "QR", "QE"]

	metric_file = calc_dir + "/MetricsAll/" + approach_name + "Results.csv"
	write_header_for_approach_rankings(metric_file)

	#Filtering
	for filtering_gui in filtering_list:
		for screen in screen_list:
			row = get_result_for_each_row("Filtering",filtering_gui, "", "GUI_States", screen, "Ranks (Query-Bug Report)", "Ranks-unsorted (Query-Bug Report)", "Files (Query-Bug Report)",
						"BR", result_dir, final_ranks_folder, file_ranks_folder, approach_name, prepocessed_data_dir)
			write_to_csv(metric_file, row)
	for query_reformulation_gui in query_reformulation_list:
		for filtering_gui in filtering_list:
			for screen in screen_list:
				row = get_result_for_each_row("Filtering",filtering_gui, "", query_reformulation_gui, screen, "Ranks (Query Expansion 1)", "Ranks-unsorted (Query Expansion 1)", "Files (Query Expansion 1)",
					"QE", result_dir, final_ranks_folder, file_ranks_folder, approach_name, prepocessed_data_dir)
				write_to_csv(metric_file, row)
	for query_reformulation_gui in query_reformulation_list:
		for filtering_gui in filtering_list:
			for screen in screen_list:
				row = get_result_for_each_row("Filtering",filtering_gui, "", query_reformulation_gui, screen, "Ranks (Query Replacement)", "Ranks-unsorted (Query Replacement)", "Files (Query Replacement)",
					"QR", result_dir, final_ranks_folder, file_ranks_folder, approach_name, prepocessed_data_dir)
				write_to_csv(metric_file, row)

	#Boosting
	for boosting_gui in boosting_list:
		for screen in screen_list:
			row = get_result_for_each_row("Boosting","", boosting_gui, "GUI_States", screen, "Ranks (Query-Bug Report)", "Ranks-unsorted (Query-Bug Report)", "Files (Query-Bug Report)",
						"BR", result_dir, final_ranks_folder, file_ranks_folder, approach_name, prepocessed_data_dir)
			write_to_csv(metric_file, row)
	for query_reformulation_gui in query_reformulation_list:
		for boosting_gui in boosting_list:
			for screen in screen_list:
				row = get_result_for_each_row("Boosting","", boosting_gui, query_reformulation_gui, screen, "Ranks (Query Expansion 1)", "Ranks-unsorted (Query Expansion 1)", "Files (Query Expansion 1)",
					"QE", result_dir, final_ranks_folder, file_ranks_folder, approach_name, prepocessed_data_dir)
				write_to_csv(metric_file, row)
	for query_reformulation_gui in query_reformulation_list:
		for boosting_gui in boosting_list:
			for screen in screen_list:
				row = get_result_for_each_row("Boosting","", boosting_gui, query_reformulation_gui, screen, "Ranks (Query Replacement)", "Ranks-unsorted (Query Replacement)", "Files (Query Replacement)",
					"QR", result_dir, final_ranks_folder, file_ranks_folder, approach_name, prepocessed_data_dir)
				write_to_csv(metric_file, row)

	#For Filtering+Boosting
	for i in range(2, len(filtering_list)):
		for l in range(len(screen_list)):
			boosting_gui_type=[]
			index = 0
			for j in range(len(boosting_list)):
				if index < i:
					boosting_gui_type.append(boosting_list[j])
					index+=1
				else:
					break
			for j in range(len(boosting_gui_type)):
				row = get_result_for_each_row("Filtering+Boosting", filtering_list[i], boosting_gui_type[j], "GUI_States", screen_list[l], "Ranks (Query-Bug Report)", "Ranks-unsorted (Query-Bug Report)", "Files (Query-Bug Report)",
						"BR", result_dir, final_ranks_folder, file_ranks_folder, approach_name, prepocessed_data_dir)
				write_to_csv(metric_file, row)

	for k in range(len(query_reformulation_list)):
		for i in range(2, len(filtering_list)):
			for l in range(len(screen_list)):
				boosting_gui_type=[]
				index = 0
				for j in range(len(boosting_list)):
					if index < i:
						boosting_gui_type.append(boosting_list[j])
						index+=1
					else:
						break
				for j in range(len(boosting_gui_type)):
					row = get_result_for_each_row("Filtering+Boosting", filtering_list[i], boosting_gui_type[j], query_reformulation_list[k], 
					screen_list[l], "Ranks (Query Expansion 1)", "Ranks-unsorted (Query Expansion 1)", "Files (Query Expansion 1)", "QE", result_dir, final_ranks_folder, file_ranks_folder, approach_name, prepocessed_data_dir)
					write_to_csv(metric_file, row)

	for k in range(len(query_reformulation_list)):
		for i in range(2, len(filtering_list)):
			for l in range(len(screen_list)):
				boosting_gui_type=[]
				index = 0
				for j in range(len(boosting_list)):
					if index < i:
						boosting_gui_type.append(boosting_list[j])
						index+=1
					else:
						break
				for j in range(len(boosting_gui_type)):
					row = get_result_for_each_row("Filtering+Boosting", filtering_list[i], boosting_gui_type[j], query_reformulation_list[k], 
					screen_list[l], "Ranks (Query Replacement)", "Ranks-unsorted (Query Replacement)", "Files (Query Replacement)", "QR", result_dir, final_ranks_folder, file_ranks_folder, approach_name, prepocessed_data_dir)
					write_to_csv(metric_file, row)

	# For query_reformulation
	for l in range(len(screen_list)):
		row = get_result_for_each_row("QueryReformulation","", "", "GUI_States", screen_list[l], "Ranks (Query-Bug Report)", "Ranks-unsorted (Query-Bug Report)", "Files (Query-Bug Report)",
						"BR", result_dir, final_ranks_folder, file_ranks_folder, approach_name, prepocessed_data_dir)
		write_to_csv(metric_file, row)	
	for k in range(len(query_reformulation_list)):
		for l in range(len(screen_list)):
			row = get_result_for_each_row("QueryReformulation","", "", query_reformulation_list[k], screen_list[l], "Ranks (Query Expansion 1)", "Ranks-unsorted (Query Expansion 1)", "Files (Query Expansion 1)",
					"QE", result_dir, final_ranks_folder, file_ranks_folder, approach_name, prepocessed_data_dir)
			write_to_csv(metric_file, row)	
	for k in range(len(query_reformulation_list)):
		for l in range(len(screen_list)):
			row = get_result_for_each_row("QueryReformulation","", "", query_reformulation_list[k], screen_list[l], "Ranks (Query Replacement)", "Ranks-unsorted (Query Replacement)", "Files (Query Replacement)",
					"QR", result_dir, final_ranks_folder, file_ranks_folder, approach_name, prepocessed_data_dir)
			write_to_csv(metric_file, row)	

if __name__ == "__main__":
	main()
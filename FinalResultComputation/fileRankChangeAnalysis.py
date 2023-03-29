import pandas as pd
import csv
import numpy as np
import os
from ast import literal_eval

def write_to_csv(write_file, row):
	with open(write_file, 'a') as file:
		writer = csv.writer(file)
		writer.writerow(row)

def get_best_config_file_rank(bug_id, buggy_file, best_config_file):
	ranklist_df = pd.read_csv(best_config_file)
	rank = ranklist_df.loc[(ranklist_df['Bug Report ID']==int(bug_id)) & (ranklist_df['File']==buggy_file), "Rank"].values.tolist()
	if rank is None or len(rank)<1 or rank !=rank :
		return -1
	return int(rank[0])

def analyze_ranks(bug_ids, baseline_ranks, best_config_ranks):
	number_of_lost_files = sum(1 for x,y in zip(baseline_ranks, best_config_ranks) if x==-1 or y==-1)
	number_of_improved_ranks = sum(1 for x,y in zip(baseline_ranks, best_config_ranks) if x>y and x!=-1 and y!=-1)
	number_of_deteriorated_ranks = sum(1 for x,y in zip(baseline_ranks, best_config_ranks) if x<y and x!=-1 and y!=-1)
	number_of_unchanged_ranks = sum(1 for x,y in zip(baseline_ranks, best_config_ranks) if x==y and x!=-1 and y!=-1)

	number_of_ranks_out10_to_in10 = sum(1 for x,y in zip(baseline_ranks, best_config_ranks) if x>10 and y<=10 and x!=-1 and y!=-1)
	number_of_ranks_in10_to_out10 = sum(1 for x,y in zip(baseline_ranks, best_config_ranks) if x<=10 and y>10 and x!=-1 and y!=-1)

	number_of_ranks_inside10_improved = sum(1 for x,y in zip(baseline_ranks, best_config_ranks) if x<=10 and y<=10 and x>y and x!=-1 and y!=-1)
	number_of_ranks_inside10_deteriorated = sum(1 for x,y in zip(baseline_ranks, best_config_ranks) if x<=10 and y<=10 and x<y and x!=-1 and y!=-1)
	number_of_ranks_inside10_unchanged = sum(1 for x,y in zip(baseline_ranks, best_config_ranks) if x<=10 and y<=10 and x==y and x!=-1 and y!=-1)

	number_of_ranks_outside10_improved = sum(1 for x,y in zip(baseline_ranks, best_config_ranks) if x>10 and y>10 and x>y and x!=-1 and y!=-1)
	number_of_ranks_outside10_deteriorated = sum(1 for x,y in zip(baseline_ranks, best_config_ranks) if x>10 and y>10 and x<y and x!=-1 and y!=-1)
	number_of_ranks_outside10_unchanged = sum(1 for x,y in zip(baseline_ranks, best_config_ranks) if x>10 and y>10 and x==y and x!=-1 and y!=-1)

	bug_ids_improved = []
	for i in range(len(baseline_ranks)):
		if baseline_ranks[i]>best_config_ranks[i] and baseline_ranks[i]>10 and best_config_ranks[i]<=10 and best_config_ranks[i]!=-1:
			bug_ids_improved.append(bug_ids[i])

	return [number_of_lost_files, number_of_improved_ranks, number_of_deteriorated_ranks, number_of_unchanged_ranks,
		number_of_ranks_out10_to_in10, number_of_ranks_in10_to_out10, number_of_ranks_inside10_improved, 
		number_of_ranks_inside10_deteriorated, number_of_ranks_inside10_unchanged, number_of_ranks_outside10_improved,
		number_of_ranks_outside10_deteriorated, number_of_ranks_outside10_unchanged, bug_ids_improved]


def get_file_analysis(filename, best_config_file):
	baseline_df = pd.read_csv(filename)
	
	baseline_ranks = []
	best_config_ranks = []
	for _, row in baseline_df.iterrows():
		baseline_rank = row['Rank']
		best_config_rank = get_best_config_file_rank(row['Bug Report ID'], row['File'], best_config_file)
		baseline_ranks.append(baseline_rank)
		best_config_ranks.append(best_config_rank)

		#print(f"File: {row['File']} {baseline_rank} {best_config_rank}")

	return analyze_ranks(baseline_ranks, best_config_ranks)

def get_ranks(bug_id, filename, col_name):
	ranklist_df = pd.read_csv(filename)
	if not ranklist_df['Bug Report ID'].isin([int(bug_id)]).any():
		print(f'Bug Id: {bug_id} does not exist in {filename}')
	ranks_for_bug_id = ranklist_df.loc[ranklist_df['Bug Report ID']==int(bug_id), col_name].values.tolist()
	if ranks_for_bug_id is None or len(ranks_for_bug_id)<1 or ranks_for_bug_id!=ranks_for_bug_id:
		return "[]"
	return ranks_for_bug_id[0]

def get_bug_report_ids():
	bug_report_ids = ["2", "8", "10", "18", "19", "44",
					"53", "117", "128", "129", "130",
					"135", "191", "206", "209", "256",
					"1073", 
					"1202", "1205", "1207",
					"1214", "1215", "1224",
					"1299", "1399", "1430", "1441",
					"1445", "1481", "54", "76", "92", "158", "160", "162", 
					 "192", "199", "200", "248", "1198", "1228",
					"1389", "1425", "1446", "1563", "1568",
					"11", "55", "56", "227", "1213", "1222", "1428",
					"84", "87", "159", "193", "275", "1028", "1089", "1130", "1402", "1403",
					"71", "201", "1641",
					"1096", "1146", "1147", "1151", "1223", "1645", "106", "110", "168", "271",
					"1406", "45", "1640",
					"1150"]
	return bug_report_ids

# Calculate hit@K
def calculate_hitK(ranks, K):
	hit = 0
	for rank in ranks:
		if rank <= K:
			hit = 1 
			break
	return hit

def get_average_hit(ranks):
	K_values = [1,5,10]
	hit_list = []
	for k in K_values:
		hit_k = calculate_hitK(ranks, k)
		hit_list.append(hit_k)
	return np.mean(hit_list)

# def get_bug_analysis(baseline_file, best_config_file):
# 	bug_report_ids = get_bug_report_ids()

# 	number_of_improved_bugs = 0
# 	number_of_deteriorated_bugs = 0
# 	number_of_unchanged_bugs = 0

# 	for i in range(len(bug_report_ids)):
# 		baseline_ranks = get_ranks(bug_report_ids[i], baseline_file, "Ranks")
# 		best_config_ranks = get_ranks(bug_report_ids[i], best_config_file, "Ranks")
# 		#print(f"{bug_report_ids[i]} {baseline_ranks} {best_config_ranks}")

# 		baseline_avg_hit = get_average_hit(literal_eval(baseline_ranks))
# 		best_config_avg_hit = get_average_hit(literal_eval(best_config_ranks))
		
# 		if baseline_avg_hit > best_config_avg_hit:
# 			number_of_improved_bugs += 1
# 		elif baseline_avg_hit < best_config_avg_hit:
# 			number_of_deteriorated_bugs += 1
# 		elif baseline_avg_hit == best_config_avg_hit:
# 			number_of_unchanged_bugs +=1

# 	return [number_of_improved_bugs, number_of_deteriorated_bugs, number_of_unchanged_bugs]

def write_qual_analysis_header(filename):
	os.makedirs(os.path.dirname(filename), exist_ok=True)
	with open(filename, 'w') as file:
		writer = csv.writer(file)
		writer.writerow(["Approach", "Config", "#Not Retrieved Bugs (Top Buggy File)", "#Bugs (Top Buggy File) Improved", 
		"#Bugs (Top Buggy File) Deteriorated", "#Bugs (Top Buggy File) Unchanged", "#Bugs (Top Buggy File) Ranks (Out10 to In10)",
		"#Bugs (Top Buggy File) (In10 to Out10)", "#Bugs (Top Buggy File) Inside 10 Improved", "#Bugs (Top Buggy File) Inside 10 Deteriorated", 
		"#Bugs (Top Buggy File) Inside 10 Unchanged",
		"#Bugs (Top Buggy File) Outside 10 Improved", "#Bugs (Top Buggy File) Outside 10 Deteriorated", "#Bugs (Top Buggy File) Outside 10 Unchanged", "Bug Ids Improved"])

def get_top_ranked_file_with_rank(bug_id, filename):
	ranklist_df = pd.read_csv(filename)
	rankList = ranklist_df.loc[(ranklist_df['Bug Report ID']==int(bug_id)), ("File", "Rank")].values.tolist()
	if rankList is None or len(rankList)<1 or rankList != rankList :
		return -1
	rankList.sort(key=lambda x:int(x[1]))
	return rankList[0]

def get_bug_analysis(baseline_file, best_config_file):
	bug_report_ids = get_bug_report_ids()
	
	baseline_ranks = []
	best_config_ranks = []
	bug_ids = []
	for i in range(len(bug_report_ids)):
		baseline_top_filerank = get_top_ranked_file_with_rank(bug_report_ids[i], baseline_file)
		
		#best_config_rank = get_best_config_file_rank(bug_report_ids[i], baseline_top_filerank[0], best_config_file)
		best_config_rank = get_top_ranked_file_with_rank(bug_report_ids[i], best_config_file)
		bug_ids.append(bug_report_ids[i])
		if baseline_top_filerank == -1:
			baseline_ranks.append(-1)
		else:
			baseline_ranks.append(baseline_top_filerank[1])
		
		if best_config_rank == -1:
			best_config_ranks.append(-1)
		else:
			best_config_ranks.append(best_config_rank[1])
	return analyze_ranks(bug_ids,baseline_ranks, best_config_ranks)

def get_best_config_files(filename):
	df = pd.read_csv(filename)
	config_file_list = []
	for index, row in df.iterrows():
		config_file = row['Task']+"#Filtering-"+row['GUI Info for Filtering']+"#Boosting-"+row['GUI Info for Boosting'] + "#Query_Expansion-" + row['GUI Info for Query Expansion'] + "#Query_Replacement-" + row['GUI Info for Query Replacement'] + "#Screen-" + str(row['Number of Screens']) + ".csv"
		config_file_list.append(config_file)

	return config_file_list


def main():
	file_rank_dir = "FinalResults/FileRanksAll"
	# general_rank_dir = "FinalResults/RanksAll"
	qual_analysis_file = "FinalResults/QualitativeAnalysis/QualitativeAnalysis-Out10toIn10-2.csv"
	write_qual_analysis_header(qual_analysis_file)

	baseline_default_file = "QueryReformulation#Filtering-NO#Boosting-NO#Query_Expansion-None#Query_Replacement-None#Screen-2.csv" # Ranks col: Ranks-unsorted (Query-Bug Report) // Files col: (Query-Bug Report)

	buglocator_best_among_all_config_files = "FinalResults/BestAmongAllConfigResults/BugLocatorBestConfigResults.csv"
	buglocator_best_config_files = get_best_config_files(buglocator_best_among_all_config_files)

	for buglocator_config in buglocator_best_config_files:
		buglocator_row = ["BugLocator"]
		buglocator_row.append(buglocator_config)
		buglocator_row.extend(get_bug_analysis(file_rank_dir + "/BugLocator/" + baseline_default_file, file_rank_dir + "/BugLocator/" + buglocator_config))
		#buglocator_row.extend(get_file_analysis(file_rank_dir + "/BugLocator/" + baseline_default_file, file_rank_dir + "/BugLocator/" + buglocator_best_config_file))
		write_to_csv(qual_analysis_file, buglocator_row)

	lucene_best_among_all_config_files = "FinalResults/BestAmongAllConfigResults/LuceneBestConfigResults.csv"
	lucene_best_config_files = get_best_config_files(lucene_best_among_all_config_files)

	for lucene_config in lucene_best_config_files:
		lucene_row = ["Lucene"]
		lucene_row.append(lucene_config)
		lucene_row.extend(get_bug_analysis(file_rank_dir + "/Lucene/" + baseline_default_file, file_rank_dir + "/Lucene/" + lucene_config))
		write_to_csv(qual_analysis_file, lucene_row)
	
	sentencebert_best_among_all_config_files = "FinalResults/BestAmongAllConfigResults/SentenceBERTBestConfigResults.csv"
	sentencebert_best_config_files = get_best_config_files(sentencebert_best_among_all_config_files)

	for sentencebert_config in sentencebert_best_config_files:
		sentencebert_row = ["SentenceBERT"]
		sentencebert_row.append(sentencebert_config)
		sentencebert_row.extend(get_bug_analysis(file_rank_dir + "/SentenceBERT/" + baseline_default_file, file_rank_dir + "/SentenceBERT/" + sentencebert_config))
		write_to_csv(qual_analysis_file, sentencebert_row)

	unixcoder_best_among_all_config_files = "FinalResults/BestAmongAllConfigResults/UniXCoderBestConfigResults.csv"
	unixcoder_best_config_files = get_best_config_files(unixcoder_best_among_all_config_files)

	for unixcoder_config in unixcoder_best_config_files:
		unixcoder_row = ["UniXCoder"]
		unixcoder_row.append(unixcoder_config)
		print(unixcoder_config)
		unixcoder_row.extend(get_bug_analysis(file_rank_dir + "/UniXCoder/" + baseline_default_file, file_rank_dir + "/UniXCoder/" + unixcoder_config))
		write_to_csv(qual_analysis_file, unixcoder_row)

if __name__ == "__main__":
	main()


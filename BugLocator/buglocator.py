#!/usr/bin/python3
# https://openwritings.net/pg/python/python-how-write-xml-file

import xml.etree.ElementTree as ET
from xml.dom import minidom
import os
import re
import json
import csv
from bs4 import BeautifulSoup
import glob
import argparse
import pandas as pd
import time

def read_file_content(file_name):
	# Read the file
	file_content = open(file_name, "r")
	file_content = file_content.read()
	return file_content

def write_to_csv(write_file, row):
	with open(write_file, 'a') as file:
		writer = csv.writer(file)
		writer.writerow(row)

def create_file_path(file):
	#https://stackoverflow.com/questions/12517451/automatically-creating-directories-with-file-output
	os.makedirs(os.path.dirname(file), exist_ok=True)

def get_ranked_files(bug_id, filename):
	file_list_df = pd.read_csv(filename)
	files_for_bug_id = file_list_df.loc[file_list_df['Bug Report ID']==int(bug_id), 'FilePaths'].values.tolist()

	return files_for_bug_id

def get_filtered_files(bug_issue_id, filtered_files_stored_file):
	filtered_files = get_ranked_files(bug_issue_id, filtered_files_stored_file)

	return filtered_files

def create_record_file_header(record_existence_file):
	create_file_path(record_existence_file)
	with open(record_existence_file, 'w') as file:
		writer = csv.writer(file)
		writer.writerow(["Bug_Id", "File", "Filenames_Store_File", "Stored"])

def check_if_file_exist(file, bug_id, filenames_store_file, subpath):
	record_existence_file = "existence/" + subpath + "/bug-" + bug_id + ".csv"

	if not os.path.exists(record_existence_file):
		create_record_file_header(record_existence_file)
	elif os.path.exists(record_existence_file):
		record_df = pd.read_csv(record_existence_file)
		file_exist = record_df.loc[(record_df['Bug_Id']==int(bug_id)) & (record_df['File']==file) 
				 & (record_df['Filenames_Store_File']==filenames_store_file), 'Stored'].values.tolist()
		if len(file_exist)>0:
			if file_exist[0]=="Exist":
				return True
			if file_exist[0]=="NotExist":
				return False
		
	filenameList = get_ranked_files(bug_id, filenames_store_file)
	
	for filename in filenameList:
		if filename.endswith(file):
			write_to_csv(record_existence_file, [bug_id, file, filenames_store_file, "Exist"])
			return True
	write_to_csv(record_existence_file, [bug_id, file, filenames_store_file, "NotExist"])
	return False

def remove_java_files_if_not_exist(bug_id, filenames_store_file, temp_xml_dir, xml_file, subpath, filetype):
	with open(xml_file, 'r') as f:
		data = f.read()
	 
	Bs_data = BeautifulSoup(data, "xml")
	b_unique = Bs_data.find_all('file')
	
	not_existed_file = []
	for item in b_unique:
		filename_without_extension = os.path.splitext(item.text)[0]
		if bug_id=="45":
			filename_without_extension = "it.feio.android.omninotes.helpers/GeocodeProviderBaseFactory"
		else:
			filename_without_extension = filename_without_extension.replace(".","/")
		filename_with_extension = filename_without_extension + ".java"

		if not check_if_file_exist(filename_with_extension, bug_id, filenames_store_file, subpath):
			not_existed_file.append(item.text)

	buggy_file_cnt = 0
	oldxmlfile = ET.parse(xml_file)
	root = oldxmlfile.getroot()
	# https://stackoverflow.com/questions/37335943/removing-xml-subelement-tags-with-python-using-elementtree-and-remove
	for elem in root.iter():
		for child in list(elem):
			if child.tag == 'file':
				buggy_file_cnt+=1
				if child.text in not_existed_file:
					elem.remove(child)

	if buggy_file_cnt-len(not_existed_file)==0:
		return False, ""
	temp_xml_file_path = temp_xml_dir + "/" + subpath + "/"+ filetype + "/" + "bug_" + bug_id + ".xml"
	create_file_path(temp_xml_file_path)
	oldxmlfile.write(temp_xml_file_path)
	return True, temp_xml_file_path

def get_ranks(result_path, bug_id, java_dir, temp_xml_filepath):
	result_file = result_path + "Bug"+ str(bug_id) +"_result.csv"
	create_file_path(result_path)
	
	try:
		command = "java -jar BugLocator.jar -b " + temp_xml_filepath +" -s " + java_dir + "/bug-"+ str(bug_id) +" -a 0.2 -o " + result_file
		os.system(command)
	except Exception as e:
		print(f"Error: Could not get the buggy java files: {e}")

	rowList = []
	with open(result_file, 'r') as file:
		csvreader = csv.reader(file)
		for row in csvreader:
			rowList.append(row)

	headerList = ["bugID","filename","rank","score"]
	with open(result_file, 'w') as file:
		writer = csv.DictWriter(file,delimiter=',',fieldnames=headerList)
		writer.writeheader()

	with open(result_file, 'a') as file:
		writer = csv.writer(file)   
		for row in rowList:
			writer.writerow(row)
	return rowList

def ranking_on_corpus(bug_id, xml_file, subpath, filetype, filtered_boosted_repo, temp_xml_dir, temp_result_dir, 
	filtered_boosted_filenames, query_reformulation_gui):
	filenameType = ""

	if filetype=="MathedQueryFiles":
		filenameType = "Match_Query_File_List"
	elif filetype=="NotMathedQueryFiles":
		filenameType = "Not_Match_Query_File_List"
	elif filetype=="FilteredFiles":
		filenameType = "Files_In_Corpus"

	filenames_store_file = filtered_boosted_filenames + "/" + subpath + "/" + filenameType + ".csv"
	files_dir = filtered_boosted_repo + "/" + subpath + "/" + filetype
	search_needed, temp_xml_file_path = remove_java_files_if_not_exist(bug_id, filenames_store_file, temp_xml_dir, xml_file, subpath, filetype)
	
	if search_needed:
		return get_ranks(temp_result_dir + "/" + subpath + "/QueryReformulation-" + query_reformulation_gui + "/" + filetype + "/",bug_id, files_dir, temp_xml_file_path)
	return []

def get_final_ranks(bug_id, filtered_files_stored_file, rankList1, rankList2, operation):
	ranks1=[]
	ranks1_files=[]
	for row in rankList1:
		ranks1.append(int(row[2])+1)
		ranks1_files.append(row[1])

	unsorted_ranks1 = ranks1.copy()
	if operation=='Filtering' or operation=="QueryReformulation":
		ranks1.sort()
		return unsorted_ranks1, ranks1, ranks1_files
	
	number_of_filtered_files = len(get_filtered_files(bug_id, filtered_files_stored_file))
	ranks2=[]
	ranks2_files=[]
	for row2 in rankList2:
		ranks2.append(int(row2[2])+1)
		ranks2_files.append(row2[1])

	ranks2 = [number_of_filtered_files + ranks2[i] for i in range(len(ranks2))]
	cur_ranks = unsorted_ranks1.copy()
	cur_ranks.extend(ranks2)

	unsorted_ranks = cur_ranks.copy()
	cur_ranks.sort()
	ranks1_files.extend(ranks2_files)
	return unsorted_ranks, cur_ranks, ranks1_files

def get_ranklist_on_query_reformulation_type(bug_id, filtering_gui, boosting_gui, query_reformulation_gui, operation, 
						 no_of_screen, temp_xml_dir, filtered_boosted_repo, temp_result_dir, 
						 preprocessed_data_dir, filtered_boosted_filenames, query_reformulation_type):
	query_subpath = "Screen-" + no_of_screen + "/Preprocessed_with_" + query_reformulation_gui
	query_xml_file = preprocessed_data_dir + "/" + query_subpath + "/"+ query_reformulation_type + "/" + "bug_" + bug_id + ".xml"
	if operation=="Filtering":
		corpus_path = "Screen-" + no_of_screen + "/" + "Corpus-" + filtering_gui
		query_rankLists = ranking_on_corpus(bug_id, query_xml_file, corpus_path, "FilteredFiles", filtered_boosted_repo, temp_xml_dir, temp_result_dir, filtered_boosted_filenames, query_reformulation_gui)
		unsorted_ranks, sorted_ranks, ranks_files = get_final_ranks(bug_id, "", query_rankLists, [], operation)
	
	elif operation=="QueryReformulation":
		corpus_path = "Screen-" + no_of_screen + "/" + "Corpus-" + "All_Java_Files"
		query_rankLists = ranking_on_corpus(bug_id, query_xml_file, corpus_path, "FilteredFiles", filtered_boosted_repo, temp_xml_dir, temp_result_dir, filtered_boosted_filenames, query_reformulation_gui)
		unsorted_ranks, sorted_ranks, ranks_files = get_final_ranks(bug_id, "", query_rankLists, [], operation)
	
	elif operation=="Boosting":
		corpus_path = "Screen-" + no_of_screen + "/" + "Corpus-" + "All_Java_Files"
		boosting_path = corpus_path + "/Boosting-" + boosting_gui
		query_boosted_rankLists = ranking_on_corpus(bug_id, query_xml_file, boosting_path, "MathedQueryFiles", filtered_boosted_repo, temp_xml_dir, temp_result_dir, filtered_boosted_filenames, query_reformulation_gui)
		query_not_boosted_rankLists = ranking_on_corpus(bug_id, query_xml_file, boosting_path, "NotMathedQueryFiles", filtered_boosted_repo, temp_xml_dir, temp_result_dir, filtered_boosted_filenames, query_reformulation_gui)
		matched_file = filtered_boosted_filenames + "/" + boosting_path + "/Match_Query_File_List.csv"
		unsorted_ranks, sorted_ranks, ranks_files = get_final_ranks(bug_id, matched_file, query_boosted_rankLists, query_not_boosted_rankLists, operation)

	elif operation=="Filtering+Boosting":
		corpus_path = "Screen-" + no_of_screen + "/" + "Corpus-" + filtering_gui
		boosting_path = corpus_path + "/Boosting-" + boosting_gui
		query_boosted_rankLists = ranking_on_corpus(bug_id, query_xml_file, boosting_path, "MathedQueryFiles", filtered_boosted_repo, temp_xml_dir, temp_result_dir, filtered_boosted_filenames, query_reformulation_gui)
		query_not_boosted_rankLists = ranking_on_corpus(bug_id, query_xml_file, boosting_path, "NotMathedQueryFiles", filtered_boosted_repo, temp_xml_dir, temp_result_dir, filtered_boosted_filenames, query_reformulation_gui)

		matched_file = filtered_boosted_filenames + "/" + boosting_path + "/Match_Query_File_List.csv"
		unsorted_ranks, sorted_ranks, ranks_files = get_final_ranks(bug_id, matched_file, query_boosted_rankLists, query_not_boosted_rankLists, operation)

	return unsorted_ranks, sorted_ranks, ranks_files

def create_final_result_header(result_file):
	os.makedirs(os.path.dirname(result_file), exist_ok=True)
	with open(result_file, 'w') as file:
		writer = csv.writer(file)
		writer.writerow(["Bug Report ID", "Ranks-unsorted (Query-Bug Report)", "Ranks (Query-Bug Report)", "Files (Query-Bug Report)",
			"Ranks-unsorted (Query Replacement)", "Ranks (Query Replacement)", "Files (Query Replacement)",
			"Ranks-unsorted (Query Expansion 1)", "Ranks (Query Expansion 1)", "Files (Query Expansion 1)"])


def compute_result(bug_id, filtering_gui, boosting_gui, query_reformulation_gui, operation, no_of_screen, temp_xml_dir,
		   final_ranks_folder, filtered_boosted_repo, temp_result_dir, preprocessed_data_dir, filtered_boosted_filenames, final_ranks_file):
	data_row = []
	data_row.append(bug_id)
	br_unsorted_ranks, br_sorted_ranks, br_ranks_files = get_ranklist_on_query_reformulation_type(bug_id, filtering_gui, boosting_gui, query_reformulation_gui, operation, 
						 no_of_screen, temp_xml_dir, filtered_boosted_repo, temp_result_dir, 
						 preprocessed_data_dir, filtered_boosted_filenames, "bug_report_original")
	data_row.append(br_unsorted_ranks)
	data_row.append(br_sorted_ranks)
	data_row.append(br_ranks_files)

	qr_unsorted_ranks, qr_sorted_ranks, qr_ranks_files = get_ranklist_on_query_reformulation_type(bug_id, filtering_gui, boosting_gui, query_reformulation_gui, operation, 
						 no_of_screen, temp_xml_dir, filtered_boosted_repo, temp_result_dir, 
						 preprocessed_data_dir, filtered_boosted_filenames, "replaced_query")
	data_row.append(qr_unsorted_ranks)
	data_row.append(qr_sorted_ranks)
	data_row.append(qr_ranks_files)

	qe_unsorted_ranks, qe_sorted_ranks, qe_ranks_files = get_ranklist_on_query_reformulation_type(bug_id, filtering_gui, boosting_gui, query_reformulation_gui, operation, 
						 no_of_screen, temp_xml_dir, filtered_boosted_repo, temp_result_dir, 
						 preprocessed_data_dir, filtered_boosted_filenames, "query_expansion_1")
	data_row.append(qe_unsorted_ranks)
	data_row.append(qe_sorted_ranks)
	data_row.append(qe_ranks_files)

	write_to_csv(final_ranks_file, data_row)

def main(args):
	# bug_issue_ids = ["2", "8", "10", "18", "19", "44",
	# 					"53", "117", "128", "129", "130",
	# 					"135", "191", "206", "209", "256",
	# 					"1073", "1096", "1146",
	# 					"1147", "1151", "1202", "1205", "1207",
	# 					"1214", "1215", "1223", "1224",
	# 					"1299", "1399", "1406", "1430", "1441",
	# 					"1445", "1481", "1645", "45", "54", "76", "92", "106", "110", "158", "160", "162", "168",
	# 					 "192", "199", "200", "248", "1150", "1198", "1228",
	# 					"1389", "1425", "1446", "1563", "1568"]
	bug_issue_ids = ["53"]
	
	#bug_issue_ids = ["11", "55", "56", "227", "1213", "1222", "1428"]

	#bug_issue_ids = ["84", "87", "151", "159", "193", "271", "275", "1028", "1089", "1130", "1402", "1403"]

	#bug_issue_ids = ["71", "201", "1641"]

	# Fifth Round
	#bug_issue_ids = ["1096", "1146", "1147", "1151", "1223", "1645", "106", "110", "168", "271"]

	# Sixth Round
	#bug_issue_ids = ["1406", "45", "1640"]

	# Seventh Round
	#bug_issue_ids = ["1150"]
	
	if args['operation']=="Filtering":
		final_ranks_file = args['final_ranks_folder'] + "/" + args['operation'] + "#Screen-" + args['screen'] + "#Filtering-" + args['filtering'] + "#Query_Reformulation-" + args['query_reformulation'] + ".csv"
	elif args['operation']=="Boosting":
		final_ranks_file = args['final_ranks_folder'] + "/" + args['operation'] + "#Screen-" + args['screen'] + "#Boosting-" + args['boosting'] + "#Query_Reformulation-" + args['query_reformulation'] + ".csv"
	elif args['operation']=="Filtering+Boosting":
		final_ranks_file = args['final_ranks_folder'] + "/" + args['operation'] + "#Screen-" + args['screen'] + "#Filtering-" + args['filtering'] + "#Boosting-" + args['boosting'] + "#Query_Reformulation-" + args['query_reformulation'] + ".csv"
	elif args['operation']=="QueryReformulation":
		final_ranks_file = args['final_ranks_folder'] + "/" + args['operation'] + "#Screen-" + args['screen'] + "#Query_Reformulation-" + args['query_reformulation'] + ".csv"
	
	# if os.path.exists(final_ranks_file):
	# 	return
	create_final_result_header(final_ranks_file)

	for bug_id in bug_issue_ids:
		compute_result(bug_id, args['filtering'], args['boosting'], args['query_reformulation'], args['operation'], 
			args['screen'], args['temp_data_dir'], args['final_ranks_folder'], args['filtered_boosted_repo'], 
			args['temp_result_dir'], args['prep_data_dir'], args['filtered_boosted_filenames'], final_ranks_file)

if __name__ == "__main__":
	# https://stackoverflow.com/questions/7427101/simple-argparse-example-wanted-1-argument-3-results
	parser = argparse.ArgumentParser()

	parser.add_argument('-f','--filtering', help='GUI type for filtering', required=False)
	parser.add_argument('-b','--boosting', help='GUI type for boosting', required=False)
	parser.add_argument('-q', '--query_reformulation', help='GUI type for reformulation', required=True)
	parser.add_argument('-s', '--screen', help='Number of screens', required=True)
	parser.add_argument('-ops','--operation', help='Operation', required=True)
	parser.add_argument('-tx','--temp_data_dir', help='Temporary xml directory', required=True)
	parser.add_argument('-franks','--final_ranks_folder', help='Final Ranks', required=True)
	parser.add_argument('-fbr','--filtered_boosted_repo', help='Filtered Boosted Repos', required=True)
	parser.add_argument('-rf','--temp_result_dir', help='Temporary result directory', required=True)
	parser.add_argument('-preq','--prep_data_dir', help='Preprocessed_Query', required=True)
	parser.add_argument('-fbfilenames','--filtered_boosted_filenames', help='filtered_boosted_filenames', required=True)

	args = vars(parser.parse_args())

	start_time = time.time()
	main(args)
	end_time = time.time()
	print("Finished in %.10f seconds" % (end_time-start_time))
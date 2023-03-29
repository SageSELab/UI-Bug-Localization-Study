import pandas as pd
import csv
import json
from file_analysis import FileAnalysis

class ReadFiles:
	def __init__(self):
		self.fileAnalysis = FileAnalysis()

	# Return all the ranked files for a particular repository based on matching with the bug report ID
	def get_ranked_files(self, bug_id, filename):
		file_list_df = pd.read_csv(filename)
		files_for_bug_id = file_list_df.loc[file_list_df['Bug Report ID']==int(bug_id), 'FilePaths'].values.tolist()

		return files_for_bug_id

	def get_code_processed(self, bug_id, codeFilepath):
		filename = "UIBugLocalization/FaultLocalizationCode/data/PreprocessedData/Preprocessed_code/bug-" + bug_id + ".csv"
		file_list_df = pd.read_csv(filename)
		files_for_bug_id = file_list_df.loc[file_list_df['FilePath']==codeFilepath, 'PreprocessedCode'].values.tolist()
		if len(files_for_bug_id)<1:
			return ""
		return files_for_bug_id[0]

	def get_ranks_for_all_bugs(self, filename, col_name):
		file_list_df = pd.read_csv(filename)
		return file_list_df[col_name]

	def get_bug_report_ids(self, filename):
		file_list_df = pd.read_csv(filename)
		return file_list_df["Bug Report ID"]

	# Returns the number of buggy java files for each bug report
	def get_buggy_java_files(self, bug_issue_id):
		######## Read json file containing the correct bug locations ###########
		json_file = "../../data/JSON-Files-All/" + str(bug_issue_id) + ".json"
		with open(json_file, 'r') as jfile:
			json_data = jfile.read()
		original_buggy_locations = json.loads(json_data)

		unique_java_files = set()
		for bug_location in original_buggy_locations["bug_location"]:
			buggy_file = bug_location["file_name"]
			if buggy_file.endswith(".java"):
				unique_java_files.add(buggy_file)

		return unique_java_files

	# Returns the number of buggy java and xml files for each bug report
	def get_buggy_files(self, bug_issue_id):
		######## Read json file containing the correct bug locations ###########
		json_file = "../../data/JSON-Files-All/" + str(bug_issue_id) + ".json"
		with open(json_file, 'r') as jfile:
			json_data = jfile.read()
		original_buggy_locations = json.loads(json_data)

		unique_files = set()
		for bug_location in original_buggy_locations["bug_location"]:
			buggy_file = bug_location["file_name"]
			if buggy_file.endswith(".java") or buggy_file.endswith(".xml"):
				unique_files.add(buggy_file)

		return unique_files

	# Return filtered files for a bug report
	def get_filtered_files(self, bug_issue_id):
		filtered_files_stored_file = "results/GraphBasedApproach_Filtered_File_List.csv"
		filtered_files = self.get_ranked_files(bug_issue_id, filtered_files_stored_file)

		return filtered_files

	# Return noisy files that do not match with the query
	def get_unfiltered_files(self, bug_issue_id):
		unfiltered_files_stored_file = "results/GraphBasedApproach_Unfiltered_File_List.csv"
		unfiltered_files = self.get_ranked_files(bug_issue_id, unfiltered_files_stored_file)

		return unfiltered_files

	def get_bug_report_contents(self, bug_id):
		bug_report_file = "UIBugLocalization/FaultLocalizationCode/data/BugReports/bug_report_" + bug_id + ".txt"
		bug_report_contents = self.fileAnalysis.get_file_content(bug_report_file)

		return bug_report_contents

	def get_bug_report_contents_preprocessed(self, bug_id, query_type, query):
		bug_report_file = "UIBugLocalization/FaultLocalizationCode/data/PreprocessedData/Preprocessed_with_" + query_type + "/Preprocessed_" + query + "/bug_report_" + bug_id + ".txt"
		bug_report_contents = self.fileAnalysis.get_file_content(bug_report_file)

		return bug_report_contents   

	def get_all_java_files(self, bug_id):
		parent_directory = "UIBugLocalization/Backup/CodeUnused/BuggyProjects/bug-" + bug_id
		all_java_files = self.fileAnalysis.get_all_java_files(parent_directory)

		return all_java_files

	def get_all_component_id_related_files(self, bug_id, all_component_ids):
		parent_directory = "UIBugLocalization/Backup/CodeUnused/BuggyProjects/bug-" + bug_id
		all_comp_id_related_files = self.fileAnalysis.get_files_if_term_exists(parent_directory, all_component_ids)

		return all_comp_id_related_files






import pandas as pd
import csv

def write_to_csv(write_file, row):
	with open(write_file, 'a') as file:
		writer = csv.writer(file)
		writer.writerow(row)

# Return all the ranked files for a particular repository based on matching with the bug report ID
def get_ranked_files(bug_id, filename):
	file_list_df = pd.read_csv(filename)
	files_for_bug_id = file_list_df.loc[file_list_df['Bug Report ID']==int(bug_id), 'FilePaths'].values.tolist()

	return files_for_bug_id

src_file = "UIBugLocalization/FaultLocalizationCode/BugLocator-organizedCode/TestRs/GraphBasedApproach_Filtered_File_List.csv"
file_list_output_file = "UIBugLocalization/FaultLocalizationCode/BugLocator-organizedCode/TestRs/Res.csv"
with open(file_list_output_file, 'w') as file:
	writer = csv.writer(file)
	writer.writerow(["Bug ID", "Number of files"])

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

for bug_id in bug_issue_ids:
	file_count = len(get_ranked_files(bug_id, src_file))

	write_to_csv(file_list_output_file, [bug_id, file_count])


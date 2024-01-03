#! /bin/bash
export JAVA_HOME=`/usr/libexec/java_home -v 1.11`
mvn package -DskipTests

# Data directory
data_dir=/Users/sagelab/Documents/Projects/BugLocalization/Artifact-ICSE24/GUI-Bug-Localization-Data

export screens=("4" "3" "2")

# This variable contains the type of the information that will be preprocessed. There are exactly four keywords that should be used here.
#	- Title: Preprocess Bug Report Titles. Only necessary for BugLocator.
#   - Content: Preprocess Bug Report Contents. Only necessary for BugLocator. 
#   - BugReport: Preprocess Bug Reports. It is necessary for all baselines except BugLocator.
# 	- Code: Preprocess Source Code. It is necessary for all baselines.
export content_type="Code" # Title or Content or BugReport or Code

if [[ "$content_type" == "BugReport" ]]; 
then
	# This corpus type should not be changed
	corpus_type=GUI_State_and_All_GUI_Component_IDs
	# The path of the folder that contains bug reports
	bug_reports_folder=${data_dir}/BugReports
	# The path of the GUI info. In the data repository, this folder is named Augmentation-Info.
	query_infos_file=${data_dir}/Augmentation-Info
	# Output: Preprocessed bug reports with query reformulation
	preprocessed_query_folder=${data_dir}/PreprocessedData/PreprocessedBugReports

	for i in ${!screens[@]}; do
		"$JAVA_HOME/bin/java" -cp target/code_search_ir-1.0.jar MainClass -br ${bug_reports_folder} \
		-qinfo ${query_infos_file} -s ${screens[$i]} -c ${corpus_type} -preq ${preprocessed_query_folder} \
		-ctype ${content_type} 
	done
elif [[ "$content_type" == "Content" ]]; 
then
	corpus_type=GUI_State_and_All_GUI_Component_IDs
	# The path of the folder that contains bug reports without titles
	bug_reports_folder=${data_dir}/BugReportsContents
	# The path of the GUI info. In the data repository, this folder is named Augmentation-Info.
	query_infos_file=${data_dir}/Augmentation-Info
	# Output: Preprocessed bug reports contents with query reformulation
	preprocessed_query_folder=${data_dir}/PreprocessedData/PreprocessedContents

	for i in ${!screens[@]}; do
		"$JAVA_HOME/bin/java" -cp target/code_search_ir-1.0.jar MainClass -br ${bug_reports_folder} \
		-qinfo ${query_infos_file} -s ${screens[$i]} -c ${corpus_type} -preq ${preprocessed_query_folder} \
		-ctype ${content_type} 
	done
elif [[ "${content_type}" == "Title" ]];
then
	# The path of the folder that contains bug report titles
	bug_reports_titles=${data_dir}/BugReportsTitles
	# Output: Preprocessed bug report titles
	preprocessed_titles_folder=${data_dir}/PreprocessedData/PreprocessedTitles

	for i in ${!screens[@]}; do
		"$JAVA_HOME/bin/java" -cp target/code_search_ir-1.0.jar MainClass -br ${bug_reports_titles} \
		-s ${screens[$i]} -preq ${preprocessed_titles_folder} \
		-ctype ${content_type} 
	done
elif [[ "${content_type}" == "Code" ]];
then
	# The path of the source code repositories
	buggy_projects=${data_dir}/BuggyProjects
	# Output: Preprocessed code
	preprocessed_code_folder=${data_dir}/PreprocessedData/PreprocessedCode

	"$JAVA_HOME/bin/java" -cp target/code_search_ir-1.0.jar MainClass \
		-preq ${preprocessed_code_folder} -bp ${buggy_projects}\
		-ctype ${content_type}

fi

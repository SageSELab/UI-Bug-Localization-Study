#! /bin/bash
export JAVA_HOME=`/usr/libexec/java_home -v 1.11`
mvn package -DskipTests

export screens=("4" "3" "2")

export content_type="Code" # Title or Content or BugReport or Code

if [[ "$content_type" == "BugReport" ]]; 
then
	corpus_type=GUI_State_and_All_GUI_Component_IDs
	bug_reports_folder=/Users/sagelab/Documents/Projects/BugLocalization/FL-final/FaultLocalizationCode-ICSE/data/BugReports
	query_infos_file=/Users/sagelab/Documents/Projects/BugLocalization/FL-final/FaultLocalizationCode-ICSE/data/Augmentation-Info
	preprocessed_query_folder=/Users/sagelab/Documents/Projects/BugLocalization/FL-final/FaultLocalizationCode-ICSE/data/PreprocessedData/PreprocessedBugReports

	for i in ${!screens[@]}; do
		"$JAVA_HOME/bin/java" -cp target/code_search_ir-1.0.jar MainClass -br ${bug_reports_folder} \
		-qinfo ${query_infos_file} -s ${screens[$i]} -c ${corpus_type} -preq ${preprocessed_query_folder} \
		-ctype ${content_type} 
	done
elif [[ "$content_type" == "Content" ]]; 
then
	corpus_type=GUI_State_and_All_GUI_Component_IDs
	bug_reports_folder=/Users/sagelab/Documents/Projects/BugLocalization/FL-final/FaultLocalizationCode-ICSE/data/BugReportsContents
	query_infos_file=/Users/sagelab/Documents/Projects/BugLocalization/FL-final/FaultLocalizationCode-ICSE/data/Augmentation-Info
	preprocessed_query_folder=/Users/sagelab/Documents/Projects/BugLocalization/FL-final/FaultLocalizationCode-ICSE/data/PreprocessedData/PreprocessedContents

	for i in ${!screens[@]}; do
		"$JAVA_HOME/bin/java" -cp target/code_search_ir-1.0.jar MainClass -br ${bug_reports_folder} \
		-qinfo ${query_infos_file} -s ${screens[$i]} -c ${corpus_type} -preq ${preprocessed_query_folder} \
		-ctype ${content_type} 
	done
elif [[ "${content_type}" == "Title" ]];
then
	bug_reports_titles=/Users/sagelab/Documents/Projects/BugLocalization/FL-final/FaultLocalizationCode-ICSE/data/BugReportsTitles
	preprocessed_titles_folder=/Users/sagelab/Documents/Projects/BugLocalization/FL-final/FaultLocalizationCode-ICSE/data/PreprocessedData/PreprocessedTitles

	for i in ${!screens[@]}; do
		"$JAVA_HOME/bin/java" -cp target/code_search_ir-1.0.jar MainClass -br ${bug_reports_titles} \
		-s ${screens[$i]} -preq ${preprocessed_titles_folder} \
		-ctype ${content_type} 
	done
elif [[ "${content_type}" == "Code" ]];
then
	buggy_projects=/Users/sagelab/Documents/Projects/BugLocalization/BuggyProjects
	preprocessed_code_folder=/Users/sagelab/Documents/Projects/BugLocalization/FL-final/FaultLocalizationCode-ICSE/data/PreprocessedData/PreprocessedCode

	"$JAVA_HOME/bin/java" -cp target/code_search_ir-1.0.jar MainClass \
		-preq ${preprocessed_code_folder} -bp ${buggy_projects}\
		-ctype ${content_type}

fi

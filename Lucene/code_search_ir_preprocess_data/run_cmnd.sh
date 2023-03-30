#! /bin/bash
export JAVA_HOME=`/usr/libexec/java_home -v 1.11`
mvn package -DskipTests

# boosted_queries=("GUI_States" "Interacted_GUI_Component_IDs" "GUI_State_and_Interacted_GUI_Component_IDs"
# 	"All_GUI_Component_IDs" "GUI_State_and_All_GUI_Component_IDs")

# screens=("4" "3" "2")
# corpus_types=("All_Java_Files" "GUI_State_and_All_GUI_Component_IDs" "All_GUI_Component_IDs"
# 	"GUI_States" "Interacted_GUI_Component_IDs" "GUI_State_and_Interacted_GUI_Component_IDs")

export screens=("4" "3" "2")

export content_type="Title"

if [[ "$content_type" == "Content" ]]; then
	corpus_type=GUI_State_and_All_GUI_Component_IDs
	#bug_reports_folder=UIBugLocalization/FaultLocalizationCode/data/BugReports
	bug_reports_folder=UIBugLocalization/FaultLocalizationCode/data/BugReportsContents
	query_infos_file=UIBugLocalization/FaultLocalizationCode/data/FilteringBoostingFileNames-round7
	#preprocessed_query_folder=UIBugLocalization/FaultLocalizationCode/data/PreprocessedData/PreprocessedQueries-round7
	preprocessed_query_folder=UIBugLocalization/FaultLocalizationCode/data/PreprocessedData/PreprocessedContents-round7

	for i in ${!screens[@]}; do
		"$JAVA_HOME/bin/java" -cp target/code_rch_ir-1.0.jar MainClass -br ${bug_reports_folder} \
		-qinfo ${query_infos_file} -s ${screens[$i]} -c ${corpus_type} -preq ${preprocessed_query_folder} \
		-ctype ${content_type} 
	done
elif [[ "${content_type}" == "Title" ]];
then
	bug_reports_titles=UIBugLocalization/FaultLocalizationCode/data/BugReportsTitles
	preprocessed_titles_folder=UIBugLocalization/FaultLocalizationCode/data/PreprocessedData/PreprocessedTitles-round7

	for i in ${!screens[@]}; do
		"$JAVA_HOME/bin/java" -cp target/code_rch_ir-1.0.jar MainClass -br ${bug_reports_titles} \
		-s ${screens[$i]} -preq ${preprocessed_titles_folder} \
		-ctype ${content_type} 
	done
elif [[ "${content_type}" == "Code" ]];
then
	preprocessed_code_folder=UIBugLocalization/FaultLocalizationCode/data/PreprocessedData/PreprocessedCode-round7
	buggy_projects=UIBugLocalization/Backup/CodeUnused/BuggyProjects

	"$JAVA_HOME/bin/java" -cp target/code_rch_ir-1.0.jar MainClass \
		-preq ${preprocessed_code_folder} -bp ${buggy_projects}\
		-ctype ${content_type}

fi

#! /bin/bash
#export JAVA_HOME=`/usr/libexec/java_home -v 1.11`
mvn package -DskipTests

export preprocessedDataPath=/Users/sagelab/Documents/Projects/BugLocalization/FL-final/FaultLocalizationCode-ICSE/data/PreprocessedData/PreprocessedBugReports
export preprocessedCodePath=/Users/sagelab/Documents/Projects/BugLocalization/FL-final/FaultLocalizationCode-ICSE/data/PreprocessedData/PreprocessedCode
export jsonFilePath=/Users/sagelab/Documents/Projects/BugLocalization/FL-final/FaultLocalizationCode-ICSE/data/BugLocalizationGroundTruth
export buggy_project_dir=/Users/sagelab/Documents/Projects/BugLocalization/BuggyProjects
export filtered_boosted_files_in_repo=/Users/sagelab/Documents/Projects/BugLocalization/FL-final/Augmenation-Corpus
export result_folder=/Users/sagelab/Documents/Projects/BugLocalization/FL-final/FaultLocalizationCode-ICSE/Results/Lucene/TempResults

#Final Results with the proper format will be saved here
export final_ranks_folder=/Users/sagelab/Documents/Projects/BugLocalization/FL-final/FaultLocalizationCode-ICSE/Results/Lucene/FinalRankings
export filtered_boosted_filenames=/Users/sagelab/Documents/Projects/BugLocalization/FL-final/FaultLocalizationCode-ICSE/data/Augmentation-Info

# This path will be similar to Original Source Code Repository.
export preprocessed_code_dir=/Users/sagelab/Documents/Projects/BugLocalization/BuggyProjects

export filtering_list=("GUI_States" "Interacted_GUI_Component_IDs" "GUI_State_and_Interacted_GUI_Component_IDs" 
	"All_GUI_Component_IDs" "GUI_State_and_All_GUI_Component_IDs")
export boosting_list=("GUI_States" "Interacted_GUI_Component_IDs" "GUI_State_and_Interacted_GUI_Component_IDs" 
	"All_GUI_Component_IDs" "GUI_State_and_All_GUI_Component_IDs")
export query_reformulation_list=("GUI_States" "Interacted_GUI_Component_IDs" "GUI_State_and_Interacted_GUI_Component_IDs" 
	"All_GUI_Component_IDs" "GUI_State_and_All_GUI_Component_IDs")
export screen_list=("2" "3" "4")

#For Boosting
# for j in ${!boosting_list[@]}; do 
# 	for k in ${!query_reformulation_list[@]}; do
# 		for l in ${!screen_list[@]}; do 
# 			echo "Boosting: B-${boosting_list[$j]}#Q-${query_reformulation_list[$k]}#S-${screen_list[$l]}"

# 			java -cp target/code_search_ir-1.0.jar MainClass -b ${boosting_list[$j]} \
# 				-q ${query_reformulation_list[$k]} -s ${screen_list[$l]}  \
# 				-rf $result_folder \
# 				-bpd $buggy_project_dir -pcd ${preprocessed_code_dir}\
# 				-fbr $filtered_boosted_files_in_repo -preq $preprocessedDataPath -jpath $jsonFilePath \
# 				-ops Boosting -prec $preprocessedCodePath -franks $final_ranks_folder \
# 				-fbfilenames $filtered_boosted_filenames
# 		done
# 	done
# done


# No filtering or boosting, query reformulation only
for k in ${!query_reformulation_list[@]}; do
	for l in ${!screen_list[@]}; do 
		echo "Query Reformulation: Q-${query_reformulation_list[$k]}#S-${screen_list[$l]}"

		java -cp target/code_search_ir-1.0.jar MainClass \
				-q ${query_reformulation_list[$k]} -s ${screen_list[$l]}  \
				-rf $result_folder \
				-bpd $buggy_project_dir -pcd ${preprocessed_code_dir}\
				-fbr $filtered_boosted_files_in_repo -preq $preprocessedDataPath -jpath $jsonFilePath \
				-ops QueryReformulation -prec $preprocessedCodePath -franks $final_ranks_folder \
				-fbfilenames $filtered_boosted_filenames 
	done
done

#For Filtering and boosting
# for i in ${!filtering_list[@]}; do
# 	if [[ ${filtering_list[$i]} == "GUI_States" ]]; then
# 		boosting_gui_type=("Interacted_GUI_Component_IDs")
# 	elif [[ ${filtering_list[$i]} == "Interacted_GUI_Component_IDs" ]]; then
# 		boosting_gui_type=("GUI_States")
# 	else
# 		boosting_gui_type=()
# 		index=0
# 		for j in ${!boosting_list[@]}; do
# 			if [[ $index -lt $i ]]; then
# 				boosting_gui_type+=(${boosting_list[j]})
# 				index=$((index+1))
# 			else
# 				break
# 			fi
# 		done
# 	fi

# 	for j in ${!boosting_gui_type[@]}; do 
# 		for k in ${!query_reformulation_list[@]}; do
# 			for l in ${!screen_list[@]}; do 
# 				echo "Filtering+Boosting: F-${filtering_list[$i]}#B-${boosting_gui_type[$j]}#Q-${query_reformulation_list[$k]}#S-${screen_list[$l]}"

# 				java -cp target/code_search_ir-1.0.jar MainClass \
# 					-f ${filtering_list[$i]} -b ${boosting_gui_type[$j]} \
# 					-q ${query_reformulation_list[$k]} -s ${screen_list[$l]}  \
# 					-rf $result_folder \
# 					-bpd $buggy_project_dir -pcd ${preprocessed_code_dir}\
# 					-fbr $filtered_boosted_files_in_repo -preq $preprocessedDataPath -jpath $jsonFilePath \
# 					-ops Filtering+Boosting -prec $preprocessedCodePath -franks $final_ranks_folder \
# 					-fbfilenames $filtered_boosted_filenames 
# 			done
# 		done
# 	done
# 	#echo "\n"
# done


# # For Filtering
# for i in ${!filtering_list[@]}; do
# 	for k in ${!query_reformulation_list[@]}; do
# 		for l in ${!screen_list[@]}; do 
# 			echo "Filtering: F-${filtering_list[$i]}#Q-${query_reformulation_list[$k]}#S-${screen_list[$l]}"

# 			java -cp target/code_search_ir-1.0.jar MainClass \
# 					-f ${filtering_list[$i]} \
# 					-q ${query_reformulation_list[$k]} -s ${screen_list[$l]}  \
# 					-rf $result_folder \
# 					-bpd $buggy_project_dir -pcd ${preprocessed_code_dir}\
# 					-fbr $filtered_boosted_files_in_repo -preq $preprocessedDataPath -jpath $jsonFilePath \
# 					-ops Filtering -prec $preprocessedCodePath -franks $final_ranks_folder \
# 					-fbfilenames $filtered_boosted_filenames
# 		done
# 	done
# done
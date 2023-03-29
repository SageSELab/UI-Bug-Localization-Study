export prep_data_dir=../data/PreprocessedData/BugLocatorQueries-bug53

#Change this path
export filtered_boosted_files_in_repo=UIBugLocalization/Backup/FilteredBoostedProjects
#export filtered_boosted_files_in_repo=UIBugLocalization/FilteredBoostedProjects
#export filtered_boosted_files_in_repo=UIBugLocalization/FaultLocalizationCode/Projects/FilteredBoostedProjects-round5
#export filtered_boosted_files_in_repo=UIBugLocalization/FaultLocalizationCode/Projects/FilteredBoostedProjects-round7

export temp_data_dir=temp_xml_dir
export temp_result_dir=results
#export final_ranks_folder=../FinalResultComputation/AllResults/BugLocator-round7
#export filtered_boosted_filenames=../data/FilteringBoostingFileNames-round7
export final_ranks_folder=../FinalResultComputation/AllResults/BugLocator53-2
export filtered_boosted_filenames=../data/FilteringBoostingFileNames

export filtering_list=("GUI_States" "Interacted_GUI_Component_IDs" "GUI_State_and_Interacted_GUI_Component_IDs" 
	"All_GUI_Component_IDs" "GUI_State_and_All_GUI_Component_IDs")
export boosting_list=("GUI_States" "Interacted_GUI_Component_IDs" "GUI_State_and_Interacted_GUI_Component_IDs" 
	"All_GUI_Component_IDs" "GUI_State_and_All_GUI_Component_IDs")
export query_reformulation_list=("GUI_States" "Interacted_GUI_Component_IDs" "GUI_State_and_Interacted_GUI_Component_IDs" 
	"All_GUI_Component_IDs" "GUI_State_and_All_GUI_Component_IDs")
export screen_list=("2" "3" "4")

# export filtering_list=("GUI_States" "GUI_State_and_All_GUI_Component_IDs")
# export boosting_list=("GUI_States")
# export query_reformulation_list=("GUI_States")
# export screen_list=("4")

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
# 				python3 buglocator.py -f ${filtering_list[$i]} -b ${boosting_gui_type[$j]} \
# 					-q ${query_reformulation_list[$k]} -s ${screen_list[$l]}  \
# 					-rf $temp_result_dir -tx $temp_data_dir\
# 					-fbr $filtered_boosted_files_in_repo -preq $prep_data_dir \
# 					-ops Filtering+Boosting -franks $final_ranks_folder -fbfilenames $filtered_boosted_filenames
# 			done
# 		done
# 	done
# 	#echo "\n"
# done

# # #For Filtering
# for i in ${!filtering_list[@]}; do
# 	for k in ${!query_reformulation_list[@]}; do
# 		for l in ${!screen_list[@]}; do 
# 			echo "Filtering: F-${filtering_list[$i]}#Q-${query_reformulation_list[$k]}#S-${screen_list[$l]}"
# 			python3 buglocator.py -f ${filtering_list[$i]} \
# 					-q ${query_reformulation_list[$k]} -s ${screen_list[$l]}  \
# 					-rf $temp_result_dir -tx $temp_data_dir\
# 					-fbr $filtered_boosted_files_in_repo -preq $prep_data_dir \
# 					-ops Filtering -franks $final_ranks_folder -fbfilenames $filtered_boosted_filenames
# 		done
# 	done
# done

# # # #For Boosting
# for j in ${!boosting_list[@]}; do 
# 	for k in ${!query_reformulation_list[@]}; do
# 		for l in ${!screen_list[@]}; do 
# 			echo "Boosting: B-${boosting_list[$j]}#Q-${query_reformulation_list[$k]}#S-${screen_list[$l]}"
# 			python3 buglocator.py -b ${boosting_list[$j]} \
# 					-q ${query_reformulation_list[$k]} -s ${screen_list[$l]}  \
# 					-rf $temp_result_dir -tx $temp_data_dir\
# 					-fbr $filtered_boosted_files_in_repo -preq $prep_data_dir \
# 					-ops Boosting -franks $final_ranks_folder -fbfilenames $filtered_boosted_filenames
# 		done
# 	done
# done


# No filtering or boosting, query reformulation only
for k in ${!query_reformulation_list[@]}; do
	for l in ${!screen_list[@]}; do 
		echo "Query Reformulation: Q-${query_reformulation_list[$k]}#S-${screen_list[$l]}"
		python3 buglocator.py \
					-q ${query_reformulation_list[$k]} -s ${screen_list[$l]}  \
					-rf $temp_result_dir -tx $temp_data_dir\
					-fbr $filtered_boosted_files_in_repo -preq $prep_data_dir \
					-ops QueryReformulation -franks $final_ranks_folder -fbfilenames $filtered_boosted_filenames
	done
done
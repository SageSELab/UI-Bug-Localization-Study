# Data directory
data_dir=/Users/sagelab/Documents/Projects/BugLocalization/Artifact-ICSE24/GUI-Bug-Localization-Data
package_dir=/Users/sagelab/Documents/Projects/BugLocalization/Artifact-ICSE24/UI-Bug-Localization-Study

export prep_data_dir=${data_dir}/PreprocessedData/BugLocatorQueries

export filtered_boosted_files_in_repo=${data_dir}/Augmenation-Corpus
export filtered_boosted_filenames=${data_dir}/Augmentation-Info

export temp_data_dir=temp_xml_dir
export temp_result_dir=temp_results

export final_ranks_folder=${package_dir}/Results/BugLocator

export filtering_list=("GUI_States" "Interacted_GUI_Component_IDs" "GUI_State_and_Interacted_GUI_Component_IDs" 
	"All_GUI_Component_IDs" "GUI_State_and_All_GUI_Component_IDs")
export boosting_list=("GUI_States" "Interacted_GUI_Component_IDs" "GUI_State_and_Interacted_GUI_Component_IDs" 
	"All_GUI_Component_IDs" "GUI_State_and_All_GUI_Component_IDs")
export query_reformulation_list=("GUI_States" "Interacted_GUI_Component_IDs" "GUI_State_and_Interacted_GUI_Component_IDs" 
	"All_GUI_Component_IDs" "GUI_State_and_All_GUI_Component_IDs")
export screen_list=("2" "3" "4")

#For Boosting
for j in ${!boosting_list[@]}; do 
	for k in ${!query_reformulation_list[@]}; do
		for l in ${!screen_list[@]}; do 
			echo "Boosting: B-${boosting_list[$j]}#Q-${query_reformulation_list[$k]}#S-${screen_list[$l]}"
			python3 buglocator.py -b ${boosting_list[$j]} \
					-q ${query_reformulation_list[$k]} -s ${screen_list[$l]}  \
					-rf $temp_result_dir -tx $temp_data_dir\
					-fbr $filtered_boosted_files_in_repo -preq $prep_data_dir \
					-ops Boosting -franks $final_ranks_folder -fbfilenames $filtered_boosted_filenames
		done
	done
done

#For Filtering and boosting
for i in ${!filtering_list[@]}; do
	if [[ ${filtering_list[$i]} == "GUI_States" ]]; then
		boosting_gui_type=("Interacted_GUI_Component_IDs")
	elif [[ ${filtering_list[$i]} == "Interacted_GUI_Component_IDs" ]]; then
		boosting_gui_type=("GUI_States")
	else
		boosting_gui_type=()
		index=0
		for j in ${!boosting_list[@]}; do
			if [[ $index -lt $i ]]; then
				boosting_gui_type+=(${boosting_list[j]})
				index=$((index+1))
			else
				break
			fi
		done
	fi

	for j in ${!boosting_gui_type[@]}; do 
		for k in ${!query_reformulation_list[@]}; do
			for l in ${!screen_list[@]}; do 
				echo "Filtering+Boosting: F-${filtering_list[$i]}#B-${boosting_gui_type[$j]}#Q-${query_reformulation_list[$k]}#S-${screen_list[$l]}"
				python3 buglocator.py -f ${filtering_list[$i]} -b ${boosting_gui_type[$j]} \
					-q ${query_reformulation_list[$k]} -s ${screen_list[$l]}  \
					-rf $temp_result_dir -tx $temp_data_dir\
					-fbr $filtered_boosted_files_in_repo -preq $prep_data_dir \
					-ops Filtering+Boosting -franks $final_ranks_folder -fbfilenames $filtered_boosted_filenames
			done
		done
	done
	#echo "\n"
done

#For Filtering
for i in ${!filtering_list[@]}; do
	for k in ${!query_reformulation_list[@]}; do
		for l in ${!screen_list[@]}; do 
			echo "Filtering: F-${filtering_list[$i]}#Q-${query_reformulation_list[$k]}#S-${screen_list[$l]}"
			python3 buglocator.py -f ${filtering_list[$i]} \
					-q ${query_reformulation_list[$k]} -s ${screen_list[$l]}  \
					-rf $temp_result_dir -tx $temp_data_dir\
					-fbr $filtered_boosted_files_in_repo -preq $prep_data_dir \
					-ops Filtering -franks $final_ranks_folder -fbfilenames $filtered_boosted_filenames
		done
	done
done


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
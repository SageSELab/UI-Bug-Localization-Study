screens=("4" "3" "2")
corpus_types=("All_Java_Files" "GUI_State_and_All_GUI_Component_IDs" "All_GUI_Component_IDs"
	"GUI_States" "Interacted_GUI_Component_IDs" "GUI_State_and_Interacted_GUI_Component_IDs")
boosted_queries=("GUI_States" "Interacted_GUI_Component_IDs" "GUI_State_and_Interacted_GUI_Component_IDs"
	"All_GUI_Component_IDs" "GUI_State_and_All_GUI_Component_IDs")

# Data directory
data_dir=/Users/sagelab/Documents/Projects/BugLocalization/Artifact-ICSE24/GUI-Bug-Localization-Data

# The path of the source code repositories
buggy_project_dir=${data_dir}/BuggyProjects
# The path of the folder that contains trace-replayer data
trace_replacer_data_dir=${data_dir}/TraceReplayer-Data
# Output: The path where the output will be saved. In the data repository, this folder is named Augmentation-Info.
results_folder=${data_dir}/Augmentation-Info

for i in ${!screens[@]}; do
	for j in ${!corpus_types[@]}; do
		for k in ${!boosted_queries[@]}; do
			python3 get_filtered_unfiltered_files.py -s ${screens[$i]} \
			-c ${corpus_types[$j]} -q ${boosted_queries[$k]} -r ${results_folder} \
			-ops Filtering+Boosting -bpr ${buggy_project_dir} -tr ${trace_replacer_data_dir} 
		done
		python3 get_filtered_unfiltered_files.py -s ${screens[$i]} \
			-c ${corpus_types[$j]} -r ${results_folder} \
			-ops Filtering -bpr ${buggy_project_dir} -tr ${trace_replacer_data_dir} 
	done
done


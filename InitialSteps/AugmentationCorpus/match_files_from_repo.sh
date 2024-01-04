# Data directory
data_dir=/Users/sagelab/Documents/Projects/BugLocalization/Artifact-ICSE24/GUI-Bug-Localization-Data

# The path of the source code repositories
export buggy_project_dir=${data_dir}/BuggyProjects
# The path of the GUI info. In the data repository, this folder is named Augmentation-Info.
export filtering_boosting_filenames=${data_dir}/Augmentation-Info
# Output: This path contains the path where the filtered corpus will be saved. After searching according to different queries, we will remove the files that are irrelevant to the queries.
export filtered_boosted_files_in_repo=${data_dir}/Augmenation-Corpus

screens=("4" "3" "2")
corpus_types=("All_Java_Files" "GUI_State_and_All_GUI_Component_IDs" "All_GUI_Component_IDs"
	"GUI_States" "Interacted_GUI_Component_IDs" "GUI_State_and_Interacted_GUI_Component_IDs")
boosted_queries=("GUI_States" "Interacted_GUI_Component_IDs" "GUI_State_and_Interacted_GUI_Component_IDs"
	"All_GUI_Component_IDs" "GUI_State_and_All_GUI_Component_IDs")

for i in ${!screens[@]}; do
	for j in ${!corpus_types[@]}; do
		for k in ${!boosted_queries[@]}; do
			python3 match_files_from_repo.py -s ${screens[$i]} \
			-c ${corpus_types[$j]} -q ${boosted_queries[$k]} \
			-bpd $buggy_project_dir -fbfile $filtering_boosting_filenames \
			-fbr $filtered_boosted_files_in_repo -bpdcsv $buggy_project_dir -ops Filtering+Boosting
		done
		python3 match_files_from_repo.py -s ${screens[$i]} \
			-c ${corpus_types[$j]} \
			-bpd $buggy_project_dir -fbfile $filtering_boosting_filenames \
			-fbr $filtered_boosted_files_in_repo -bpdcsv $buggy_project_dir -ops Filtering
	done
done
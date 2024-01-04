# Data directory
data_dir=/Users/sagelab/Documents/Projects/BugLocalization/Artifact-ICSE24/GUI-Bug-Localization-Data
package_dir=/Users/sagelab/Documents/Projects/BugLocalization/Artifact-ICSE24/UI-Bug-Localization-Study

export preprocessedDataPath=${data_dir}/PreprocessedData/PreprocessedBugReports
export preprocessedCodePath=${data_dir}/PreprocessedData/PreprocessedCode
export jsonFilePath=${data_dir}/BugLocalizationGroundTruth

export buggy_project_dir=${data_dir}/BuggyProjects

export filtered_boosted_files_in_repo=${data_dir}/Augmenation-Corpus
export filtered_boosted_filenames=${data_dir}/Augmentation-Info

#Delete the following three folders if exists
#The temporary results will be saved here
export result_folder=temp_results
#Temporary text embeddings will be saved here
export embeddings_folder=embeddings
#Similarity Scores will be saved here. Basically if the cosine similarity scores are already computed, we will not have to recompute that again.
export similarity_folder=similarityScores

#Final Results with the proper format will be saved here
export final_ranks_folder=${package_dir}/Results/SentenceBERT/Rankings

# This path is the directory of the source code projects that was used during preprocessing. If you are using our preprocessed data, the the path should be /Users/sagelab/Documents/Projects/BugLocalization/Artifact-ICSE24/BuggyProjects
export preprocessed_code_dir=${data_dir}/BuggyProjects

export filtering_list=("GUI_States" "GUI_State_and_All_GUI_Component_IDs")
export boosting_list=("GUI_States")
export query_reformulation_list=("GUI_States")
export screen_list=("4")

# #For Boosting
for j in ${!boosting_list[@]}; do 
	for k in ${!query_reformulation_list[@]}; do
		for l in ${!screen_list[@]}; do 
			echo "Boosting: B-${boosting_list[$j]}#Q-${query_reformulation_list[$k]}#S-${screen_list[$l]}"
			python sentenceBert-FBQ.py -b ${boosting_list[$j]} \
				-q ${query_reformulation_list[$k]} -s ${screen_list[$l]}  \
				-rf $result_folder \
				-bpd $buggy_project_dir -pcd ${preprocessed_code_dir}\
				-fbr $filtered_boosted_files_in_repo -preq $preprocessedDataPath -jpath $jsonFilePath \
				-ops Boosting -prec $preprocessedCodePath -franks $final_ranks_folder \
				-fbfilenames $filtered_boosted_filenames -emb $embeddings_folder \
				-sim $similarity_folder
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
				python sentenceBert-FBQ.py -f ${filtering_list[$i]} -b ${boosting_gui_type[$j]} \
					-q ${query_reformulation_list[$k]} -s ${screen_list[$l]}  \
					-rf $result_folder \
					-bpd $buggy_project_dir -pcd ${preprocessed_code_dir}\
					-fbr $filtered_boosted_files_in_repo -preq $preprocessedDataPath -jpath $jsonFilePath \
					-ops Filtering+Boosting -prec $preprocessedCodePath -franks $final_ranks_folder \
					-fbfilenames $filtered_boosted_filenames -emb $embeddings_folder\
					-sim $similarity_folder
			done
		done
	done
	#echo "\n"
done


# For Filtering
for i in ${!filtering_list[@]}; do
	for k in ${!query_reformulation_list[@]}; do
		for l in ${!screen_list[@]}; do 
			echo "Filtering: F-${filtering_list[$i]}#Q-${query_reformulation_list[$k]}#S-${screen_list[$l]}"
			python sentenceBert-FBQ.py -f ${filtering_list[$i]} \
				-q ${query_reformulation_list[$k]} -s ${screen_list[$l]}  \
				-rf $result_folder \
				-bpd $buggy_project_dir -pcd ${preprocessed_code_dir}\
				-fbr $filtered_boosted_files_in_repo -preq $preprocessedDataPath -jpath $jsonFilePath \
				-ops Filtering -prec $preprocessedCodePath -franks $final_ranks_folder \
				-fbfilenames $filtered_boosted_filenames -emb $embeddings_folder \
				-sim $similarity_folder
		done
	done
done


# No filtering or boosting, query reformulation only
for k in ${!query_reformulation_list[@]}; do
	for l in ${!screen_list[@]}; do 
		echo "Query Reformulation: Q-${query_reformulation_list[$k]}#S-${screen_list[$l]}"
		python sentenceBert-FBQ.py \
			-q ${query_reformulation_list[$k]} -s ${screen_list[$l]}  \
			-rf $result_folder \
			-bpd $buggy_project_dir -pcd ${preprocessed_code_dir}\
			-fbr $filtered_boosted_files_in_repo -preq $preprocessedDataPath -jpath $jsonFilePath \
			-ops QueryReformulation -prec $preprocessedCodePath -franks $final_ranks_folder \
			-fbfilenames $filtered_boosted_filenames -emb $embeddings_folder \
			-sim $similarity_folder
	done
done

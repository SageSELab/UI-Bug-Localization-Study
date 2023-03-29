: '
python get_filtered_unfiltered_files.py -s <number_of_screens> -c <corpus> -q <files_to_boost> -r <result_folder>

Here, 
number_of_screens = Number of screens, n to get activities/fragments and we will have (n-1) interacted component ids
	Possible values: 4 or 3 or 2

corpus = Type of corpus we will use
	Possible values: 
	All_Java_Files or GUI_State_and_All_GUI_Component_IDs or All_GUI_Component_IDs or GUI_States 
	or Interacted_GUI_Component_IDs or GUI_State_and_Interacted_GUI_Component_IDs

query = Files that we boost based on matching query
	Possible values:
	GUI_State_and_Interacted_GUI_Component_IDs or GUI_States or GUI_State_and_All_GUI_Component_IDs 
	or Interacted_GUI_Component_IDs or All_GUI_Component_IDs

results = Folder where we will store the results 
'
screens=("4" "3" "2")
corpus_types=("All_Java_Files" "GUI_State_and_All_GUI_Component_IDs" "All_GUI_Component_IDs"
	"GUI_States" "Interacted_GUI_Component_IDs" "GUI_State_and_Interacted_GUI_Component_IDs")
boosted_queries=("GUI_States" "Interacted_GUI_Component_IDs" "GUI_State_and_Interacted_GUI_Component_IDs"
	"All_GUI_Component_IDs" "GUI_State_and_All_GUI_Component_IDs")
results_folder=results-bug53

for i in ${!screens[@]}; do
	for j in ${!corpus_types[@]}; do
		for k in ${!boosted_queries[@]}; do
			python3 get_filtered_unfiltered_files.py -s ${screens[$i]} \
			-c ${corpus_types[$j]} -q ${boosted_queries[$k]} -r ${results_folder} \
			-ops Filtering+Boosting
		done
		python3 get_filtered_unfiltered_files.py -s ${screens[$i]} \
			-c ${corpus_types[$j]} -r ${results_folder} \
			-ops Filtering
	done
done


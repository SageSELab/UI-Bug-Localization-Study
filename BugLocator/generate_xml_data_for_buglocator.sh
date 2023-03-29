export preprocessedDataPath=../data/PreprocessedData
export query_reformulation_list=("GUI_States" "Interacted_GUI_Component_IDs" "GUI_State_and_Interacted_GUI_Component_IDs" 
	"All_GUI_Component_IDs" "GUI_State_and_All_GUI_Component_IDs")
export screen_list=("2" "3" "4")
export generated_data_path=../data/PreprocessedData/BugLocatorQueries-round7
export jsonFilePath=../data/JSON-Files-All

for k in ${!query_reformulation_list[@]}; do
	for l in ${!screen_list[@]}; do 
		echo "Generate Data: Q-${query_reformulation_list[$k]}#S-${screen_list[$l]}"
		python3 generateXMLData.py \
			-q ${query_reformulation_list[$k]} -s ${screen_list[$l]}  \
            -prep_data $preprocessedDataPath -gen_data $generated_data_path \
            -jpath $jsonFilePath
	done
done
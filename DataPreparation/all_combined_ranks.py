from helpers_code_mapping import CodeMappingHelper
from write_results import WriteResults

from calculate_metrics import CalculateMetrics
from file_analysis import FileAnalysis
from call_graph import CallGraph
from read_files import ReadFiles
from filtered_files_ranking import FilteredFilesRanking
from get_ranking_of_corpus import Corpus
from get_filtered_unfiltered_files import SoureCodeMapping

class AllCombinedRanks:
	def __init__(self):
		self.codeMappingHelper = CodeMappingHelper()
		self.writeResults = WriteResults()
		self.calculateMetrics = CalculateMetrics()
		self.fileAnalysis = FileAnalysis()
		self.callGraph = CallGraph()
		self.readFiles = ReadFiles()
		self.filteredFilesRanking = FilteredFilesRanking()
		self.corpus = Corpus()

		self.combined_result_file = "results/Boosting-GUI+Interacted-Final.csv"  
		self.sentence_transformers_list_file = "results/Files_Ranked_Based_On_Sentence_Transformers.csv"
		self.replaced_query_list_file = "results/Files_Ranked_Based_On_Replaced_Query.csv"
		self.query_expansion_one_list_file = "results/Files_Ranked_Based_On_Query_Expansion_One.csv"
		self.query_expansion_two_list_file = "results/Files_Ranked_Based_On_Query_Expansion_Two.csv"
		self.query_expansion_three_list_file = "results/Files_Ranked_Based_On_Query_Expansion_Three.csv"

		self.requiredFiles = SoureCodeMapping()
		self.query_name = self.requiredFiles.get_query_name()



	def main(self):
		bug_ids_states = [("2",41), ("8",14), ("10",15), ("18",21), ("19",5), ("44",21),
                ("53",18), ("71",10), ("117",11), ("128",28), ("129", 33), ("130",2),
                ("135",14), ("191",1), ("201",11), ("206",14), ("209",50), ("256",19),
                ("1073",8), ("1096",14), ("1146",6),
                ("1147",7), ("1151",5), ("1202",11), ("1205",22), ("1207",13),
                ("1214",13), ("1215",31), ("1223",81), ("1224",39),
                ("1226",45), ("1299",20), ("1399",14), ("1406",20), ("1430",21), ("1441",18),
                ("1445",14), ("1481",16), ("1645",6),
                #new ones
                ("45",22), ("54",10), ("76",6), ("92",4), ("101",8),("106",11),("110",5),
                ("158",10), ("160",14), ("162",6), ("168",3), ("192",12),("198",120),("199",11),
                ("200",9), ("248",45), ("1150",11), ("1198",20),
                ("1228",24),("1389",2),("1425",18),("1446",18),("1563",7),("1568",8),("1641",9)]

		filtered_corpus_flag = self.requiredFiles.get_corpus_flag()

		bug_id_list = []
		number_of_buggy_files_list = []
		len_java_files_list = []

		number_of_all_gui_comp_id_related_files = []
		number_of_files_in_corpus = []
		number_of_java_buggy_files_list = []
		number_of_filtered_files = []
		ranks_of_buggy_files_among_filtered_files = []
		number_of_buggy_files_among_filtered_files = []

		buggy_files_ranks_on_sentence_transformers = []
		best_buggy_files_ranks_on_sentence_transformers = []
		filtered_files_ranks_on_sentence_transformers = []
		best_filtered_files_ranks_on_sentence_transformers = []

		buggy_files_ranks_on_replaced_query = []
		best_buggy_files_ranks_on_replaced_query = []
		filtered_files_ranks_on_replaced_query = []
		best_filtered_files_ranks_on_replaced_query = []

		buggy_files_ranks_on_query_expansion_one = []
		best_buggy_files_ranks_on_query_expansion_one = []
		filtered_files_ranks_on_query_expansion_one = []
		best_filtered_files_ranks_on_query_expansion_one = []

		buggy_files_ranks_on_query_expansion_two = []
		best_buggy_files_ranks_on_query_expansion_two = []
		filtered_files_ranks_on_query_expansion_two = []
		best_filtered_files_ranks_on_query_expansion_two = []

		buggy_files_ranks_on_query_expansion_three = []
		best_buggy_files_ranks_on_query_expansion_three = []
		filtered_files_ranks_on_query_expansion_three = []
		best_filtered_files_ranks_on_query_expansion_three = []


		for issue_id, app_final_state in bug_ids_states:
			bug_id = issue_id
			bug_id_list.append(bug_id)
			print(bug_id)
			number_of_buggy_files_list.append(len(self.readFiles.get_buggy_files(bug_id)) if self.readFiles.get_buggy_files(bug_id) else "")

			all_java_files = self.readFiles.get_all_java_files(bug_id)
			len_java_files_list.append(len(all_java_files) if all_java_files else "")

			if filtered_corpus_flag == True:
				gui_comp_id_related_files = self.readFiles.get_all_component_id_related_files(bug_id, self.corpus.get_all_component_ids(bug_id))
				number_of_all_gui_comp_id_related_files.append(len(gui_comp_id_related_files))
				number_of_files_in_corpus.append(len(self.readFiles.get_filtered_files(bug_id))+len(self.readFiles.get_unfiltered_files(bug_id)))

			buggy_java_files = self.readFiles.get_buggy_java_files(bug_id)
			number_of_java_buggy_files_list.append(len(buggy_java_files) if buggy_java_files else "")

			#filtered_files = self.readFiles.get_filtered_files(bug_id)
			filtered_files = []
			number_of_filtered_files.append(len(filtered_files))

			buggy_files_on_filtered_files = self.filteredFilesRanking.rank_buggy_files_in_filtered_files(bug_id, filtered_files, buggy_java_files)
			ranks_of_buggy_files_among_filtered_files.append(buggy_files_on_filtered_files)

			number_of_buggy_files_among_filtered_files.append(len(buggy_files_on_filtered_files) if buggy_files_on_filtered_files else "")

			buggy_files_on_sentence_transformers, buggy_files_on_replaced_query, buggy_files_on_query_expansion_one, buggy_files_on_query_expansion_two, buggy_files_on_query_expansion_three = self.filteredFilesRanking.rank_buggy_files(bug_id, self.sentence_transformers_list_file, self.replaced_query_list_file, self.query_expansion_one_list_file, self.query_expansion_two_list_file, self.query_expansion_three_list_file)

			buggy_files_ranks_on_sentence_transformers.append(buggy_files_on_sentence_transformers)
			best_buggy_files_ranks_on_sentence_transformers.append(min(buggy_files_on_sentence_transformers) if buggy_files_on_sentence_transformers else "")

			buggy_files_ranks_on_replaced_query.append(buggy_files_on_replaced_query)
			best_buggy_files_ranks_on_replaced_query.append(min(buggy_files_on_replaced_query) if buggy_files_on_replaced_query else "")

			buggy_files_ranks_on_query_expansion_one.append(buggy_files_on_query_expansion_one)
			best_buggy_files_ranks_on_query_expansion_one.append(min(buggy_files_on_query_expansion_one) if buggy_files_on_query_expansion_one else "")

			buggy_files_ranks_on_query_expansion_two.append(buggy_files_on_query_expansion_two)
			best_buggy_files_ranks_on_query_expansion_two.append(min(buggy_files_on_query_expansion_two) if buggy_files_on_query_expansion_two else "")

			buggy_files_ranks_on_query_expansion_three.append(buggy_files_on_query_expansion_three)
			best_buggy_files_ranks_on_query_expansion_three.append(min(buggy_files_on_query_expansion_three) if buggy_files_on_query_expansion_three else "")

			filtered_files_on_sentence_transformers, filtered_files_on_replaced_query, filtered_files_on_query_expansion_one, filtered_files_on_query_expansion_two, filtered_files_on_query_expansion_three = self.filteredFilesRanking.rank_filtered_files(bug_id, self.sentence_transformers_list_file, self.replaced_query_list_file, self.query_expansion_one_list_file, self.query_expansion_two_list_file, self.query_expansion_three_list_file)

			# filtered_files_on_sentence_transformers= []
			# filtered_files_on_replaced_query=[]
			# filtered_files_on_query_expansion_one=[] 
			# filtered_files_on_query_expansion_two=[] 
			# filtered_files_on_query_expansion_three = []
			
			filtered_files_ranks_on_sentence_transformers.append(filtered_files_on_sentence_transformers)
			best_filtered_files_ranks_on_sentence_transformers.append(min(filtered_files_on_sentence_transformers) if filtered_files_on_sentence_transformers else "")

			filtered_files_ranks_on_replaced_query.append(filtered_files_on_replaced_query)
			best_filtered_files_ranks_on_replaced_query.append(min(filtered_files_on_replaced_query) if filtered_files_on_replaced_query else "")

			filtered_files_ranks_on_query_expansion_one.append(filtered_files_on_query_expansion_one)
			best_filtered_files_ranks_on_query_expansion_one.append(min(filtered_files_on_query_expansion_one) if filtered_files_on_query_expansion_one else "")

			filtered_files_ranks_on_query_expansion_two.append(filtered_files_on_query_expansion_two)
			best_filtered_files_ranks_on_query_expansion_two.append(min(filtered_files_on_query_expansion_two) if filtered_files_on_query_expansion_two else "")

			filtered_files_ranks_on_query_expansion_three.append(filtered_files_on_query_expansion_three)
			best_filtered_files_ranks_on_query_expansion_three.append(min(filtered_files_on_query_expansion_three) if filtered_files_on_query_expansion_three else "")

		if filtered_corpus_flag == False:
			self.writeResults.write_header_for_combined_result(self.combined_result_file, self.query_name)
			self.writeResults.write_multiple_lists_to_file(self.combined_result_file, bug_id_list, number_of_buggy_files_list, len_java_files_list, 
				number_of_java_buggy_files_list, number_of_filtered_files, ranks_of_buggy_files_among_filtered_files,
				number_of_buggy_files_among_filtered_files, 
				buggy_files_ranks_on_sentence_transformers, best_buggy_files_ranks_on_sentence_transformers,
				filtered_files_ranks_on_sentence_transformers, best_filtered_files_ranks_on_sentence_transformers,
				buggy_files_ranks_on_replaced_query, best_buggy_files_ranks_on_replaced_query,
				filtered_files_ranks_on_replaced_query, best_filtered_files_ranks_on_replaced_query,
				buggy_files_ranks_on_query_expansion_one, best_buggy_files_ranks_on_query_expansion_one,
				filtered_files_ranks_on_query_expansion_one, best_filtered_files_ranks_on_query_expansion_one,
				buggy_files_ranks_on_query_expansion_two, best_buggy_files_ranks_on_query_expansion_two,
				filtered_files_ranks_on_query_expansion_two, best_filtered_files_ranks_on_query_expansion_two,
				buggy_files_ranks_on_query_expansion_three, best_buggy_files_ranks_on_query_expansion_three,
				filtered_files_ranks_on_query_expansion_three, best_filtered_files_ranks_on_query_expansion_three)
		else:
			self.writeResults.write_header_for_combined_result_corpus_filtered(self.combined_result_file, self.query_name)
			self.writeResults.write_multiple_lists_to_file_corpus_filtered(self.combined_result_file, bug_id_list, number_of_buggy_files_list, 
				len_java_files_list, number_of_all_gui_comp_id_related_files, number_of_files_in_corpus,
				number_of_java_buggy_files_list, number_of_filtered_files, ranks_of_buggy_files_among_filtered_files,
				number_of_buggy_files_among_filtered_files, 
				buggy_files_ranks_on_sentence_transformers, best_buggy_files_ranks_on_sentence_transformers,
				filtered_files_ranks_on_sentence_transformers, best_filtered_files_ranks_on_sentence_transformers,
				buggy_files_ranks_on_replaced_query, best_buggy_files_ranks_on_replaced_query,
				filtered_files_ranks_on_replaced_query, best_filtered_files_ranks_on_replaced_query,
				buggy_files_ranks_on_query_expansion_one, best_buggy_files_ranks_on_query_expansion_one,
				filtered_files_ranks_on_query_expansion_one, best_filtered_files_ranks_on_query_expansion_one,
				buggy_files_ranks_on_query_expansion_two, best_buggy_files_ranks_on_query_expansion_two,
				filtered_files_ranks_on_query_expansion_two, best_filtered_files_ranks_on_query_expansion_two,
				buggy_files_ranks_on_query_expansion_three, best_buggy_files_ranks_on_query_expansion_three,
				filtered_files_ranks_on_query_expansion_three, best_filtered_files_ranks_on_query_expansion_three)


if __name__ == '__main__':
	allCombinedRanks = AllCombinedRanks()
	allCombinedRanks.main()

from read_files import ReadFiles
from file_analysis import FileAnalysis
from get_ranking_of_corpus import Corpus
from calculate_metrics import CalculateMetrics

class FilteredFilesRanking:
	def __init__(self):
		self.readFiles = ReadFiles()
		self.fileAnalysis = FileAnalysis()
		self.corpus = Corpus()
		self.calculateMetrics = CalculateMetrics()

	#Slice full path of a filename starting from "bug"
	def filePath_slice_starting_from_bug(self, bug_id, filePathList):
		ranked_corpus = []
		for filepath in filePathList:
			bug_id_index = filepath.find("bug-"+bug_id)
			filepath = filepath[bug_id_index:]
			ranked_corpus.append(filepath)

		return ranked_corpus

	def rank_buggy_files_in_one_configuration(self, bug_id, corpus_filename, to_be_ranked_files):
		ranked_corpus = self.readFiles.get_ranked_files(bug_id, corpus_filename)
		ranked_corpus = self.filePath_slice_starting_from_bug(bug_id, ranked_corpus)
		to_be_ranked_files = self.filePath_slice_starting_from_bug(bug_id, to_be_ranked_files)

		ranks = self.get_ranking(ranked_corpus, to_be_ranked_files)
		return ranks

	def get_ranking(self,ranked_corpus, to_be_ranked_files):
		ranks = [] 
		for i in range(len(ranked_corpus)):
			if ranked_corpus[i] in to_be_ranked_files:
				ranks.append(i+1)

		ranks.sort()
		return ranks

	def rank_buggy_files_in_filtered_files(self, bug_id, filtered_files, buggy_java_files):
		bug_report_contents = self.readFiles.get_bug_report_contents(bug_id)

		replaced_query = self.corpus.query_replacement(bug_id)
		#filtered_files_ranked_based_on_replaced_query, replaced_query_similarity_scores = self.calculateMetrics.get_class_ranks_from_similarity_scores(replaced_query, filtered_files)
		filtered_files = self.filePath_slice_starting_from_bug(bug_id, filtered_files)
		buggy_java_files = self.filePath_slice_starting_from_bug(bug_id, buggy_java_files)

		buggy_files_ranking_on_filtered_files = self.get_ranking(filtered_files, buggy_java_files)
		return buggy_files_ranking_on_filtered_files

	#files_to_be_ranked will be ranked for different query configurations
	def rank_files_different_configurations(self, bug_id, files_to_be_ranked, sentence_transformers_list_file, replaced_query_list_file, query_expansion_one_list_file, query_expansion_two_list_file, query_expansion_three_list_file):
		to_be_ranked_files_ranking_on_sentence_transformers_files_ranks = self.rank_buggy_files_in_one_configuration(bug_id, sentence_transformers_list_file, files_to_be_ranked)
		to_be_ranked_files_ranking_on_replaced_query_files_ranks = self.rank_buggy_files_in_one_configuration(bug_id, replaced_query_list_file, files_to_be_ranked)
		to_be_ranked_files_ranking_on_query_expansion_one_list_files_ranks = self.rank_buggy_files_in_one_configuration(bug_id, query_expansion_one_list_file, files_to_be_ranked)
		to_be_ranked_files_ranking_on_query_expansion_two_list_files_ranks = self.rank_buggy_files_in_one_configuration(bug_id, query_expansion_two_list_file, files_to_be_ranked)
		to_be_ranked_files_ranking_on_query_expansion_three_list_files_ranks = self.rank_buggy_files_in_one_configuration(bug_id, query_expansion_three_list_file, files_to_be_ranked)

		return to_be_ranked_files_ranking_on_sentence_transformers_files_ranks, to_be_ranked_files_ranking_on_replaced_query_files_ranks, to_be_ranked_files_ranking_on_query_expansion_one_list_files_ranks, to_be_ranked_files_ranking_on_query_expansion_two_list_files_ranks, to_be_ranked_files_ranking_on_query_expansion_three_list_files_ranks

	def rank_buggy_files(self, bug_id, sentence_transformers_list_file, replaced_query_list_file, query_expansion_one_list_file, query_expansion_two_list_file, query_expansion_three_list_file):
		buggy_java_files = self.readFiles.get_buggy_java_files(bug_id)
		return self.rank_files_different_configurations(bug_id, buggy_java_files, sentence_transformers_list_file, replaced_query_list_file, query_expansion_one_list_file, query_expansion_two_list_file, query_expansion_three_list_file)

	def rank_filtered_files(self, bug_id, sentence_transformers_list_file, replaced_query_list_file, query_expansion_one_list_file, query_expansion_two_list_file, query_expansion_three_list_file):
		filtered_files = self.readFiles.get_filtered_files(bug_id)
		return self.rank_files_different_configurations(bug_id, filtered_files, sentence_transformers_list_file, replaced_query_list_file, query_expansion_one_list_file, query_expansion_two_list_file, query_expansion_three_list_file)

	def main(self):
		bug_ids_states = [("2",41)]
		for issue_id, app_final_state in bug_ids_states:
			bug_id = issue_id
			buggy_files_on_sentence_transformers, buggy_files_on_replaced_query, buggy_files_on_query_expansion_one, buggy_files_on_query_expansion_two, buggy_files_on_query_expansion_three = self.rank_buggy_files(bug_id)

			filtered_files_on_sentence_transformers, filtered_files_on_replaced_query, filtered_files_on_query_expansion_one, filtered_files_on_query_expansion_two, filtered_files_on_query_expansion_three = self.rank_filtered_files(bug_id)



if __name__ == '__main__':
    filteredFilesRanking = FilteredFilesRanking()
    filteredFilesRanking.main()

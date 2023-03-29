import csv

class WriteResults:
	def write_to_csv(self, write_file, row):
	    with open(write_file, 'a') as file:
	        writer = csv.writer(file)
	        writer.writerow(row)

	def write_header_for_query(self, filename):
		with open(filename, 'w') as file:
			writer = csv.writer(file)
			writer.writerow(["Bug Report ID", "Activities", "Fragments", "Interacted Component IDs", "All Component IDs"])

	def write_row_for_query(self, filename, bug_id, activities, fragments, interacted_comp_ids, all_component_ids):
		result_row=[]
		result_row.append(bug_id)
		result_row.append(activities)
		result_row.append(fragments)
		result_row.append(interacted_comp_ids)
		result_row.append(all_component_ids)
		self.write_to_csv(filename, result_row)

	def write_header_for_file_list(self, filename):
		with open(filename, 'w') as file:
			writer = csv.writer(file)
			writer.writerow(["Bug Report ID", "FilePaths", "File Source"])

	def write_file_list_each_row(self, bug_id, files, filename, fileSource):
		for i in range(len(files)):
			result_row=[]
			result_row.append(bug_id)
			result_row.append(files[i])
			result_row.append(fileSource)
			self.write_to_csv(filename, result_row)

	def write_header_for_file_list_sim_scores(self, filename):
		with open(filename, 'w') as file:
			writer = csv.writer(file)
			writer.writerow(["Bug Report ID", "FilePaths", "File Source", "Cosine Similarity Scores"])

	def write_file_list_each_row_sim_scores(self, bug_id, files, filename, fileSource, cos_sim_scores):
		for i in range(len(files)):
			result_row=[]
			result_row.append(bug_id)
			result_row.append(files[i])
			result_row.append(fileSource)
			result_row.append(cos_sim_scores[i])
			self.write_to_csv(filename, result_row)

	def write_header_for_metrics(self, filename):
		with open(filename, 'w') as file:
			writer = csv.writer(file)
			# writer.writerow(["Bug Report ID", "Ranks", 
   #              "Hit@1", "RR@1", "AP@1", "Hit@3", "RR@3", "AP@3", "Hit@5", "RR@5", "AP@5", "Hit@10", "RR@10", "AP@10",
   #              "Hit@15", "RR@15", "AP@15", "Hit@20", "RR@20", "AP@20", "Hit@50", "RR@50", "AP@50"])
			writer.writerow(["Bug Report ID", "Ranks", 
                "Hit@1", "Hit@5", "Hit@10", "Hit@20", "Hit@50", "MRR@1", "MRR@5", "MRR@10", "MRR@20", "MRR@50", 
                "MAP@1", "MAP@5", "MAP@10",
                "MAP@20",  "MAP@50"])

	def write_metric_result_lists_to_file(self, filename, bug_ids, rankList, K_values, hit_K_values, rr_K_values, ap_K_values):
		for i in range(len(bug_ids)):
			result_row = []
			result_row.append(bug_ids[i])
			result_row.append(rankList[i])
			for j in range(len(K_values)):
				result_row.append(hit_K_values[i][j])
			for j in range(len(K_values)):
				result_row.append(rr_K_values[i][j])
			for j in range(len(K_values)):
				result_row.append(ap_K_values[i][j])
			self.write_to_csv(filename, result_row)

	def write_header_for_combined_result(self, filename, type_of_file):
		with open(filename, 'w') as file:
			writer = csv.writer(file)
			writer.writerow(["Bug Report ID", "# of Buggy Files in Groud Truth", "# Java Files in Project", "# Buggy Java Files", 
			    "# of " + type_of_file + " Related Files", "Ranks of Buggy Files Among the " + type_of_file + " Related Files", 
			    "# of Buggy Files Among the " + type_of_file + " Related Files", 
			    "Ranks (Query-Bug Report)",
			    "Best Ranking of Buggy files among files that are ranked based on BASELINE - Sentence Transformers",
			    "Ranking of "+ type_of_file + " Related files among files that are ranked based on BASELINE - Sentence Transformers",
			    "Best Ranking of "+ type_of_file + " Related files among files that are ranked based on BASELINE - Sentence Transformers",
			    "Ranks (Query Replacement)",
			    "Best Ranking of Buggy Files (Query Replacement: use " + type_of_file + " as query)",
			    "Ranking of " + type_of_file + " Relevant Files (Query Replacement)",
			    "Best Ranking of " + type_of_file + " Relevant Files (Query Replacement)",
			    "Ranks (Query Expansion 1)", "Best Ranking of Buggy Files (Query Expansion 1st configuration)",
			    "Ranking of "+ type_of_file + " Relevant Files (Query Expansion 1st configuration)",
			    "Best Ranking of "+ type_of_file + " Relevant Files (Query Expansion 1st configuration)",
			    "Ranks (Query Expansion 2)", "Best Ranking of Buggy Files (Query Expansion 2nd configuration)",
			    "Ranking of "+ type_of_file + " Relevant Files (Query Expansion 2nd configuration)",
			    "Best Ranking of "+ type_of_file + " Relevant Files (Query Expansion 2nd configuration)",
			    "Ranks (Query Expansion 3)", "Best Ranking of Buggy Files (Query Expansion 3rd configuration)",
			    "Ranking of "+ type_of_file + " Relevant Files (Query Expansion 3rd configuration)",
			    "Best Ranking of "+ type_of_file + " Relevant Files (Query Expansion 3rd configuration)"])

	def write_multiple_lists_to_file(self, filename, bug_id_list, number_of_buggy_files_list, len_java_files_list, 
			number_of_java_buggy_files_list, number_of_filtered_files, ranks_of_buggy_files_among_filtered_files,
			number_of_buggy_files_among_filtered_files, buggy_files_ranks_on_sentence_transformers, best_buggy_files_ranks_on_sentence_transformers,
			filtered_files_ranks_on_sentence_transformers, best_filtered_files_ranks_on_sentence_transformers,
			buggy_files_ranks_on_replaced_query, best_buggy_files_ranks_on_replaced_query,
			filtered_files_ranks_on_replaced_query, best_filtered_files_ranks_on_replaced_query,
			buggy_files_ranks_on_query_expansion_one, best_buggy_files_ranks_on_query_expansion_one,
			filtered_files_ranks_on_query_expansion_one, best_filtered_files_ranks_on_query_expansion_one,
			buggy_files_ranks_on_query_expansion_two, best_buggy_files_ranks_on_query_expansion_two,
			filtered_files_ranks_on_query_expansion_two, best_filtered_files_ranks_on_query_expansion_two,
			buggy_files_ranks_on_query_expansion_three, best_buggy_files_ranks_on_query_expansion_three,
			filtered_files_ranks_on_query_expansion_three, best_filtered_files_ranks_on_query_expansion_three):

		for i in range(len(bug_id_list)):
			result_row = []
			result_row.append(bug_id_list[i])
			result_row.append(number_of_buggy_files_list[i])
			result_row.append(len_java_files_list[i])
			result_row.append(number_of_java_buggy_files_list[i])
			result_row.append(number_of_filtered_files[i])
			result_row.append(ranks_of_buggy_files_among_filtered_files[i])
			result_row.append(number_of_buggy_files_among_filtered_files[i])
			result_row.append(buggy_files_ranks_on_sentence_transformers[i])
			result_row.append(best_buggy_files_ranks_on_sentence_transformers[i])
			result_row.append(filtered_files_ranks_on_sentence_transformers[i])
			result_row.append(best_filtered_files_ranks_on_sentence_transformers[i])
			result_row.append(buggy_files_ranks_on_replaced_query[i])
			result_row.append(best_buggy_files_ranks_on_replaced_query[i])
			result_row.append(filtered_files_ranks_on_replaced_query[i])
			result_row.append(best_filtered_files_ranks_on_replaced_query[i])
			result_row.append(buggy_files_ranks_on_query_expansion_one[i])
			result_row.append(best_buggy_files_ranks_on_query_expansion_one[i])
			result_row.append(filtered_files_ranks_on_query_expansion_one[i])
			result_row.append(best_filtered_files_ranks_on_query_expansion_one[i])
			result_row.append(buggy_files_ranks_on_query_expansion_two[i])
			result_row.append(best_buggy_files_ranks_on_query_expansion_two[i])
			result_row.append(filtered_files_ranks_on_query_expansion_two[i])
			result_row.append(best_filtered_files_ranks_on_query_expansion_two[i])
			result_row.append(buggy_files_ranks_on_query_expansion_three[i])
			result_row.append(best_buggy_files_ranks_on_query_expansion_three[i])
			result_row.append(filtered_files_ranks_on_query_expansion_three[i])
			result_row.append(best_filtered_files_ranks_on_query_expansion_three[i])
			self.write_to_csv(filename, result_row)


	def write_header_for_combined_result_corpus_filtered(self, filename, type_of_file):
		with open(filename, 'w') as file:
			writer = csv.writer(file)
			writer.writerow(["Bug Report ID", "# of Buggy Files in Groud Truth", "# Java Files in Project", "# of files where any GUI component id exist",
				"# of files in corpus (Unique files among the query matched files and files where any component id exists)", "# Buggy Java Files", 
			    "# of " + type_of_file + " Related Files", "Ranks of Buggy Files Among the " + type_of_file + " Related Files", 
			    "# of Buggy Files Among the " + type_of_file + " Related Files", 
			    "Ranking of Buggy files among files that are ranked based on BASELINE - Sentence Transformers",
			    "Best Ranking of Buggy files among files that are ranked based on BASELINE - Sentence Transformers",
			    "Ranking of "+ type_of_file + " Related files among files that are ranked based on BASELINE - Sentence Transformers",
			    "Best Ranking of "+ type_of_file + " Related files among files that are ranked based on BASELINE - Sentence Transformers",
			    "Ranking of Buggy Files (Query Replacement: use " + type_of_file + " as query)",
			    "Best Ranking of Buggy Files (Query Replacement: use " + type_of_file + " as query)",
			    "Ranking of " + type_of_file + " Relevant Files (Query Replacement)",
			    "Best Ranking of " + type_of_file + " Relevant Files (Query Replacement)",
			    "Ranking of Buggy Files (Query Expansion 1st configuration)", "Best Ranking of Buggy Files (Query Expansion 1st configuration)",
			    "Ranking of "+ type_of_file + " Relevant Files (Query Expansion 1st configuration)",
			    "Best Ranking of "+ type_of_file + " Relevant Files (Query Expansion 1st configuration)",
			    "Ranking of Buggy Files (Query Expansion 2nd configuration)", "Best Ranking of Buggy Files (Query Expansion 2nd configuration)",
			    "Ranking of "+ type_of_file + " Relevant Files (Query Expansion 2nd configuration)",
			    "Best Ranking of "+ type_of_file + " Relevant Files (Query Expansion 2nd configuration)",
			    "Ranking of Buggy Files (Query Expansion 3rd configuration)", "Best Ranking of Buggy Files (Query Expansion 3rd configuration)",
			    "Ranking of "+ type_of_file + " Relevant Files (Query Expansion 3rd configuration)",
			    "Best Ranking of "+ type_of_file + " Relevant Files (Query Expansion 3rd configuration)"])

	def write_multiple_lists_to_file_corpus_filtered(self, filename, bug_id_list, number_of_buggy_files_list, len_java_files_list, 
			all_comp_id_related_files, number_of_files_in_corpus,
			number_of_java_buggy_files_list, number_of_filtered_files, ranks_of_buggy_files_among_filtered_files,
			number_of_buggy_files_among_filtered_files, buggy_files_ranks_on_sentence_transformers, best_buggy_files_ranks_on_sentence_transformers,
			filtered_files_ranks_on_sentence_transformers, best_filtered_files_ranks_on_sentence_transformers,
			buggy_files_ranks_on_replaced_query, best_buggy_files_ranks_on_replaced_query,
			filtered_files_ranks_on_replaced_query, best_filtered_files_ranks_on_replaced_query,
			buggy_files_ranks_on_query_expansion_one, best_buggy_files_ranks_on_query_expansion_one,
			filtered_files_ranks_on_query_expansion_one, best_filtered_files_ranks_on_query_expansion_one,
			buggy_files_ranks_on_query_expansion_two, best_buggy_files_ranks_on_query_expansion_two,
			filtered_files_ranks_on_query_expansion_two, best_filtered_files_ranks_on_query_expansion_two,
			buggy_files_ranks_on_query_expansion_three, best_buggy_files_ranks_on_query_expansion_three,
			filtered_files_ranks_on_query_expansion_three, best_filtered_files_ranks_on_query_expansion_three):

		for i in range(len(bug_id_list)):
			result_row = []
			result_row.append(bug_id_list[i])
			result_row.append(number_of_buggy_files_list[i])
			result_row.append(len_java_files_list[i])
			result_row.append(all_comp_id_related_files[i])
			result_row.append(number_of_files_in_corpus[i])
			result_row.append(number_of_java_buggy_files_list[i])
			result_row.append(number_of_filtered_files[i])
			result_row.append(ranks_of_buggy_files_among_filtered_files[i])
			result_row.append(number_of_buggy_files_among_filtered_files[i])
			result_row.append(buggy_files_ranks_on_sentence_transformers[i])
			result_row.append(best_buggy_files_ranks_on_sentence_transformers[i])
			result_row.append(filtered_files_ranks_on_sentence_transformers[i])
			result_row.append(best_filtered_files_ranks_on_sentence_transformers[i])
			result_row.append(buggy_files_ranks_on_replaced_query[i])
			result_row.append(best_buggy_files_ranks_on_replaced_query[i])
			result_row.append(filtered_files_ranks_on_replaced_query[i])
			result_row.append(best_filtered_files_ranks_on_replaced_query[i])
			result_row.append(buggy_files_ranks_on_query_expansion_one[i])
			result_row.append(best_buggy_files_ranks_on_query_expansion_one[i])
			result_row.append(filtered_files_ranks_on_query_expansion_one[i])
			result_row.append(best_filtered_files_ranks_on_query_expansion_one[i])
			result_row.append(buggy_files_ranks_on_query_expansion_two[i])
			result_row.append(best_buggy_files_ranks_on_query_expansion_two[i])
			result_row.append(filtered_files_ranks_on_query_expansion_two[i])
			result_row.append(best_filtered_files_ranks_on_query_expansion_two[i])
			result_row.append(buggy_files_ranks_on_query_expansion_three[i])
			result_row.append(best_buggy_files_ranks_on_query_expansion_three[i])
			result_row.append(filtered_files_ranks_on_query_expansion_three[i])
			result_row.append(best_filtered_files_ranks_on_query_expansion_three[i])
			self.write_to_csv(filename, result_row)



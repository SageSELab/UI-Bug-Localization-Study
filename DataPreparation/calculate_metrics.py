from helpers_code_mapping import CodeMappingHelper
from file_analysis import FileAnalysis
from write_results import WriteResults
from read_files import ReadFiles

from ast import literal_eval

import json
import math

class CalculateMetrics:
	def __init__(self):
		self.codeMappingHelper = CodeMappingHelper()
		self.fileAnalysis = FileAnalysis()
		self.writeResults = WriteResults()
		self.readFiles = ReadFiles()

	def calculate_topK(self, ranks, K):
	    for rank in ranks:
	        if rank<=K:
	            return 1
	    return 0

	# Calculate mean receiprocal rank@K (MRR@K)
	def calculate_RR(self, ranks, K):
	    first_rank = 0
	    for rank in ranks:
	        if rank <= K:
	            first_rank = 1/rank
	            break

	    return first_rank

	# Calculate hit@K
	def calculate_hitK(self, ranks, K):
	    hit = 0
	    for rank in ranks:
	        if rank <= K:
	            hit = 1 
	            break
	    return hit

	# Calculate average precision@K (AP@K)
	def calculate_average_precisionK(self, ranks, K, bug_id):
	    buggy_k = 0
	    precision_k = 0
	    buggy_count = 0
	    total_precision_k = 0
	    # Check all the ranks from 1 to K
	    for rank in range(1, K+1):
	        if rank in ranks:
	            buggy_k = 1
	            buggy_count += 1
	        else:
	            buggy_k = 0

	        precision_k = buggy_count / rank
	        total_precision_k += precision_k * buggy_k

	    total_number_of_buggy_files = len(self.readFiles.get_buggy_java_files(bug_id))

	    if total_number_of_buggy_files==0:
	        return 0

	    average_precision_k = total_precision_k / total_number_of_buggy_files
	    return average_precision_k

	def calculate_average_precisionK_gui_state_files(self, ranks, K, gui_state_files):
	    buggy_k = 0
	    precision_k = 0
	    buggy_count = 0
	    total_precision_k = 0
	    # Check all the ranks from 1 to K
	    for rank in range(1, K+1):
	        if rank in ranks:
	            buggy_k = 1
	            buggy_count += 1
	        else:
	            buggy_k = 0

	        precision_k = buggy_count / rank
	        total_precision_k += precision_k * buggy_k

	    total_number_of_buggy_files = len(gui_state_files)

	    if total_number_of_buggy_files==0:
	        return 0

	    average_precision_k = total_precision_k / total_number_of_buggy_files
	    return average_precision_k

	# This function will take input as ranks and calculate MRR@K, HIT@K, MAP@K for a bug ID
	def calculate_final_metric_values_file_level_for_bug_id(self, ranks, K, bug_id):
		rr_K = self.calculate_RR(ranks, K)
		hit_K = self.calculate_hitK(ranks, K)
		ap_K = self.calculate_average_precisionK(ranks, K, bug_id)

		return rr_K, hit_K, ap_K

	def calulate_file_metrics_for_all_K(self, rankList, bug_report_ids, K_values):
		rr_list = []
		hit_list = []
		ap_list = []

		for i in range(len(rankList)):
			if rankList[i] is None or rankList[i]!=rankList[i]:
				ranks = []
				rankList[i]="[]"
			ranks = literal_eval(rankList[i])
			bug_id = bug_report_ids[i]

			rr_K_values = []
			hit_K_values = []
			ap_K_values = []
			for k in K_values:
				rr_K, hit_K, ap_K = self.calculate_final_metric_values_file_level_for_bug_id(ranks, k, bug_id)
				rr_K_values.append(rr_K)
				hit_K_values.append(hit_K)
				ap_K_values.append(ap_K)

			rr_list.append(rr_K_values)
			hit_list.append(hit_K_values)
			ap_list.append(ap_K_values)

		return rr_list, hit_list, ap_list

	# Return the ranks of methods based on matches with the original buggy methods
	def rank_methods(self, ranked_classes, ranked_target_methods, original_buggy_locations, unique_method_names):
	    ranks = []
	    set_of_class_methods = []
	    for bug_location in original_buggy_locations["bug_location"]:
	        buggy_file = bug_location["file_name"]
	        buggy_method = bug_location["method_name"]
	        if buggy_method is None or len(buggy_method)==0:
	            continue

	        visited_method_flag = False
	        for class_name, method_name in set_of_class_methods:
	            if buggy_method is not None and len(buggy_method)>0:
	                print("buggy_method")
	                print(buggy_method)
	                print(method_name)
	                if buggy_file in class_name and buggy_method in method_name:
	                #if buggy_method in method_name:
	                    visited_method_flag = True
	                    continue 

	        if visited_method_flag == True:
	            continue

	        set_of_class_methods.append((buggy_file, buggy_method))
	        basename=os.path.basename(buggy_file)
	        basename=basename.split('.')[0]
	        if buggy_method is not None and len(buggy_method)>0:
	            unique_method_names.add(buggy_method)
	            order_number = 1
	            for i in range(len(ranked_target_methods)):  
	                if buggy_method in ranked_target_methods[i]:
	                    print('other methods') 
	                    print(buggy_method)    
	                    print(buggy_file)    
	                    print(ranked_classes[i])         
	                if buggy_method in ranked_target_methods[i] and ranked_classes[i]+".java" in buggy_file:
	                    ranks.append(order_number)
	                    break
	                order_number += 1
	    ranks.sort()
	    return ranks


	def get_method_ranks(self, bug_issue_id, final_classes, predicted_methods, method_result_output_file):
	    print("------------ " + str(bug_issue_id) + ": Ranked Bug Methods -----------------")
	    rank = 1
	    for ranked_target_method in predicted_methods:
	        #print(rank, ranked_target_method)
	        rank += 1

	    ######## Read json file containing the correct bug locations ###########
	    json_file = "../../data/JSON-Files-All/" + str(bug_issue_id) + ".json"
	    with open(json_file, 'r') as jfile:
	        json_data = jfile.read()
	    original_buggy_locations = json.loads(json_data)

	    # Ranks of correct bug locations in the result
	    unique_method_names = set()
	    ranks = self.rank_methods(final_classes, predicted_methods, original_buggy_locations, unique_method_names)
	    print('rank')
	    print(ranks)

	    result_row = []
	    result_row.append(bug_issue_id)
	    result_row.append(len(unique_method_names))
	    result_row.append(unique_method_names)
	    result_row.append(ranks)

	    top_1 = self.calculate_topK(ranks, 1)
	    top_3 = self.calculate_topK(ranks, 3)
	    top_5 = self.calculate_topK(ranks, 5)

	    fr = 1e9
	    ar = 1e9
	    if len(ranks)>0:
	        fr = ranks[0]
	        ar = np.mean(ranks)

	    result_row.append(top_1)
	    result_row.append(top_3)
	    result_row.append(top_5)
	    result_row.append(fr)
	    result_row.append(ar)
	    
	    self.writeResults.write_to_csv(method_result_output_file, result_row)

	# Rank files based on similarity scores
	def get_class_ranks_from_similarity_scores(self, bug_id, bug_report_contents, import_classes):
	    all_class_contents = []
	    class_names = []
	    for import_class in import_classes:
	    	print(import_class)
	    	class_content = self.readFiles.get_code_processed(bug_id, import_class)
	    	class_names.append(import_class)
	    	all_class_contents.append(class_content)

	    class_cos_similarities = self.codeMappingHelper.get_preprocessed_file_cos_similarity_scores(bug_report_contents, all_class_contents)
	    print(class_cos_similarities)

	    class_similarity_scores = []
	    for ind in range(len(class_cos_similarities)):
	        class_similarity_scores.append((class_names[ind], class_cos_similarities[ind]))

	    class_similarity_scores.sort(key=lambda y:y[1], reverse=True)

	    ranked_files = []
	    similarity_scores = []
	    for class_name, sim_score in class_similarity_scores:
	        ranked_files.append(class_name)
	        similarity_scores.append(sim_score)
	    return ranked_files, similarity_scores

	def get_method_ranks_from_similarity_scores(self, bug_report_contents, filenames, method_blocks):
	    additional_files = []
	    additional_methods = []
	    if len(method_blocks)>0:
	        method_cos_similarities = self.codeMappingHelper.get_cos_similarity_scores(bug_report_contents, method_blocks)

	        class_method_similarities = []

	        for i in range(len(method_cos_similarities)):
	            class_method_similarities.append((method_blocks[i], method_cos_similarities[i], filenames[i]))

	        class_method_similarities.sort(key=lambda y:(y[1],y[2]), reverse=True)

	        
	        for method_block, similarity_score, inside_file in class_method_similarities:
	            if len(inside_file)>0 and len(method_block)>0:
	                additional_methods.append(method_block)
	                additional_files.append(inside_file)
	    return additional_files, additional_methods

	def main(self):
		K_values = [1, 5, 10, 20, 50]

		ranks_file = "UIBugLocalization/FaultLocalizationCode/BugLocator-organizedCode/TestRs/Filtering+Boosting-GUI-final.csv"
		col_name = "Ranks (Original Bug Report)"
		rankList = self.readFiles.get_ranks_for_all_bugs(ranks_file, col_name)
		bug_report_ids = self.readFiles.get_bug_report_ids(ranks_file)
		print(bug_report_ids)
		bug_report_ids = [int(bug_id) for bug_id in bug_report_ids]
		
		metrics_file = "UIBugLocalization/FaultLocalizationCode/BugLocator-organizedCode/TestRs/metrics-st.csv"
		rr_list, hit_list, ap_list = self.calulate_file_metrics_for_all_K(rankList, bug_report_ids, K_values)
		self.writeResults.write_header_for_metrics(metrics_file)
		self.writeResults.write_metric_result_lists_to_file(metrics_file, bug_report_ids, rankList, K_values, hit_list, rr_list, ap_list)

		col_name = "Ranks (Query Replacement)"
		rankList = self.readFiles.get_ranks_for_all_bugs(ranks_file, col_name)
		metrics_file = "UIBugLocalization/FaultLocalizationCode/BugLocator-organizedCode/TestRs/metrics-rq.csv"
		rr_list, hit_list, ap_list = self.calulate_file_metrics_for_all_K(rankList, bug_report_ids, K_values)
		self.writeResults.write_header_for_metrics(metrics_file)
		self.writeResults.write_metric_result_lists_to_file(metrics_file, bug_report_ids, rankList, K_values, hit_list, rr_list, ap_list)

		col_name = "Ranks (Query Expansion 1)"
		rankList = self.readFiles.get_ranks_for_all_bugs(ranks_file, col_name)
		metrics_file = "UIBugLocalization/FaultLocalizationCode/BugLocator-organizedCode/TestRs/metrics-qe1.csv"
		rr_list, hit_list, ap_list = self.calulate_file_metrics_for_all_K(rankList, bug_report_ids, K_values)
		self.writeResults.write_header_for_metrics(metrics_file)
		self.writeResults.write_metric_result_lists_to_file(metrics_file, bug_report_ids, rankList, K_values, hit_list, rr_list, ap_list)

		col_name = "Ranks (Query Expansion 2)"
		rankList = self.readFiles.get_ranks_for_all_bugs(ranks_file, col_name)
		metrics_file = "UIBugLocalization/FaultLocalizationCode/BugLocator-organizedCode/TestRs/metrics-qe2.csv"
		rr_list, hit_list, ap_list = self.calulate_file_metrics_for_all_K(rankList, bug_report_ids, K_values)
		self.writeResults.write_header_for_metrics(metrics_file)
		self.writeResults.write_metric_result_lists_to_file(metrics_file, bug_report_ids, rankList, K_values, hit_list, rr_list, ap_list)

		col_name = "Ranks (Query Expansion 3)"
		rankList = self.readFiles.get_ranks_for_all_bugs(ranks_file, col_name)
		metrics_file = "UIBugLocalization/FaultLocalizationCode/BugLocator-organizedCode/TestRs/metrics-qe3.csv"
		rr_list, hit_list, ap_list = self.calulate_file_metrics_for_all_K(rankList, bug_report_ids, K_values)
		self.writeResults.write_header_for_metrics(metrics_file)
		self.writeResults.write_metric_result_lists_to_file(metrics_file, bug_report_ids, rankList, K_values, hit_list, rr_list, ap_list)


if __name__ == '__main__':
	calculateMetrics = CalculateMetrics()
	calculateMetrics.main()
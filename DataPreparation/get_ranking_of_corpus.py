from helpers_code_mapping import CodeMappingHelper
from write_results import WriteResults

from calculate_metrics import CalculateMetrics
from file_analysis import FileAnalysis
from call_graph import CallGraph
from read_files import ReadFiles
from get_filtered_unfiltered_files import SoureCodeMapping

from ast import literal_eval

import pandas as pd
import csv

class Corpus:
    def __init__(self):
        self.codeMappingHelper = CodeMappingHelper()
        self.writeResults = WriteResults()
        self.calculateMetrics = CalculateMetrics()
        self.fileAnalysis = FileAnalysis()
        self.callGraph = CallGraph()
        self.readFiles = ReadFiles()
        self.requiredFiles = SoureCodeMapping()

        self.query_df = pd.read_csv("results/Queries.csv")
        self.sentence_transformers_list_file = "results/Files_Ranked_Based_On_Sentence_Transformers.csv" 
        self.replaced_query_list_file = "results/Files_Ranked_Based_On_Replaced_Query.csv"
        self.query_expansion_one_list_file = "results/Files_Ranked_Based_On_Query_Expansion_One.csv"
        self.query_expansion_two_list_file = "results/Files_Ranked_Based_On_Query_Expansion_Two.csv"
        self.query_expansion_three_list_file = "results/Files_Ranked_Based_On_Query_Expansion_Three.csv"

        self.query_name = self.requiredFiles.get_query_name()

    def get_all_component_ids(self, bug_id):
        all_comp_ids = self.query_df.loc[self.query_df['Bug Report ID']==int(bug_id), 'All Component IDs'].item()
        return literal_eval(all_comp_ids)

    def query_replacement(self, bug_id):
        activities = self.query_df.loc[self.query_df['Bug Report ID']==int(bug_id), 'Activities'].item()
        fragments = self.query_df.loc[self.query_df['Bug Report ID']==int(bug_id), 'Fragments'].item()
        interacted_comp_ids = self.query_df.loc[self.query_df['Bug Report ID']==int(bug_id), 'Interacted Component IDs'].item()

        replaced_query_list = []
        if self.query_name == "GUI_State_and_Interacted_GUI_Component_ID":
            replaced_query_list.extend(literal_eval(activities))
            replaced_query_list.extend(literal_eval(fragments))
            replaced_query_list.extend(literal_eval(interacted_comp_ids))

        elif self.query_name == "GUI_State":
            replaced_query_list.extend(literal_eval(activities))
            replaced_query_list.extend(literal_eval(fragments))

        elif self.query_name == "GUI_State_and_All_Component_IDs":
            replaced_query_list.extend(literal_eval(activities))
            replaced_query_list.extend(literal_eval(fragments))
            replaced_query_list.extend(self.get_all_component_ids(bug_id))
        
        replaced_query_list = self.codeMappingHelper.clean_query(replaced_query_list)
        # Converting the replaced query list to a string
        replaced_query = ' '.join(replaced_query_list)

        return replaced_query

    def create_headers_for_all_configurations(self):
        self.writeResults.write_header_for_file_list_sim_scores(self.sentence_transformers_list_file)   
        self.writeResults.write_header_for_file_list_sim_scores(self.replaced_query_list_file)      
        self.writeResults.write_header_for_file_list_sim_scores(self.query_expansion_one_list_file) 
        self.writeResults.write_header_for_file_list_sim_scores(self.query_expansion_two_list_file) 
        self.writeResults.write_header_for_file_list_sim_scores(self.query_expansion_three_list_file)

    #Rank files based on different configurations
    def reformulate_query(self, bug_id, all_java_files):
        bug_report_contents = self.readFiles.get_bug_report_contents_preprocessed(bug_id, self.query_name, "bug_report_original")

        files_ranked_based_on_sentence_transformers, sentence_transformers_similarity_scores = self.calculateMetrics.get_class_ranks_from_similarity_scores(bug_id, bug_report_contents, all_java_files)

        replaced_query = self.readFiles.get_bug_report_contents_preprocessed(bug_id, self.query_name, "replaced_query")

        print("replaced query")
        print(replaced_query)
    
        files_ranked_based_on_replaced_query, replaced_query_similarity_scores = self.calculateMetrics.get_class_ranks_from_similarity_scores(bug_id, replaced_query, all_java_files)

        query_expansion_one = self.readFiles.get_bug_report_contents_preprocessed(bug_id, self.query_name, "query_expansion_1")
        files_ranked_based_on_query_expansion_one, query_expansion_one_similarity_scores = self.calculateMetrics.get_class_ranks_from_similarity_scores(bug_id, query_expansion_one, all_java_files)

        query_expansion_two = self.readFiles.get_bug_report_contents_preprocessed(bug_id, self.query_name, "query_expansion_2")
        files_ranked_based_on_query_expansion_two, query_expansion_two_similarity_scores = self.calculateMetrics.get_class_ranks_from_similarity_scores(bug_id, query_expansion_two, all_java_files)

        query_expansion_three = self.readFiles.get_bug_report_contents_preprocessed(bug_id, self.query_name, "query_expansion_3")
        files_ranked_based_on_query_expansion_three, query_expansion_three_similarity_scores = self.calculateMetrics.get_class_ranks_from_similarity_scores(bug_id, query_expansion_three, all_java_files)

        self.store_ranked_files_after_reformulation(bug_id, files_ranked_based_on_sentence_transformers, sentence_transformers_similarity_scores, files_ranked_based_on_replaced_query, replaced_query_similarity_scores, files_ranked_based_on_query_expansion_one, query_expansion_one_similarity_scores, files_ranked_based_on_query_expansion_two, query_expansion_two_similarity_scores, files_ranked_based_on_query_expansion_three, query_expansion_three_similarity_scores)

    def store_ranked_files_after_reformulation(self, bug_id, files_ranked_based_on_sentence_transformers, sentence_transformers_similarity_scores, files_ranked_based_on_replaced_query, replaced_query_similarity_scores, files_ranked_based_on_query_expansion_one, query_expansion_one_similarity_scores, files_ranked_based_on_query_expansion_two, query_expansion_two_similarity_scores, files_ranked_based_on_query_expansion_three, query_expansion_three_similarity_scores):
        self.writeResults.write_file_list_each_row_sim_scores(bug_id, files_ranked_based_on_sentence_transformers, self.sentence_transformers_list_file, "all", sentence_transformers_similarity_scores)
        self.writeResults.write_file_list_each_row_sim_scores(bug_id, files_ranked_based_on_replaced_query, self.replaced_query_list_file, "all", replaced_query_similarity_scores)
        self.writeResults.write_file_list_each_row_sim_scores(bug_id, files_ranked_based_on_query_expansion_one, self.query_expansion_one_list_file, "all", query_expansion_one_similarity_scores)  
        self.writeResults.write_file_list_each_row_sim_scores(bug_id, files_ranked_based_on_query_expansion_two, self.query_expansion_two_list_file, "all", query_expansion_two_similarity_scores)
        self.writeResults.write_file_list_each_row_sim_scores(bug_id,  files_ranked_based_on_query_expansion_three, self.query_expansion_three_list_file, "all", query_expansion_three_similarity_scores)

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

        self.create_headers_for_all_configurations()
        #bug_ids_states = [("2",41), ("8",14)]
        boosting_flag = True

        for issue_id, app_final_state in bug_ids_states:
            bug_id = issue_id
            
            if boosting_flag == False:
                if self.query_name == False:
                    all_java_files = self.readFiles.get_all_java_files(bug_id)
                    self.reformulate_query(bug_id, all_java_files)
                else:
                    filtered_files = self.readFiles.get_filtered_files(bug_id)
                    unfiltered_files = self.readFiles.get_unfiltered_files(bug_id)
                    filtered_files.extend(unfiltered_files)
                    self.reformulate_query(bug_id, filtered_files)

            elif boosting_flag == True:
                filtered_files = self.readFiles.get_filtered_files(bug_id)
                self.reformulate_query(bug_id, filtered_files)
                unfiltered_files = self.readFiles.get_unfiltered_files(bug_id)
                self.reformulate_query(bug_id, unfiltered_files)

            # all_comp_id_related_files = self.readFiles.get_all_component_id_related_files(bug_id, self.get_all_component_ids(bug_id))
            # self.reformulate_query(bug_id, all_comp_id_related_files)

            # filtered_files = self.readFiles.get_filtered_files(bug_id)
            # #     self.reformulate_query(bug_id, filtered_files)
            # unfiltered_files = self.readFiles.get_unfiltered_files(bug_id)
            # filtered_files.extend(unfiltered_files)
            # self.reformulate_query(bug_id, filtered_files)

if __name__ == '__main__':
    corpus = Corpus()
    corpus.main()
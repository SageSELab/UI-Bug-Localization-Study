#!/usr/bin/env python3
import random
import json
import http.client
import re
import csv
import argparse
import os

from helpers_code_mapping import CodeMappingHelper
from write_results import WriteResults

#from calculate_metrics import CalculateMetrics
from file_analysis import FileAnalysis
#from call_graph import CallGraph
from read_files import ReadFiles


# ---- Globals ----

class SoureCodeMapping:

    def __init__(self, args):
        self.codeMappingHelper = CodeMappingHelper()
        self.writeResults = WriteResults()
        # self.calculateMetrics = CalculateMetrics()
        self.fileAnalysis = FileAnalysis()
        # self.callGraph = CallGraph()
        self.readFiles = ReadFiles()
        #self.args = args

        self.corpusType = args['corpus'] # All_Java_Files or GUI_State_and_All_GUI_Component_IDs or All_GUI_Component IDs

        #self.query_name = #  GUI_State_and_Interacted_GUI_Component_ID or GUI_State or GUI_State_and_All_GUI_Component_IDs 
        # or Interacted_GUI_Component_IDs or All_GUI_Component_IDs

        self.query_name = args['query']
        self.number_of_screens = int(args['screens'])

    def get_query_name(self):
        return self.query_name

    def get_corpus_flag(self):
        return self.filteredCorpusFlag
    # ------------------------------------------------------------------------------
    # ---- Main ----

    def get_files_gui_state_all_component_ids(self, parent_directory, list_of_activities, all_comp_ids):
        gui_state_files = self.fileAnalysis.get_filtered_files(parent_directory, list_of_activities)

        all_comp_id_related_files = self.fileAnalysis.get_files_if_term_exists(parent_directory, all_comp_ids)
        all_comp_id_related_files = self.codeMappingHelper.get_files_that_not_exist_in_first_list(all_comp_id_related_files, gui_state_files)

        filtered_files = []
        filtered_files.extend(gui_state_files)
        filtered_files.extend(all_comp_id_related_files)

        return filtered_files

    def get_all_component_id_related_files(self, parent_directory, all_comp_ids):
        all_comp_id_related_files = self.fileAnalysis.get_files_if_term_exists(parent_directory, all_comp_ids)

        return all_comp_id_related_files

    def get_files_gui_state_interacted_component_ids(self, parent_directory, list_of_activities, list_of_interacted_comp_ids):
        gui_state_files = self.fileAnalysis.get_filtered_files(parent_directory, list_of_activities)

        # Retrieve interacted component id related files and remove those files where filenames matches with the activities/fragments
        intercated_comp_id_related_files = self.fileAnalysis.get_files_if_term_exists(parent_directory, list_of_interacted_comp_ids)
        intercated_comp_id_related_files = self.codeMappingHelper.get_files_that_not_exist_in_first_list(intercated_comp_id_related_files, gui_state_files)

        filtered_files = []
        filtered_files.extend(gui_state_files)
        filtered_files.extend(intercated_comp_id_related_files)

        return filtered_files


    def main(self):
        # First set of bug reports
        # bug_ids_states = [("2",41), ("8",14), ("10",15), ("18",21), ("19",5), ("44",21),
        #         ("53",18), ("117",11), ("128",28), ("129", 33), ("130",2),
        #         ("135",14), ("191",1), ("206",14), ("209",50), ("256",19),
        #         ("1073",8), ("1096",14), ("1146",6),
        #         ("1147",7), ("1151",5), ("1202",11), ("1205",22), ("1207",13),
        #         ("1214",13), ("1215",31), ("1223",81), ("1224",39),
        #         ("1299",20), ("1399",14), ("1406",20), ("1430",21), ("1441",18),
        #         ("1445",14), ("1481",16), ("1645",6),
        #         #new ones
        #         ("45",22), ("54",10), ("76",6), ("92",4), ("106",11),("110",5),
        #         ("158",10), ("160",14), ("162",6), ("168",3), ("192",12),("199",11),
        #         ("200",9), ("248",45), ("1150",11), ("1198",20),
        #         ("1228",24),("1389",2),("1425",18),("1446",18),("1563",7),("1568",8)]

        # Second set of bug reports
        #bug_ids_states = [("11",2), ("55",50), ("56", 19), ("227", 25), ("1213",44), ("1222",17), ("1428", 12)]

        # Third set of bug reports
        # bug_ids_states = [("84",13), ("87",32), ("151",16), ("159",34), ("193",5), ("271",22), ("275",8), 
        #     ("1028",13), ("1089",7), ("1130",12), ("1321", 19), ("1402",15), ("1403", 24)]

        #Fourth set of bug reports
        #bug_ids_states = [("71", 17), ("201",37), ("1641",9)]

        # Fifth set of bug reports
        #bug_ids_states = [("1096",14), ("1146",6), ("1147",20), ("1151",5), ("1223",19), ("1645",35), ("106", 13), ("110", 5),
        #("168",3), ("271", 22)]

        # Sixth set of bug reports
        #bug_ids_states = [("1406", 20), ("45", 11), ("1640", 4)]

        # Seventh set of bug reports
        #bug_ids_states = [("1150",11)]

        # For test
        bug_ids_states = [("53",18)]
        
        corpus_folder = args['result'] + "/" + "Screen-" + str(self.number_of_screens) + "/" + "Corpus-" + self.corpusType
        result_folder = []
        print(corpus_folder)
        os.makedirs(corpus_folder, exist_ok=True)

        query_filename = corpus_folder  + "/Queries.csv"
        self.writeResults.write_header_for_query(query_filename)

        if args['operations']=="Filtering+Boosting":
            result_folder = corpus_folder + "/Boosting-" + self.query_name
            os.makedirs(result_folder, exist_ok=True)
            matched_files_stored_filename = result_folder + "/Match_Query_File_List.csv"
            self.writeResults.write_header_for_file_list(matched_files_stored_filename)

            not_matched_files_stored_filename = result_folder + "/Not_Match_Query_File_List.csv"
            self.writeResults.write_header_for_file_list(not_matched_files_stored_filename)

        files_in_corpus_filename = corpus_folder + "/Files_In_Corpus.csv"
        self.writeResults.write_header_for_file_list(files_in_corpus_filename)

        for issue_id, app_final_state in bug_ids_states:
            bug_id = issue_id
            #print("Bug id: " + bug_id)

            parent_directory = "UIBugLocalization/Backup/CodeUnused/BuggyProjects/bug-" + bug_id
            all_java_files = self.readFiles.get_all_java_files(bug_id)

            json_file = open('UIBugLocalization/FaultLocalizationCode/data/TraceReplayer-Data/TR' + bug_id +'/Execution-1.json')
            data = json.load(json_file)

            list_of_activities = []
            list_of_fragments = []
            list_of_interacted_comp_ids = []
            all_comp_ids = []

            final_state = app_final_state

            interacted_comp_states = [final_state + x for x in range(0, -self.number_of_screens+1, -1)]
            screen_states = [final_state + x for x in range(1, 1-self.number_of_screens, -1)]

            for step in data['steps']:
                if step['sequenceStep'] in interacted_comp_states:
                    interacted_comp_ids_step = self.codeMappingHelper.get_interacted_component_ids_for_step(step)
                    list_of_interacted_comp_ids.extend(interacted_comp_ids_step)

                if step['sequenceStep'] in screen_states:
                    activity = self.codeMappingHelper.get_screen_activity(step)
                    list_of_activities.append(activity)
                    cur_fragment = self.codeMappingHelper.get_screen_fragment(step)
                    list_of_fragments.append(cur_fragment)

                    step_comp_ids = self.codeMappingHelper.get_all_component_ids_unprocessed(step['screen']['dynGuiComponents'])
                    all_comp_ids.extend(step_comp_ids)

            json_file.close()
            list_of_activities = self.codeMappingHelper.clean_query(list_of_activities)
            list_of_fragments = self.codeMappingHelper.clean_query(list_of_fragments)
            
            list_of_interacted_comp_ids = self.codeMappingHelper.clean_query(list_of_interacted_comp_ids)
            all_comp_ids = self.codeMappingHelper.clean_query(all_comp_ids)
            
            self.writeResults.write_row_for_query(query_filename, bug_id, list_of_activities, list_of_fragments, list_of_interacted_comp_ids, all_comp_ids)
            list_of_activities.extend(list_of_fragments)

            files_in_corpus = []

            # This segment is to check whether we apply filtering or not and build our corpus based on that criteria
            if self.corpusType == "All_Java_Files":
                files_in_corpus = all_java_files
            elif self.corpusType == "GUI_State_and_All_GUI_Component_IDs":
                files_in_corpus = self.get_files_gui_state_all_component_ids(parent_directory, list_of_activities, all_comp_ids)
            elif self.corpusType == "All_GUI_Component_IDs":
                files_in_corpus = self.get_all_component_id_related_files(parent_directory, all_comp_ids)
            elif self.corpusType == "GUI_States":
                files_in_corpus = self.fileAnalysis.get_filtered_files(parent_directory, list_of_activities)
            elif self.corpusType == "Interacted_GUI_Component_IDs":
                files_in_corpus = self.fileAnalysis.get_files_if_term_exists(parent_directory, list_of_interacted_comp_ids)
            elif self.corpusType == "GUI_State_and_Interacted_GUI_Component_IDs":
                files_in_corpus = self.get_files_gui_state_interacted_component_ids(parent_directory, list_of_activities, list_of_interacted_comp_ids)

            #Store all files in corpus in corpus filelist
            self.writeResults.write_file_list_each_row(bug_id, files_in_corpus, files_in_corpus_filename, "Corpus")

            if args['operations']=="Filtering+Boosting":
                # This segment is to separate those files that we boost
                if self.query_name == "GUI_State_and_Interacted_GUI_Component_IDs":
                    matched_files = self.get_files_gui_state_interacted_component_ids(parent_directory, list_of_activities, list_of_interacted_comp_ids)
                    matched_files = self.codeMappingHelper.get_files_if_exist_in_corpus(matched_files, files_in_corpus)
                    self.writeResults.write_file_list_each_row(bug_id, matched_files, matched_files_stored_filename, "ActivityFragments/Interacted")

                elif self.query_name == "GUI_States":
                    matched_files = self.fileAnalysis.get_filtered_files(parent_directory, list_of_activities)
                    matched_files = self.codeMappingHelper.get_files_if_exist_in_corpus(matched_files, files_in_corpus)
                    self.writeResults.write_file_list_each_row(bug_id, matched_files, matched_files_stored_filename, "ActivityFragments")

                elif self.query_name == "GUI_State_and_All_GUI_Component_IDs":
                    matched_files = self.get_files_gui_state_all_component_ids(parent_directory, list_of_activities, all_comp_ids)
                    matched_files = self.codeMappingHelper.get_files_if_exist_in_corpus(matched_files, files_in_corpus)
                    self.writeResults.write_file_list_each_row(bug_id, matched_files, matched_files_stored_filename, "ActivityFragments/AllGUI")

                elif self.query_name == "Interacted_GUI_Component_IDs":
                    matched_files = self.fileAnalysis.get_files_if_term_exists(parent_directory, list_of_interacted_comp_ids)
                    matched_files = self.codeMappingHelper.get_files_if_exist_in_corpus(matched_files, files_in_corpus)
                    self.writeResults.write_file_list_each_row(bug_id, matched_files, matched_files_stored_filename, "Interacted")

                elif self.query_name == "All_GUI_Component_IDs":
                    matched_files = self.get_all_component_id_related_files(parent_directory, all_comp_ids)
                    matched_files = self.codeMappingHelper.get_files_if_exist_in_corpus(matched_files, files_in_corpus)
                    self.writeResults.write_file_list_each_row(bug_id, matched_files, matched_files_stored_filename, "All")

                not_matched_files = self.codeMappingHelper.get_files_that_not_exist_in_first_list(files_in_corpus, matched_files)
                self.writeResults.write_file_list_each_row(bug_id, not_matched_files, not_matched_files_stored_filename, "NotMatched")

            
    # ------------------------------------------------------------------------------

if __name__ == '__main__':
    # https://stackoverflow.com/questions/7427101/simple-argparse-example-wanted-1-argument-3-results
    parser = argparse.ArgumentParser()
    
    parser.add_argument('-c','--corpus', help='Description for boosting', required=True)
    parser.add_argument('-q','--query', help='Description for query', required=False)
    parser.add_argument('-r','--result', help='Description for results', required=True)
    parser.add_argument('-s','--screens', help='Number of screens', required=True)
    parser.add_argument('-ops','--operations', help='Operations', required=True)
    args = vars(parser.parse_args())

    sourcodeCodeMapping = SoureCodeMapping(args)
    sourcodeCodeMapping.main()




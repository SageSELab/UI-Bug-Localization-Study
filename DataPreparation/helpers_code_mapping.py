from similarityCalculation import SimilarityCalculation
from preprocess import Preprocess
from file_analysis import FileAnalysis

import re

class CodeMappingHelper:
    def __init__(self):
        self.similarityCalculation = SimilarityCalculation()
        self.preprocess = Preprocess()
        self.fileAnalysis = FileAnalysis()

    def get_cos_similarity_scores(self, bug_report_contents, method_blocks):
        bug_report_processed = self.preprocess.get_preprocessed_data(bug_report_contents)
        method_processed_list = []
        for method in method_blocks:
            method_processed = self.preprocess.get_preprocessed_data(method)
            method_processed_list.append(method_processed)

        cos_similarities = []
        if len(method_processed_list)>0:
            cos_similarities = self.similarityCalculation.compute_similarity(bug_report_processed, method_processed_list)
        return cos_similarities

    def get_preprocessed_file_cos_similarity_scores(self, bug_report_processed, code_processed_files):
        cos_similarities = []
        code_processed_list = []
        for code_block in code_processed_files:
            #print(code_block)
            if code_block is None or len(code_block)<1:
                code_block = ""
            code_processed_list.append(code_block)
        #print("rt")
        #print(len(code_processed_list))
        if len(code_processed_list)>0:
            if len(code_processed_list)>300:
                cos_similarities_1 = self.similarityCalculation.compute_similarity(bug_report_processed, code_processed_list[:300])
                cos_similarities.extend(cos_similarities_1)
                cos_similarities_2 = self.similarityCalculation.compute_similarity(bug_report_processed, code_processed_list[300:len(code_processed_list)])
                cos_similarities.extend(cos_similarities_2)
            else:
                cos_similarities = self.similarityCalculation.compute_similarity(bug_report_processed, code_processed_list)
        return cos_similarities

    def get_screen_activity(self, step):
        activity = step['screen']['activity']
        activity = re.split(r"[(]", activity)
        activity = activity[0]
        activity = activity.replace(".", "/")
        if "/" in activity:
            activity_splits = activity.split("/")
            activity = activity_splits[len(activity_splits)-1]
        return activity

    def get_screen_fragment(self, step):
        fragment = step['screen']['window']
        fragment_splits = fragment.split(":")
        cur_fragment = ""
        if len(fragment_splits)>1 and fragment_splits[len(fragment_splits)-2]=='FRAGMENT':
            cur_fragment = fragment_splits[len(fragment_splits)-1]
        return cur_fragment

    def get_interacted_component_ids_and_string_ids_and_android_ids_for_step(self, step, parent_directory):
        search_terms = []
        if 'dynGuiComponent' in step:
            if 'idXml' in step['dynGuiComponent']:
                if len(step['dynGuiComponent']['idXml'])>0:
                    comp_str = step['dynGuiComponent']['idXml'].split("/")
                    #component id
                    comp_id = comp_str [len(comp_str )-1]
                    search_terms.append(comp_id)

            if 'titleWindow' in step['dynGuiComponent']:
                comp_window = step['dynGuiComponent']['titleWindow']
                if len(comp_window)>0:
                    strings_ids = self.fileAnalysis.get_string_ids(parent_directory, comp_window)
                    for str_id in strings_ids:
                        android_ids = self.fileAnalysis.get_android_ids(parent_directory, str_id)
                        search_terms.extend(android_ids)
                    search_terms.extend(strings_ids)

            if 'text' in step['dynGuiComponent']:
                comp_window = step['dynGuiComponent']['text']
                if len(comp_window)>0:
                    strings_ids = self.fileAnalysis.get_string_ids(parent_directory, comp_window)
                    for str_id in strings_ids:
                        android_ids = self.fileAnalysis.get_android_ids(parent_directory, str_id)
                        search_terms.extend(android_ids)
                    search_terms.extend(strings_ids)

        return search_terms

    def get_interacted_component_ids_for_step(self, step):
        search_terms = []
        if 'dynGuiComponent' in step:
            if 'idXml' in step['dynGuiComponent']:
                if len(step['dynGuiComponent']['idXml'])>0:
                    comp_str = step['dynGuiComponent']['idXml'].split("/")
                    #component id
                    comp_id = comp_str [len(comp_str )-1]
                    search_terms.append(comp_id)
        return search_terms

    def get_additional_search_terms_from_screen_procecessed(self, gui_components):
        additional_search_terms = []
        for component in gui_components:
            if 'text' in component:
                if len(component['text'])>0:
                    comp_text = component['text']
                    comp_text = self.preprocess_file_content(comp_text)
                    comp_text = self.tokenize_file_content(comp_text)
                    for each_text in comp_text:
                        if len(each_text)>0:
                            additional_search_terms.append(each_text)
            if 'idXml' in component:
                if len(component['idXml'])>0:
                    component_idxml = component['idXml'].split("/")
                    comp_id = component_idxml[len(component_idxml)-1]
                    comp_id = self.preprocess_file_content(comp_id)
                    comp_id = self.tokenize_file_content(comp_id)
                    for each_id in comp_id: 
                        if len(each_id)>0:
                            additional_search_terms.append(each_id)
        additional_search_terms = self.get_unique_names(additional_search_terms)

        return additional_search_terms

    def get_all_component_ids_unprocessed(self, gui_components):
        additional_search_terms = []
        for component in gui_components:
            if 'idXml' in component:
                if len(component['idXml'])>0:
                    component_idxml = component['idXml'].split("/")
                    comp_id = component_idxml[len(component_idxml)-1]
                    if len(comp_id)>0:
                        additional_search_terms.append(comp_id)
        additional_search_terms = self.get_unique_names(additional_search_terms)
        return additional_search_terms

    #Remove duplicates and empty string
    def get_unique_names(self, list_of_names):
        current_name_set = set()
        unique_name_list = [] 
        for cur_name in list_of_names:
            if cur_name not in current_name_set:
                unique_name_list.append(cur_name)
            current_name_set.add(cur_name)

        return unique_name_list

    def remove_keywords_from_query(self, search_terms):
        modified_search_terms = []
        # unimportant_words = ["NO_ID","BACK_MODAL", "text", "button", "title", "ok", "save", "null"]
        unimportant_words = ["NO_ID","BACK_MODAL", "null"]

        for item in search_terms:
            unimportant_word_flag = False
            for word in unimportant_words:
                if len(item)<=1 or word.lower() in item.lower():
                    unimportant_word_flag = True
                    break
            if unimportant_word_flag==False:
               modified_search_terms.append(item)
        return modified_search_terms

    def remove_empty_from_list(self, string):
        #https://stackoverflow.com/questions/3845423/remove-empty-strings-from-a-list-of-strings
        return [item for item in string if item]

    # Remove duplicate keywords and empty string from queries
    def clean_query(self, queries):
        queries = self.remove_empty_from_list(queries)
        queries = self.get_unique_names(queries)
        queries = self.remove_keywords_from_query(queries)

        return queries

    # Return those files from the cur_file_list that doesn't exist in the first file list
    def get_files_that_not_exist_in_first_list(self, cur_file_list, first_file_list):
        pr_extra_files = []
        for additional_file in cur_file_list:
            if additional_file not in first_file_list:
                pr_extra_files.append(additional_file)

        return pr_extra_files

    # Return those files from the cur_file_list if exist in corpus_files
    def get_files_if_exist_in_corpus(self, cur_file_list, corpus_files):
        pr_files = []
        for each_file in cur_file_list:
            if each_file in corpus_files:
                pr_files.append(each_file)
                
        return pr_files





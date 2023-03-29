#https://github.com/microsoft/CodeBERT/tree/master/UniXcoder#2-similarity-between-code-and-nl

import torch
from unixcoder import UniXcoder

import torch.nn.functional as F
import os
import re
import json
import csv
import pandas as pd
import argparse
import numpy as np
import math
import re
from ast import literal_eval
import time

model = UniXcoder("microsoft/unixcoder-base")
device = 'cuda' if torch.cuda.is_available() else 'cpu'
#print(device)
model = model.to(device)

def get_file_content(file_name):
    # Read the file
    file_content = open(file_name, "r")
    file_content = file_content.read()
    return file_content

def get_bug_report_contents_preprocessed(queries_dir, bug_id, query):
    bug_report_file = queries_dir + "/" + query + "/bug_report_" + bug_id + ".txt"
    bug_report_contents = get_file_content(bug_report_file)
    if bug_report_contents is None or len(bug_report_contents)<1:
        bug_report_contents = ""

    return bug_report_file, bug_report_contents

#Encode text
def encode(texts):
    # Tokenize sentences
    tokens_ids = model.tokenize([texts],max_length=512,mode="<encoder-only>")
    source_ids = torch.tensor(tokens_ids).to(device)

    tokens_embeddings,max_func_embedding = model(source_ids)

    norm_max_func_embedding = torch.nn.functional.normalize(max_func_embedding, p=2, dim=1)

    return norm_max_func_embedding

def get_buggy_java_files(jsonFilePath, bug_issue_id):
    json_file = jsonFilePath + "/" + str(bug_issue_id) + ".json"
    with open(json_file, 'r') as jfile:
        json_data = jfile.read()
    original_buggy_locations = json.loads(json_data)

    unique_java_files = set()
    for bug_location in original_buggy_locations["bug_location"]:
        buggy_file = bug_location["file_name"]
        if buggy_file.endswith(".java"):
            unique_java_files.add(buggy_file)

    return unique_java_files

def get_buggy_file_rankings(jsonFilePath, bug_id, sorted_similarity_scores):
    ranks = []
    unsorted_ranks = []
    ranked_buggy_files = []
    buggy_java_files = get_buggy_java_files(jsonFilePath, bug_id)

    order_number = 1
    for key in sorted_similarity_scores:
        bug_id_index = key.find("bug-"+bug_id)
        cur_file = key[bug_id_index:]
        if cur_file in buggy_java_files:
            ranks.append(order_number)
            ranked_buggy_files.append(cur_file)
        order_number += 1

    unsorted_ranks = ranks.copy()
    ranks.sort()
    return ranks, ranked_buggy_files, unsorted_ranks

def get_code_processed(preprocessed_code_path, bug_id, codeFilepath):
    filename = preprocessed_code_path + "/bug-" + bug_id + ".csv"
    file_list_df = pd.read_csv(filename)
    files_for_bug_id = file_list_df.loc[file_list_df['FilePath']==codeFilepath, 'PreprocessedCode'].values.tolist()
    if len(files_for_bug_id)<1:
        return ""
    return files_for_bug_id[0]

def write_to_csv(write_file, row):
    with open(write_file, 'a') as file:
        writer = csv.writer(file)
        writer.writerow(row)

def write_ranks_to_csv(jsonFilePath, bug_issue_id, number_of_files, similarity_scores, class_result_output_file):
    data_row = []
    data_row.append(bug_issue_id)
    data_row.append(number_of_files)

    sorted_similarity_scores = sorted(similarity_scores, key=similarity_scores.get, reverse=True)

    # Ranks of correct bug locations in the result
    ranks, ranked_buggy_files, unsorted_ranks = get_buggy_file_rankings(jsonFilePath, bug_issue_id, sorted_similarity_scores)
    #print("Ranks: ", ranks)
    data_row.append(ranks)
    data_row.append(ranked_buggy_files)
    data_row.append(unsorted_ranks)
    write_to_csv(class_result_output_file, data_row)

def calculate_similarity(code_emb_list, query_emb):
    sim_score_list = []
    for code_emb in code_emb_list:
        score = torch.einsum("ac,bc->ab", code_emb, query_emb)
        score = score[0].cpu().tolist()
        sim_score_list.append(score[0])
    return np.max(sim_score_list)

def create_sim_score_file_header(sim_score_store_file):
    #https://stackoverflow.com/questions/12517451/automatically-creating-directories-with-file-output
    os.makedirs(os.path.dirname(sim_score_store_file), exist_ok=True)
    with open(sim_score_store_file, 'w') as file:
        writer = csv.writer(file)
        writer.writerow(["Source_Code_Filename", "Preprocessed_Query_File", "Cosine_Similarity"])

def check_if_score_already_computed(sim_score_store_file, code_filename, query_filename):
    if not os.path.exists(sim_score_store_file):
        create_sim_score_file_header(sim_score_store_file)
        return False, "Not Exist"
    elif os.path.exists(sim_score_store_file):
        sim_file_df = pd.read_csv(sim_score_store_file)
        cos_score = sim_file_df.loc[(sim_file_df['Source_Code_Filename']==code_filename) & (sim_file_df['Preprocessed_Query_File']==query_filename), 'Cosine_Similarity'].values.tolist()

        if len(cos_score)<1:
            return False, "Not Exist"
        return True, cos_score[0]

def get_code_segment_embedding_and_similarity(code_filename, query_filename, code_processed, query_emb, query_type, sim_path, bug_id):
    sim_score_store_file = sim_path + "/" + query_type + "/bug-" + bug_id + ".csv"
    check_score_exist, cos_score = check_if_score_already_computed(sim_score_store_file, code_filename, query_filename)
    if check_score_exist:
        return float(cos_score)

    number_of_segments = math.floor(len(code_processed)/512)+1

    code_emb_list = []
    start_ind = 0
    end_ind = 512
    max_sim = 0
    for i in range(number_of_segments-1):
        cur_code_segment = code_processed[start_ind:end_ind]
        code_emb = encode(cur_code_segment)
        code_emb_list.append(code_emb)

        if len(code_emb_list)==90:
            max_sim = max(max_sim, calculate_similarity(code_emb_list, query_emb))
            code_emb_list = []

        start_ind+=512
        end_ind+=512

    cur_code_segment = code_processed[start_ind:len(code_processed)]
    code_emb = encode(cur_code_segment)
    code_emb_list.append(code_emb)

    max_sim = max(max_sim, calculate_similarity(code_emb_list, query_emb))

    write_to_csv(sim_score_store_file, [code_filename, query_filename, max_sim])

    return max_sim

def get_embedding(embedding_file, content):
    query_emb = []
    if os.path.exists(embedding_file):
        query_emb = torch.load(embedding_file, map_location=device)
    else:
        query_emb = encode(content)
        torch.save(query_emb, embedding_file)
    return query_emb

def create_filepath(file):
    #https://stackoverflow.com/questions/12517451/automatically-creating-directories-with-file-output
    os.makedirs(os.path.dirname(file), exist_ok=True)

def compute_result(queries_dir, jsonFilePath, bug_id, files_list,  
    class_result_output_file, replaced_query_output_file, query_expansion1_output_file, 
    preprocessed_code_dir, 
    buggy_projects_dir, prep_code_path, emb_path, sim_path):

    original_bug_report_emb = []
    replaced_query_emb = []
    query_expansion_1_emb = []

    original_bug_report_similarity_scores = {}
    bug_report_file, original_bug_report = get_bug_report_contents_preprocessed(queries_dir, bug_id, "bug_report_original")
    if len(original_bug_report)>0:
        original_bug_report_embedding_file = emb_path + "/bug_report_original/bug-" + bug_id + ".pt"
        create_filepath(original_bug_report_embedding_file)
        original_bug_report_emb = get_embedding(original_bug_report_embedding_file, original_bug_report)

    replaced_query_similarity_scores = {}
    replaced_query_file, replaced_query = get_bug_report_contents_preprocessed(queries_dir, bug_id, "replaced_query")
    if len(replaced_query)>0:
        replaced_query_embedding_file = emb_path + "/replaced_query/bug-" + bug_id + ".pt"
        create_filepath(replaced_query_embedding_file)
        replaced_query_emb = get_embedding(replaced_query_embedding_file, replaced_query)

    query_expansion_1_similarity_scores = {}
    query_expansion_1_file, query_expansion_1 = get_bug_report_contents_preprocessed(queries_dir, bug_id, "query_expansion_1")
    if len(query_expansion_1)>0:
        query_expansion_1_embedding_file = emb_path + "/query_expansion_1/bug-" + bug_id + ".pt"
        create_filepath(query_expansion_1_embedding_file)
        query_expansion_1_emb = get_embedding(query_expansion_1_embedding_file, query_expansion_1)

    file_count = 0
    for file_name in files_list:
        file_count += 1
        file_name = file_name.replace(buggy_projects_dir, preprocessed_code_dir)
        code_processed = get_code_processed(prep_code_path, bug_id, file_name)

        if len(original_bug_report)>0:
            original_bug_report_similarity_scores[file_name] = get_code_segment_embedding_and_similarity(file_name, bug_report_file, code_processed, original_bug_report_emb, "bug_report_original", sim_path, bug_id)
        if len(replaced_query)>0:
            replaced_query_similarity_scores[file_name] = get_code_segment_embedding_and_similarity(file_name, replaced_query_file, code_processed, replaced_query_emb, "replaced_query", sim_path, bug_id)
        if len(query_expansion_1)>0:
            query_expansion_1_similarity_scores[file_name] = get_code_segment_embedding_and_similarity(file_name, query_expansion_1_file, code_processed, query_expansion_1_emb, "query_expansion_1", sim_path, bug_id)

    write_ranks_to_csv(jsonFilePath, bug_id, len(files_list), original_bug_report_similarity_scores, class_result_output_file)
    write_ranks_to_csv(jsonFilePath, bug_id, len(files_list), replaced_query_similarity_scores, replaced_query_output_file)
    write_ranks_to_csv(jsonFilePath, bug_id, len(files_list), query_expansion_1_similarity_scores, query_expansion1_output_file)
    
def create_header(class_result_output_file):
    #https://stackoverflow.com/questions/12517451/automatically-creating-directories-with-file-output
    os.makedirs(os.path.dirname(class_result_output_file), exist_ok=True)

    with open(class_result_output_file, 'w') as file:
        writer = csv.writer(file)
        writer.writerow(["Bug Report ID", "#Files (.java)", "Ranks", "Ranked Buggy Files", "Ranks (Unsorted)"])

def log_completion(bug_id):
    print(f'Done: {bug_id}')

def compute_result_for_individual_bug(bug_issue_id, corpus_match_files_dir, queries_dir, jsonFilePath,
        class_result_output_file, replaced_query_output_file, query_expansion1_output_file, 
        preprocessed_code_dir, 
        buggy_projects_dir, prep_code_path, emb_path, sim_path):
    #print("Bug: " +bug_issue_id)
    files_list = []
    for root, subdirs, files in os.walk(corpus_match_files_dir + "/bug-" + str(bug_issue_id)):
        for file_name in files:
            if ".java" in file_name:
                fullpath = os.path.join(root, file_name)
                fullpath = fullpath.replace(corpus_match_files_dir, buggy_projects_dir)
                files_list.append(fullpath)

    compute_result(queries_dir, jsonFilePath, bug_issue_id, files_list,
        class_result_output_file, replaced_query_output_file, query_expansion1_output_file, 
        preprocessed_code_dir, 
        buggy_projects_dir, prep_code_path, emb_path, sim_path)

def file_search_and_rankings(filetype, bug_issue_ids, result_folder, subpath, filtered_boosted_dir, 
    buggy_projects_dir, preprocessed_data_path, jsonFilePath, preprocessed_code_dir, 
    prep_query_path, prep_code_path, emb_path, sim_path, query_reformulation_gui):
    result_sub_dir = result_folder + "/" + subpath + "/QueryReformulation-" + query_reformulation_gui + "/" + filetype
    corpus_match_files_dir = filtered_boosted_dir + "/" + subpath + "/" + filetype
    queries_dir = preprocessed_data_path + "/" + prep_query_path
    class_result_output_file, replaced_query_output_file, query_expansion1_output_file = create_result_files_header(result_sub_dir)

    for bug_issue_id in bug_issue_ids:
        compute_result_for_individual_bug(bug_issue_id, corpus_match_files_dir, queries_dir, jsonFilePath,
            class_result_output_file, replaced_query_output_file, query_expansion1_output_file, 
            preprocessed_code_dir, 
            buggy_projects_dir, prep_code_path, emb_path, sim_path)


def get_ranks(bug_id, query_type, result_file):
    file_list_df = pd.read_csv(result_file)
    files_for_bug_id = file_list_df.loc[file_list_df['Bug Report ID']==int(bug_id), 'Ranks (Unsorted)'].values.tolist()

    return files_for_bug_id[0]

def get_buggy_found_files(bug_id, query_type, result_file):
    file_list_df = pd.read_csv(result_file)
    files_for_bug_id = file_list_df.loc[file_list_df['Bug Report ID']==int(bug_id), 'Ranked Buggy Files'].values.tolist()

    return files_for_bug_id[0]

def create_result_files_header(result_sub_dir):
    class_result_output_file = result_sub_dir + "/original-bug-report.csv"
    create_header(class_result_output_file)

    replaced_query_output_file = result_sub_dir + "/replaced-query.csv"
    create_header(replaced_query_output_file)

    query_expansion1_output_file = result_sub_dir + "/query-expansion-1.csv"
    create_header(query_expansion1_output_file)

    # return class_result_output_file, replaced_query_output_file, query_expansion1_output_file, query_expansion2_output_file, query_expansion3_output_file
    return class_result_output_file, replaced_query_output_file, query_expansion1_output_file

def create_final_result_header(result_file):
    os.makedirs(os.path.dirname(result_file), exist_ok=True)
    with open(result_file, 'w') as file:
        writer = csv.writer(file)
        writer.writerow(["Bug Report ID", "Ranks-unsorted (Query-Bug Report)", "Ranks (Query-Bug Report)", "Files (Query-Bug Report)",
            "Ranks-unsorted (Query Replacement)", "Ranks (Query Replacement)", "Files (Query Replacement)",
            "Ranks-unsorted (Query Expansion 1)", "Ranks (Query Expansion 1)", "Files (Query Expansion 1)"])

def get_ranked_files(bug_id, filename):
    file_list_df = pd.read_csv(filename)
    files_for_bug_id = file_list_df.loc[file_list_df['Bug Report ID']==int(bug_id), 'FilePaths'].values.tolist()

    return files_for_bug_id

def get_filtered_files(bug_issue_id, filtered_files_stored_file):
    filtered_files = get_ranked_files(bug_issue_id, filtered_files_stored_file)

    return filtered_files

def get_final_ranks(bug_id, query_type, matched_files_stored_file, result_folder1, result_folder2, operations):
    ranks1 = get_ranks(bug_id, query_type, result_folder1 + "/" + query_type + ".csv")
    ranks1_files = get_buggy_found_files(bug_id, query_type, result_folder1 + "/" + query_type + ".csv")
    ranks1_files = literal_eval(ranks1_files)
    ranks1 = literal_eval(ranks1)
    ranks1[:] = [rank1 for rank1 in ranks1 if rank1 != 0]

    unsorted_ranks1 = ranks1.copy()
    if operations=='Filtering' or operations=="QueryReformulation":
        ranks1.sort()
        return unsorted_ranks1, ranks1, ranks1_files

    ranks2 = get_ranks(bug_id, query_type, result_folder2 + "/" + query_type + ".csv")
    ranks2_files = get_buggy_found_files(bug_id, query_type, result_folder2 + "/" + query_type + ".csv")
    ranks2_files = literal_eval(ranks2_files)
    ranks2 = literal_eval(ranks2)
    ranks2[:] = [rank2 for rank2 in ranks2 if rank2 != 0]

    number_of_filtered_files = len(get_filtered_files(bug_id, matched_files_stored_file))

    ranks2 = [number_of_filtered_files + ranks2[i] for i in range(len(ranks2))]
    cur_ranks = unsorted_ranks1.copy()
    cur_ranks.extend(ranks2)

    unsorted_ranks = cur_ranks.copy()
    cur_ranks.sort()
    ranks1_files.extend(ranks2_files)
    return unsorted_ranks, cur_ranks, ranks1_files

def merge_query_matching_ranks(bug_issue_ids, final_ranks_file, matched_file, 
    matched_ranks_folder, not_matched_ranks_folder, operation_type):
    for bug_id in bug_issue_ids:
        data_row = []
        data_row.append(bug_id)
        #print(bug_id)

        query_type = "original-bug-report"
        orginal_br_ranks, sorted_br_ranks, original_br_files = get_final_ranks(bug_id, query_type, matched_file, matched_ranks_folder, not_matched_ranks_folder, operation_type)
        data_row.append(orginal_br_ranks)
        data_row.append(sorted_br_ranks)
        data_row.append(original_br_files)

        query_type = "replaced-query"
        query_replacement_ranks, sorted_query_replacement_ranks, query_replacement_files = get_final_ranks(bug_id, query_type, matched_file, matched_ranks_folder, not_matched_ranks_folder, operation_type)
        data_row.append(query_replacement_ranks)
        data_row.append(sorted_query_replacement_ranks)
        data_row.append(query_replacement_files)

        query_type = "query-expansion-1"
        query_expansion1_ranks, sorted_query_expansion1_ranks, query_expansion1_files = get_final_ranks(bug_id, query_type, matched_file, matched_ranks_folder, not_matched_ranks_folder, operation_type)
        data_row.append(query_expansion1_ranks)
        data_row.append(sorted_query_expansion1_ranks)
        data_row.append(query_expansion1_files)

        write_to_csv(final_ranks_file, data_row)

def main(args):
    # First Round
    #bug_issue_ids = ["2", "8", "10", "18", "19", "44",
    #               "53", "71", "117", "128", "129", "130",
    #              "135", "191", "201", "206", "209", "256",
    #                "1073", "1096", "1146",
    #                "1147", "1151", "1202", "1205", "1207",
    #                "1214", "1215", "1223", "1224",
    #                "1299", "1399", "1406", "1430", "1441",
    #                "1445", "1481", "1645", "45", "54", "76", "92", "101", "106", "110", "158", "160", "162", "168",
    #                 "192", "199", "200", "248", "1150", "1198", "1228",
    #                "1389", "1425", "1446", "1563", "1568", "1641"]

    # Second Round
    #bug_issue_ids = ["11", "55", "56", "227", "1213", "1222", "1428"]

    #Third Round
    #bug_issue_ids = ["84", "87", "151", "159", "193", "271", "275", "1028", "1089", "1130", "1402", "1403"]

    # Fourth Round
    # bug_issue_ids = ["71", "201", "1641"]

    # Fifth Round
    # bug_issue_ids = ["1096", "1146", "1147", "1151", "1223", "1645", "106", "110", "168", "271"]

    # Sixth Round
    #bug_issue_ids = ["1406", "45", "1640"]

    # Seventh Round
    bug_issue_ids = ["1150"]

    #Get preprocessed queries
    prep_query_path = "Screen-" + args['screen'] + "/Preprocessed_with_" + args['query_reformulation']
    emb_path = args['emb_subdir'] + "/" + prep_query_path
    sim_path = args['sim_subdir'] + "/" + prep_query_path

    if args['operations']=='Filtering':
        corpus_path = "Screen-" + args['screen'] + "/" + "Corpus-" + args['filtering'] 
        file_search_and_rankings("FilteredFiles", bug_issue_ids, args['result'], corpus_path, 
            args['filtered_boosted_repo'], args['buggy_project_dir'], 
            args['prep_data_path'], args['json_file_path'], args['preprocessed_code_dir'], 
            prep_query_path, args['prep_code_path'], emb_path, sim_path, args['query_reformulation'])
        final_ranks_file = args['final_ranks_folder'] + "/" + args['operations'] + "#Screen-" + args['screen'] + "#Filtering-" + args['filtering'] + "#Query_Reformulation-" + args['query_reformulation'] + ".csv"
        matched_file = ""
        matched_ranks_folder = args['result'] + "/" + corpus_path + "/QueryReformulation-" + args['query_reformulation'] + "/" + "FilteredFiles"
        not_matched_ranks_folder = ""

        create_final_result_header(final_ranks_file)
        merge_query_matching_ranks(bug_issue_ids, final_ranks_file, matched_file, 
            matched_ranks_folder, not_matched_ranks_folder, args['operations'])

    elif args['operations']=='Boosting':
        corpus_path = "Screen-" + args['screen'] + "/" + "Corpus-" + "All_Java_Files" 
        boosting_path = corpus_path + "/Boosting-" + args['boosting']
        file_search_and_rankings("MathedQueryFiles", bug_issue_ids, args['result'], boosting_path, 
            args['filtered_boosted_repo'], args['buggy_project_dir'], 
            args['prep_data_path'], args['json_file_path'], args['preprocessed_code_dir'], 
            prep_query_path, args['prep_code_path'], emb_path, sim_path, args['query_reformulation'])
        file_search_and_rankings("NotMathedQueryFiles", bug_issue_ids, args['result'], boosting_path, 
            args['filtered_boosted_repo'], args['buggy_project_dir'], 
            args['prep_data_path'], args['json_file_path'], args['preprocessed_code_dir'], 
            prep_query_path, args['prep_code_path'], emb_path, sim_path, args['query_reformulation'])

        final_ranks_file = args['final_ranks_folder'] + "/" + args['operations'] + "#Screen-" + args['screen'] + "#Boosting-" + args['boosting'] + "#Query_Reformulation-" + args['query_reformulation'] + ".csv"
        matched_file = args['filtered_boosted_filenames'] + "/" + boosting_path + "/Match_Query_File_List.csv"
        matched_ranks_folder = args['result'] + "/" + boosting_path + "/QueryReformulation-" + args['query_reformulation'] + "/" + "MathedQueryFiles"
        not_matched_ranks_folder = args['result'] + "/" + boosting_path + "/QueryReformulation-" + args['query_reformulation'] + "/" + "NotMathedQueryFiles"

        create_final_result_header(final_ranks_file)
        merge_query_matching_ranks(bug_issue_ids, final_ranks_file, matched_file, 
            matched_ranks_folder, not_matched_ranks_folder, args['operations'])

    elif args['operations']=='Filtering+Boosting':
        corpus_path = "Screen-" + args['screen'] + "/" + "Corpus-" + args['filtering'] 
        boosting_path = corpus_path + "/Boosting-" + args['boosting']
        file_search_and_rankings("MathedQueryFiles", bug_issue_ids, args['result'], boosting_path, 
            args['filtered_boosted_repo'], args['buggy_project_dir'], 
            args['prep_data_path'], args['json_file_path'], args['preprocessed_code_dir'], 
            prep_query_path, args['prep_code_path'], emb_path, sim_path, args['query_reformulation'])
        file_search_and_rankings("NotMathedQueryFiles", bug_issue_ids, args['result'], boosting_path, 
            args['filtered_boosted_repo'], args['buggy_project_dir'], 
            args['prep_data_path'], args['json_file_path'], args['preprocessed_code_dir'], 
            prep_query_path, args['prep_code_path'], emb_path, sim_path, args['query_reformulation'])

        final_ranks_file = args['final_ranks_folder'] + "/" + args['operations'] + "#Screen-" + args['screen'] + "#Filtering-" + args['filtering'] + "#Boosting-" + args['boosting'] + "#Query_Reformulation-" + args['query_reformulation'] + ".csv"
        matched_file = args['filtered_boosted_filenames'] + "/" + boosting_path + "/Match_Query_File_List.csv"
        matched_ranks_folder = args['result'] + "/" + boosting_path + "/QueryReformulation-" + args['query_reformulation'] + "/" + "MathedQueryFiles"
        not_matched_ranks_folder = args['result'] + "/" + boosting_path + "/QueryReformulation-" + args['query_reformulation'] + "/" + "NotMathedQueryFiles"

        create_final_result_header(final_ranks_file)
        merge_query_matching_ranks(bug_issue_ids, final_ranks_file, matched_file, 
            matched_ranks_folder, not_matched_ranks_folder, args['operations'])

    elif args['operations']=='QueryReformulation':
        corpus_path = "Screen-" + args['screen'] + "/" + "Corpus-" + "All_Java_Files"
        file_search_and_rankings("FilteredFiles", bug_issue_ids, args['result'], corpus_path, 
            args['filtered_boosted_repo'], args['buggy_project_dir'], 
            args['prep_data_path'], args['json_file_path'], args['preprocessed_code_dir'], 
            prep_query_path, args['prep_code_path'], emb_path, sim_path, args['query_reformulation'])

        final_ranks_file = args['final_ranks_folder'] + "/" + args['operations'] + "#Screen-" + args['screen'] + "#Query_Reformulation-" + args['query_reformulation'] + ".csv"
        matched_file = ""
        matched_ranks_folder = args['result'] + "/" + corpus_path + "/QueryReformulation-" + args['query_reformulation'] + "/" + "FilteredFiles"
        not_matched_ranks_folder = ""

        create_final_result_header(final_ranks_file)
        merge_query_matching_ranks(bug_issue_ids, final_ranks_file, matched_file, 
            matched_ranks_folder, not_matched_ranks_folder, args['operations'])
        
    
if __name__ == "__main__":
     # https://stackoverflow.com/questions/7427101/simple-argparse-example-wanted-1-argument-3-results
    parser = argparse.ArgumentParser()
    parser.add_argument('-rf','--result', help='Description for result', required=True)
    parser.add_argument('-f', '--filtering', help='Filtering GUI Type', required=False)
    parser.add_argument('-b', '--boosting', help='Boosting GUI Type', required=False)
    parser.add_argument('-q', '--query_reformulation', help='Boosting GUI Type', required=True)
    parser.add_argument('-s', '--screen', help='Number of screens', required=True)
    parser.add_argument('-bpd', '--buggy_project_dir', help='Buggy Projects Directory', required=True)
    parser.add_argument('-pcd', '--preprocessed_code_dir', help='Preprocessed Source Code Directory', required=True)
    parser.add_argument('-fbr','--filtered_boosted_repo', help='Filtered Boosted Repos', required=True)
    parser.add_argument('-preq','--prep_data_path', help='Preprocessed_Query', required=True)
    parser.add_argument('-prec','--prep_code_path', help='Preprocessed code', required=True)
    parser.add_argument('-jpath','--json_file_path', help='Preprocessed_Query', required=True)
    parser.add_argument('-ops','--operations', help='Preprocessed_Query', required=True)
    parser.add_argument('-franks','--final_ranks_folder', help='Preprocessed_Query', required=True)
    parser.add_argument('-fbfilenames','--filtered_boosted_filenames', help='filtered_boosted_filenames', required=True)
    parser.add_argument('-emb','--emb_subdir', help='Embeddings temporary', required=True)
    parser.add_argument('-sim','--sim_subdir', help='Cosine Similarity scores of already computed values', required=True)

    args = vars(parser.parse_args())
    
    start_time = time.time()
    main(args)
    end_time = time.time()
    print("Finished in %.10f seconds" % (end_time-start_time))

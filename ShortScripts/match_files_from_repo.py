import glob
import pandas as pd
import os, shutil
import argparse

class MatchFiles:
    def __init__(self, args):
        self.corpus_path = "Screen-" + args['screens'] + "/" + "Corpus-" + args['corpus'] 
        print(self.corpus_path)
        if args['operations']=='Filtering+Boosting':
            self.subpath = self.corpus_path + "/Boosting-" + args['query']
            self.filename_path = args['filtering_boosting_filenames'] + "/" + self.subpath
            self.updated_repo_path = args['filtered_boosted_repo'] + "/" + self.subpath
        elif args['operations']=='Filtering':
            self.filename_path = args['filtering_boosting_filenames'] + "/" + self.corpus_path 
            self.updated_repo_path = args['filtered_boosted_repo'] + "/" + self.corpus_path 

    def get_cur_java_files(self, parent_directory):
        all_files = []
        
        for filename in sorted(glob.glob(f'{parent_directory}/**/*.java', recursive = True)):
            all_files.append(filename)

        return all_files

    def get_all_java_files(self, bug_id):
        parent_directory = args['buggy_project_dir'] + "/bug-" + bug_id
        all_java_files = self.get_cur_java_files(parent_directory)

        return all_java_files

    def get_ranked_files(self, bug_id, filename):
        file_list_df = pd.read_csv(filename)
        files_for_bug_id = file_list_df.loc[file_list_df['Bug Report ID']==int(bug_id), 'FilePaths'].values.tolist()

        return files_for_bug_id

    def get_files_on_query_matching(self, bug_issue_id, csv_file):
        filtered_files_stored_file = self.filename_path + "/" + csv_file
        filtered_files = self.get_ranked_files(bug_issue_id, filtered_files_stored_file)

        file_list = []
        for item_file in filtered_files:
            # Changing deafult filepaths with the filepaths in the buggy projects that we are working on
            file_list.append(item_file.replace(args['buggy_project_dir_in_csv'], args['buggy_project_dir']))

        return file_list

    def match_files_separated(self, all_java_files, filtered_files, query_matching_type):
        for file in all_java_files:
            if file in filtered_files:
                new_path = file.replace(args['buggy_project_dir'], self.updated_repo_path + "/" + query_matching_type)
                try:
                    shutil.copy(file, new_path)
                except IOError as io_err:
                    os.makedirs(os.path.dirname(new_path))
                    shutil.copy(file, new_path)

    def main(self):
        # bug_ids_states = [("2",41), ("8",14), ("10",15), ("18",21), ("19",5), ("44",21),
        #             ("53",18), ("117",11), ("128",28), ("129", 33), ("130",2),
        #             ("135",14), ("191",1), ("206",14), ("209",50), ("256",19),
        #             ("1073",8), ("1096",14), ("1146",6),
        #             ("1147",7), ("1151",5), ("1202",11), ("1205",22), ("1207",13),
        #             ("1214",13), ("1215",31), ("1223",81), ("1224",39),
        #             ("1299",20), ("1399",14), ("1406",20), ("1430",21), ("1441",18),
        #             ("1445",14), ("1481",16), ("1645",6),
        #             #new ones
        #             ("45",22), ("54",10), ("76",6), ("92",4), ("101",8),("106",11),("110",5),
        #             ("158",10), ("160",14), ("162",6), ("168",3), ("192",12),("199",11),
        #             ("200",9), ("248",45), ("1150",11), ("1198",20),
        #             ("1228",24),("1389",2),("1425",18),("1446",18),("1563",7),("1568",8)]

        # bug_ids_states = [("11",2), ("55",50), ("56", 19), ("227", 25), ("1213",44), ("1222",17), ("1428", 12)]
        #bug_ids_states = [("84",13), ("87",32), ("151",16), ("159",34), ("193",5), ("271",22), ("275",8), 
        #    ("1028",13), ("1089",7), ("1130",12), ("1321", 19), ("1402",15), ("1403", 24)]

        #bug_ids_states = [("71", 17), ("201",37), ("1641",9)]
        # Fifth set of bug reports
        #bug_ids_states = [("1096",14), ("1146",6), ("1147",20), ("1151",5), ("1223",19), ("1645",35), ("106", 13), ("110", 5),
        #("168",3), ("271", 22)]

        # Sixth set of bug reports
        #bug_ids_states = [("1406", 20), ("45", 11), ("1640", 4)]

        # Seventh set of bug reports
        bug_ids_states = [("1150",11)]

        for issue_id, app_final_state in bug_ids_states:
            bug_id = issue_id

            all_java_files = self.get_all_java_files(bug_id)

            if args['operations']=='Filtering+Boosting':
                matched_files = self.get_files_on_query_matching(bug_id, "Match_Query_File_List.csv")
                self.match_files_separated(all_java_files, matched_files, "MathedQueryFiles")

                unmatched_files = self.get_files_on_query_matching(bug_id, "Not_Match_Query_File_List.csv")
                self.match_files_separated(all_java_files, unmatched_files, "NotMathedQueryFiles")

            elif args['operations']=='Filtering':
                files_corpus = self.get_files_on_query_matching(bug_id, "Files_In_Corpus.csv")
                self.match_files_separated(all_java_files, files_corpus, "FilteredFiles")


if __name__ == '__main__':
    # https://stackoverflow.com/questions/7427101/simple-argparse-example-wanted-1-argument-3-results
    parser = argparse.ArgumentParser()

    parser.add_argument('-c','--corpus', help='Description for boosting', required=True)
    parser.add_argument('-s', '--screens', help='Number of screens', required=True)
    parser.add_argument('-q', '--query', help='Description for query', required=False)
    parser.add_argument('-bpd', '--buggy_project_dir', help='Buggy Projects Directory', required=True)
    parser.add_argument('-fbfile', '--filtering_boosting_filenames', help='Filtering Boosting Filenames', required=True)
    parser.add_argument('-fbr', '--filtered_boosted_repo', help='Filtered Boosted Repos', required=True)
    parser.add_argument('-bpdcsv', '--buggy_project_dir_in_csv', help='Buggy Projects Directory Path in CSV', required=True)
    parser.add_argument('-ops','--operations', help='Operations', required=True)

    args = vars(parser.parse_args())

    matchFiles = MatchFiles(args)
    matchFiles.main()
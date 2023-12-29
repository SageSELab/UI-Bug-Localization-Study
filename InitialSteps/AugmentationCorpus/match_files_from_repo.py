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
        # Bug reports with the final states
        bug_ids_states = [("2",41), ("8",14), ("10",15), ("11",2), ("18",21), ("19",5), 
                ("44",21), ("45", 11), ("53",18), ("54",10), ("55",50), ("56", 19), 
                ("71", 17), ("76",6), ("84",13), ("87",32), ("92",4), ("106",13), ("110",5),
                ("117",11), ("128",28), ("129", 33), ("130",2), ("135",14), ("158",10), 
                ("159",34), ("160",14), ("162",6), ("168",3), ("191",1), ("192",12), 
                ("193",5), ("199",11), ("200",9), ("201",37), ("206",14), ("209",50), 
                ("227", 25), ("248",45), ("256",19), ("271",22), ("275",8), ("1028",13),
                ("1073",8), ("1089",7), ("1096",14), ("1130",12), ("1146",6), ("1147",20), ("1150",11),
                ("1151",5), ("1198",20), ("1202",11), ("1205",22), ("1207",13), ("1213",44),
                ("1214",13), ("1215",31), ("1222",17), ("1223",19), ("1224",39), ("1228",24),
                ("1299",20), ("1389",2), ("1399",14), ("1402",15), ("1403", 24), ("1406",20), ("1425",18),
                ("1428", 12), ("1430",21), ("1441",18), ("1445",14), ("1446",18), ("1481",16), 
                ("1563",7), ("1568",8), ("1640", 4), ("1641",9), ("1645",35)]

        for issue_id, _ in bug_ids_states:
            bug_id = issue_id

            all_java_files = self.get_all_java_files(bug_id)

            if args['operations']=='Filtering+Boosting':
                matched_files = self.get_files_on_query_matching(bug_id, "Match_Query_File_List.csv")
                self.match_files_separated(all_java_files, matched_files, "MatchedQueryFiles")

                unmatched_files = self.get_files_on_query_matching(bug_id, "Not_Match_Query_File_List.csv")
                self.match_files_separated(all_java_files, unmatched_files, "NotMatchedQueryFiles")

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
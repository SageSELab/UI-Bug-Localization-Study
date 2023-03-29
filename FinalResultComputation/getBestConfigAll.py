import pandas as pd
import csv
import os

def write_to_csv(write_file, row):
	with open(write_file, 'a') as file:
		writer = csv.writer(file)
		writer.writerow(row)

def write_header_for_approach_rankings(filename):
	os.makedirs(os.path.dirname(filename), exist_ok=True)
	with open(filename, 'w') as file:
		writer = csv.writer(file)
		writer.writerow(["Row ID","Task", "GUI Info for Filtering", "GUI Info for Boosting", "GUI Info for Query Expansion", "GUI Info for Query Replacement", "Number of Screens",
					"Avg Best Ranks", "Number of Identified Bugs", "Number of identified buggy files", 
					"Hit@1", "Hit@5", "Hit@10", "Number of hits@10", "Avg Hit@10", "Hit@15", "Hit@20", "Avg Hit@20", "MRR", "MAP", "HIT@10 List"])

def get_max_config_rows(filename):
	df = pd.read_csv(filename)

	rows = df
	max_val = rows['Hit@10'].max()
	max_rows = rows[rows['Hit@10']==max_val]

	return max_rows

def get_max_config_rows_without_query_reformulation(filename, config):
	df = pd.read_csv(filename)

	rows = df[(df['Task']==config) & (df["GUI Info for Query Expansion"]=='None') & (df["GUI Info for Query Replacement"]=='None')]
	max_val = rows['Hit@10'].max()
	max_rows = rows[rows['Hit@10']==max_val]

	return max_rows

def get_max_config_rows_with_query_expansion(filename, config):
	df = pd.read_csv(filename)

	rows = df[(df['Task']==config) & (df["GUI Info for Query Expansion"]!='None') & (df["GUI Info for Query Replacement"]=='None')]
	max_val = rows['Hit@10'].max()
	max_rows = rows[rows['Hit@10']==max_val]

	return max_rows

def get_max_config_rows_with_query_replacement(filename, config):
	df = pd.read_csv(filename)

	rows = df[(df['Task']==config) & (df["GUI Info for Query Expansion"]=='None') & (df["GUI Info for Query Replacement"]!='None')]
	max_val = rows['Hit@10'].max()
	max_rows = rows[rows['Hit@10']==max_val]

	return max_rows

def get_baseline_row(filename):
	df = pd.read_csv(filename)
	rows = df.loc[(df["Task"]=="QueryReformulation") & (df["GUI Info for Filtering"]=='NO') & (df["GUI Info for Boosting"]=='NO') & (df["GUI Info for Query Expansion"]=='None') & (df["GUI Info for Query Replacement"]=='None')]
	return rows.head()

def write_all_best_configs(write_file, rows):
	rows.to_csv(write_file, mode='a', header=False, float_format='%11.2f')

def main():
	approach_name = "Lucene"
	metric_file = "FinalResults/MetricsAll/" + approach_name + "Results.csv"
	best_config_file = "FinalResults/BestAmongAllConfigResults/" + approach_name + "BestConfigResults.csv"

	#metric_file = 'FinalResults/SentenceBERTResults.csv'
	#best_config_file = 'FinalResults/BestConfigResults/SentenceBERTBestConfigResults.csv'

	#metric_file = 'FinalResults/BugLocatorResults.csv'
	#best_config_file = 'FinalResults/BestConfigResults/BugLocatorBestConfigResults.csv'

	#metric_file = 'FinalResults/LuceneResults.csv'
	#best_config_file = 'FinalResults/BestConfigResults/LuceneBestConfigResults.csv'

	write_header_for_approach_rankings(best_config_file)

	# baseline = get_baseline_row(metric_file)
	# write_all_best_configs(best_config_file, baseline)

	best_config = get_max_config_rows(metric_file)
	write_all_best_configs(best_config_file, best_config)


if __name__ == "__main__":
	main()
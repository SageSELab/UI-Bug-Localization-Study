# UI BUG LOCALIZATION

### Data Preparation and Preprocessing
```DataPreparation/filter_files_cmnd.sh``` : Get all the filterted corpus and files which we need to boost

```ShortScripts/match_files_from_repo.sh```: Copy and paste files to a new directory based on query matching

```Lucene/code_search_ir_preprocess_data/run_cmnd.sh```: Preprocess queries

### Dataset:
```data/Ground-Truth-App-Screen.csv```: Contains Buggy Ground Truth Screen

```data/TraceReplayer-Data``` : Contains Trace-Replayer Data

```data/BugReports```: Contains Bug Reports

## SentenceBERT Results
```sentenceBERT/sentencebert-max-cmnd.sh```: Run to get all results for SentenceBERT

## UniXCoder Results
```Unixcoder/unixcoder-run-cmnd.sh```: Run to get all results for UniXCoder

## Lucene Results
```Lucene/code_search_ir_lucene_graph/run_cmnd.sh```: Run to get all results for Lucene

## BugLocator Results
```BugLocator/generate_xml_data_for_buglocator.sh```: Preprocess queries specifically for BugLocator.

```BugLocator/buglocator_cmnd.sh```: Run to get all results for BugLocator 

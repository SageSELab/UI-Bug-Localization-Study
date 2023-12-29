# UI Bug Localization Study

### InitialSteps
```ExtractGUIInformation/filter_files_cmnd.sh``` : Get all the filterted corpus and files which we need to boost

```AugmentationCorpus/match_files_from_repo.sh```: Copy and paste files to a new directory based on query matching

```Preprocessing/run_cmnd.sh```: Preprocess queries

## SentenceBERT
```sentenceBERT/sentencebert-max-cmnd.sh```: Run to get all results for SentenceBERT

## UniXCoder
```Unixcoder/unixcoder-run-cmnd.sh```: Run to get all results for UniXCoder

## Lucene
```Lucene/code_search_ir_lucene_graph/run_cmnd.sh```: Run to get all results for Lucene

## BugLocator
```BugLocator/generate_xml_data_for_buglocator.sh```: Preprocess queries specifically for BugLocator.

```BugLocator/buglocator_cmnd.sh```: Run to get all results for BugLocator 

## Metrics
```ResultComputation/results_summary.py```: Get metrics
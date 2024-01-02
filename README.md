# UI Bug Localization Study

### InitialSteps
```ExtractGUIInformation/filter_files_cmnd.sh``` : Get all the filterted corpus and files which we need to boost

```AugmentationCorpus/match_files_from_repo.sh```: Copy and paste files to a new directory based on query matching

```Preprocessing/run_cmnd.sh```: Preprocess queries

## SentenceBERT
### Dependency
```
conda install python=3.7.6
conda install pytorch=1.12.1
conda install transformers=4.24.0
conda install pandas=1.3.5
```

```sentenceBERT/sentencebert-run-cmnd.sh```: Run to get all results for SentenceBERT

## UniXCoder
### Dependency

```
conda install python=3.7.6
conda install pytorch=1.4.0
conda install transformers=2.1.1
conda install pandas=1.1.5
```

```Unixcoder/unixcoder-run-cmnd.sh```: Run to get all results for UniXCoder

## Lucene
```Lucene/code_search_ir_lucene_graph/run_cmnd.sh```: Run to get all results for Lucene

## BugLocator
```BugLocator/generate_xml_data_for_buglocator.sh```: Preprocess queries specifically for BugLocator.

```BugLocator/buglocator_cmnd.sh```: Run to get all results for BugLocator 

## Metrics
```ResultComputation/results_summary.py```: Get metrics
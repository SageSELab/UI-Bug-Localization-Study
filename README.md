# On Using GUI Interaction Data to Improve Text Retrieval-based Bug Localization
This article presents the replication package associated with our paper:
> Junayed Mahmud, Nadeeshan De Silva, Safwat Ali Khan, Seyed Hooman Mostafavi, SM Hasan Mansur, Oscar Chaparro, Andrian Marcus, and Kevin Moran, “_**On Using GUI Interaction Data to Improve Text Retrieval-based Bug Localization**_,” in Proceedings of the 46th IEEE/ACM International Conference on Software Engineering (ICSE 2024)

We provide access to the available dataset, source code and detailed instructions required to reproduce the experimental results discussed in our paper. We aim to apply for Available & Reusable badges and hope to further extend research on GUI-based bug localization. We recommend utilizing a recent version of the Mac operating system, and we have conducted our tests on Sonoma 14.0. We provide all of our source code in this [link](https://github.com/SageSELab/UI-Bug-Localization-Study) and the dataset is available in this [link](https://github.com/SageSELab/GUI-Bug-Localization-Data}).

# Paper Overview
One of the significant challenges in bug report management involves localizing the fault in source code based on the information provided in bug reports. This task is particularly complicated due to the incomplete or incorrect information in these reports. Researchers have attempted to automate the retrieval and ranking of relevant buggy files or code snippets using bug reports as queries. Although many researchers consider bug localization as a text-retrieval-based (TR) problem, there exists a noticeable semantic gap between the contents of bug reports and the source code written by developers. Researchers have explored various strategies to bridge this gap, such as processing bug reports or source code, or reformulating queries by incorporating information from diverse sources, including execution information, code dependencies, and historical data.

Our study explores leveraging graphical user interfaces (GUIs) in bug localization, which no prior research has thoroughly investigated. GUI information is readily obtainable and encapsulates the latent features of an application, manifested in pixel-based (i.e., screenshots) and metadata-based (i.e., html/uiautomator) information. Our objective is to utilize GUI information to boost the ranking of the files and also utilize it in query reformulation. We posit that analyzing the GUI of the application screen where a bug occurs, along with the one to three preceding screens, can aid in identifying faults in code. We refer to the GUI information on these screens as GUI interaction data. In our research, we specifically utilize three types of GUI interaction data: (1) the Activity and Window information for specific app screens, (2) the GUI components present in the selected app screens, and (3) the GUI components with which the user interacted on the selected app screens during bug reproduction. We believe that GUI interaction data can (i) filter out irrelevant files, (ii) boost relevant files, and (iii) aid in query reformulation.

To assess the effectiveness of GUI in bug localization, we employ four baseline approaches: BugLocator [1], Lucene [2], sentenceBERT [3], and UniXCoder [4]. Our focus is on bug localization within Android apps, specifically for four bug categories: crash, navigation, output, and cosmetic bugs. Our dataset comprises 80 fully localized Android bugs from 39 apps, with associated bug reproduction scenarios and GUI metadata. We compare these baseline TR-based bug localization approaches to 657 different configurations. Our findings reveal that the best-performing configurations of these techniques outperform the baseline approaches, resulting in an improvement in Hits@10 ranging from 13\% to 18\%. These augmentations imply that more files appear in the top-10 ranking of buggy files. Consequently, our results support the rationale that leveraging GUI information enhances bug localization approaches.

### InitialSteps
The entire experiment has been done on Mac. We recommend using x86_64 architecture on Mac. However, if a user is using Arm architecure, there is a workaround by running the following command to emulate x86_64:

```
conda config --env --set subdir osx-64
```

```ExtractGUIInformation/filter_files_cmnd.sh``` : Get all the filterted corpus and files which we need to boost

```AugmentationCorpus/match_files_from_repo.sh```: Copy and paste files to a new directory based on query matching

```Preprocessing/run_cmnd.sh```: Preprocess queries

```Preprocessing-BugLocator/generate_xml_data_for_buglocator.sh```: The preprocessing for BugLocator is different comparent to other approaches. Use this script to generate preprocessed queries for BugLocator.

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
- Install JDK 11+
- Install Apache Maven using the following command:
```
conda install -c conda-forge maven=3.9.6
```
-  Clone the following Repos:
    - [appcore](https://github.com/ojcchar/appcore)
    - [text-analyzer](https://github.com/ojcchar/text-analyzer)
- Go to ```appcore/appcore``` in the terminal and run the following command:
```
./gradlew clean testClasses install
```
- Go to ```text-analyzer/text-analyzer``` in the terminal and run the following command:
```
./gradlew clean testClasses install
```
- Go to ```Lucene/lib``` in the terminal and run the following command:
```
mvn install:install-file "-Dfile=ir4se-fwk-0.0.2.jar" "-DgroupId=edu.wayne.cs.severe" "-DartifactId=ir4se-fwk" "-Dversion=0.0.2" "-Dpackaging=jar"
``````
- Run the following shell script: ```Lucene/run_cmnd.sh```

## BugLocator
### Dependency
```
conda install python=3.7.6
conda install bs4=4.11.1
conda install pandas=1.3.5
conda install lxml=4.9.1
```

```BugLocator/buglocator_cmnd.sh```: Run to get all results for BugLocator 

## Metrics
```ResultComputation/results_summary.py```: Get metrics

### References
1. Jian Zhou, Hongyu Zhang, and David Lo. 2012. Where Should the Bugs Be Fixed? More Accurate Information Retrieval-Based Bug Localization Based on Bug Reports. In ICSE’12. 14–24.
2. Apache Lucene - https://lucene.apache.org (2023).
3. Nils Reimers and Iryna Gurevych. 2019. Sentence-bert: Sentence embeddings using siamese bert-networks. EMNLP’19 (2019).
4. DayaGuo,ShuaiLu,NanDuan,YanlinWang,MingZhou,andJianYin.2022. UniXcoder: Uni￿ed Cross-Modal Pre-training for Code Representation. ACL’22 (2022).




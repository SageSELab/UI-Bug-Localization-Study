# On Using GUI Interaction Data to Improve Text Retrieval-based Bug Localization
This article presents the replication package associated with our paper:
> Junayed Mahmud, Nadeeshan De Silva, Safwat Ali Khan, Seyed Hooman Mostafavi, SM Hasan Mansur, Oscar Chaparro, Andrian Marcus, and Kevin Moran, “_**On Using GUI Interaction Data to Improve Text Retrieval-based Bug Localization**_,” in Proceedings of the 46th IEEE/ACM International Conference on Software Engineering (ICSE 2024)

We provide access to the available dataset, source code and detailed instructions required to reproduce the experimental results discussed in our paper. We aim to apply for Available & Reusable badges and hope to further extend research on GUI-based bug localization. We recommend utilizing a recent version of the Mac operating system, and we have conducted our tests on Sonoma 14.0. We provide all of our source code in this [link](https://github.com/SageSELab/UI-Bug-Localization-Study) and the dataset is available in this [link](https://github.com/SageSELab/GUI-Bug-Localization-Data}).

# Paper Overview
One of the significant challenges in bug report management involves localizing the fault in source code based on the information provided in bug reports. This task is particularly complicated due to the incomplete or incorrect information in these reports. Researchers have attempted to automate the retrieval and ranking of relevant buggy files or code snippets using bug reports as queries. Although many researchers consider bug localization as a text-retrieval-based (TR) problem, there exists a noticeable semantic gap between the contents of bug reports and the source code written by developers. Researchers have explored various strategies to bridge this gap, such as processing bug reports or source code, or reformulating queries by incorporating information from diverse sources, including execution information, code dependencies, and historical data.

Our study explores leveraging graphical user interfaces (GUIs) in bug localization, which no prior research has thoroughly investigated. GUI information is readily obtainable and encapsulates the latent features of an application, manifested in pixel-based (i.e., screenshots) and metadata-based (i.e., html/uiautomator) information. Our objective is to utilize GUI information to boost the ranking of the files and also utilize it in query reformulation. We posit that analyzing the GUI of the application screen where a bug occurs, along with the one to three preceding screens, can aid in identifying faults in code. We refer to the GUI information on these screens as GUI interaction data. In our research, we specifically utilize three types of GUI interaction data: (1) the Activity and Window information for specific app screens, (2) the GUI components present in the selected app screens, and (3) the GUI components with which the user interacted on the selected app screens during bug reproduction. We believe that GUI interaction data can (i) filter out irrelevant files, (ii) boost relevant files, and (iii) aid in query reformulation.

To assess the effectiveness of GUI in bug localization, we employ four baseline approaches: BugLocator [1], Lucene [2], sentenceBERT [3], and UniXCoder [4]. Our focus is on bug localization within Android apps, specifically for four bug categories: crash, navigation, output, and cosmetic bugs. Our dataset comprises 80 fully localized Android bugs from 39 apps, with associated bug reproduction scenarios and GUI metadata. We compare these baseline TR-based bug localization approaches to 657 different configurations. Our findings reveal that the best-performing configurations of these techniques outperform the baseline approaches, resulting in an improvement in Hits@10 ranging from 13\% to 18\%. These augmentations imply that more files appear in the top-10 ranking of buggy files. Consequently, our results support the rationale that leveraging GUI information enhances bug localization approaches.

# Experiments
The entire experiment has been done on Mac. We recommend using the x86_64 architecture on Mac. However, if a user is using Arm architecture, there is a workaround by running the following command to emulate x86_64:
```
conda config --env --set subdir osx-64
```
A user needs to install [Anaconda](https://www.anaconda.com) to run the experiments. Most of the experiments are done by running either a shell script or a Python file. To run all the scripts, a user has to update thespecific path in the variable ```data_dir``` that contains the link for the [dataset](https://github.com/SageSELab/GUI-Bug-Localization-Data}) and ```package_dir``` that contains the [replication package](https://github.com/SageSELab/UI-Bug-Localization-Study).

_**Note: A user can ignore the preprocessing steps and can use the already preprocessed data. However, in that case, the user needs to update ```preprocessed_code_dir``` variable with ```/Users/sagelab/Documents/Projects/BugLocalization/Artifact-ICSE24/GUI-Bug-Localization-Data/BuggyProjects``` if it exists in each shell script when generating rankings**_

## Initial Steps
#### Environment Setup
- Install the following packages:
```
conda install python=3.7.6
conda install bs4=4.11.1
conda install anaconda::nltk
conda install pandas=1.3.5
```
- Install JDK 11
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
- Go to ```Preprocessing/lib``` in the terminal and run the following command:
```
mvn install:install-file "-Dfile=ir4se-fwk-0.0.2.jar" "-DgroupId=edu.wayne.cs.severe" "-DartifactId=ir4se-fwk" "-Dversion=0.0.2" "-Dpackaging=jar"
```

### Preprocessing
The user has to run the following scripts for preprocessing:
1. ```ExtractGUIInformation/filter_files_cmnd.sh``` : This script will extract necessary GUI information and get all the filenames that are necessary for text-retrieval augmentation methods.

2. ```AugmentationCorpus/match_files_from_repo.sh```: From the filenames extracted in the previous step, this script will copy and paste all the files into another directory. This step significantly improves running experiments because we have 657 configurations for each baseline.

3. ```Preprocessing/run_cmnd.sh```: To perform the preprocessing of the queries and source code a user needs to run this shell script. A user needs to perform preprocessing for four types of information by updating ```content_type``` variable. This variable should contain specifically four values one by one: 
- Title: Preprocess Bug Report Titles. Only necessary for BugLocator.
- Content: Preprocess Bug Report Contents. Only necessary for BugLocator. 
- BugReport: Preprocess Bug Reports. It is necessary for all baselines except BugLocator.
- Code: Preprocess Source Code. It is necessary for all baselines.

4. ```Preprocessing-BugLocator/generate_xml_data_for_buglocator.sh```: The preprocessing for BugLocator is different compared to other approaches. A user needs to run this script to generate preprocessed queries for BugLocator.


## SentenceBERT
#### Dependencies
A user needs to run the following commands to perform environment setup.
```
conda install python=3.7.6
conda install pytorch=1.12.1
conda install transformers=4.24.0
conda install pandas=1.3.5
```
#### Run
```sentenceBERT/sentencebert-cmnd-all.sh```: Run to get rankings for all configurations for SentenceBERT.
```sentenceBERT/sentencebert-cmnd-small.sh```: Run to get rankings for a subset of configurations for SentenceBERT.

## UniXCoder
#### Dependencies
A user needs to run the following commands to perform environment setup.
```
conda install python=3.7.6
conda install pytorch=1.4.0
conda install transformers=2.1.1
conda install pandas=1.1.5
```
#### Run
```Unixcoder/unixcoder-cmnd-all.sh```: Run to get rankings for all configurations for UniXCoder.
```Unixcoder/unixcoder-cmnd-small.sh```: Run to get rankings for a subset of configurations for UniXCoder.

## Lucene
#### Environment Setup
- Install JDK 11
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
```
#### Run
```Lucene/lucene-cmnd-all.sh```: Run to get rankings for all configuartions for Lucene.

```Lucene/lucene-cmnd-small.sh```: Run to get rankings for a subset of configuartions for Lucene.

## BugLocator
#### Dependencies
A user needs to run the following commands to perform environment setup.
```
conda install python=3.7.6
conda install bs4=4.11.1
conda install pandas=1.3.5
conda install lxml=4.9.1
```

#### Run
```BugLocator/buglocator-cmnd-all.sh```: Run to get rankings for all configurations for BugLocator.
```BugLocator/buglocator-cmnd-small.sh```: Run to get rankings for a subset of configurations for BugLocator.

## Metrics
Install the following packages:
```
conda install pandas=1.3.5
```
#### Run
```ResultComputation/results-summary-all.py```: Running the previous baselines will provide ranks of the buggy files. To calculate metrics for all configurations, the user needs to update the ```approach_name``` variable with one of the following baseline names: BugLocator or Lucene or SentenceBERT or UniXCoder. 
```ResultComputation/results-summary-small.py```: To calculate metrics for a subset of configurations, the user needs to update the ```approach_name``` variable with one of the following baseline names: BugLocator or Lucene or SentenceBERT or UniXCoder. 

The results will be saved in ```MetricsAll```.

### References
1. Jian Zhou, Hongyu Zhang, and David Lo. 2012. Where Should the Bugs Be Fixed? More Accurate Information Retrieval-Based Bug Localization Based on Bug Reports. In ICSE’12. 14–24.
2. Apache Lucene - https://lucene.apache.org (2023).
3. Nils Reimers and Iryna Gurevych. 2019. Sentence-bert: Sentence embeddings using siamese bert-networks. EMNLP’19 (2019).
4. Daya Guo, Shuai Lu, Nan Duan, Yanlin Wang, Ming Zhou, and Jian Yin. 2022. UniXcoder: Unified Cross-Modal Pre-training for Code Representation. ACL’22 (2022).




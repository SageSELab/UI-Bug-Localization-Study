FROM continuumio/miniconda3

WORKDIR /Users/sagelab/Documents/Projects/BugLocalization/Artifact-ICSE24
COPY ./UI-Bug-Localization-Study ./UI-Bug-Localization-Study
COPY ./GUI-Bug-Localization-Data ./GUI-Bug-Localization-Data
COPY ./environment.yml ./environment.yml
COPY ./appcore ./appcore
COPY ./text-analyzer ./text-analyzer

RUN conda env create -n buglocalizationenv -f environment.yml
RUN echo "source activate buglocalizationenv" > ~/.bashrc
ENV PATH /opt/conda/envs/buglocalizationenv/bin:$PATH

RUN cd appcore/appcore && ./gradlew clean testClasses install && cd ../..
RUN cd text-analyzer/text-analyzer && ./gradlew clean testClasses install && cd ../..
RUN cd UI-Bug-Localization-Study/Lucene/lib && mvn install:install-file "-Dfile=ir4se-fwk-0.0.2.jar" "-DgroupId=edu.wayne.cs.severe" "-DartifactId=ir4se-fwk" "-Dversion=0.0.2" "-Dpackaging=jar" && cd ../../..




#!/bin/sh
export JAVA_HOME=`/usr/libexec/java_home -v 1.11`
set REPOSITORIES_PATH=UIBugLocalization/Lucene

set CUR_DIR=$CD

set APPCORE_REPO_PATH=UIBugLocalization/Lucene/appcore/appcore
set TXT_ANALYZER_REPO_PATH=UIBugLocalization/Lucene/text-analyzer/text-analyzer
set CODE_RCH_REPO_PATH=UIBugLocalization/Lucene/code_rch_ir
set CODE_RCH_REPO_PATH_LIB=UIBugLocalization/Lucene/code_rch_ir/lib

cd "${APPCORE_REPO_PATH}" && ./gradlew clean testClasses install && @echo on
cd "${TXT_ANALYZER_REPO_PATH}" && ./gradlew clean testClasses install && @echo on

echo "Hello"

cd "${CODE_RCH_REPO_PATH_LIB}"
mvn install:install-file "-Dfile=ir4se-fwk-0.0.2.jar" "-DgroupId=.cs.severe" "-DartifactId=ir4se-fwk" "-Dversion=0.0.2" "-Dpackaging=jar"

cd "$CODE_RCH_REPO_PATH" && mvn package -DskipTests && @echo on

"$JAVA_HOME/bin/java" -cp target/code_rch_ir-1.0.jar MainClass

cd "$CUR_DIR"
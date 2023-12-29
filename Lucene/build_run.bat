REM change the JAVA_HOME path (JRE/JDK 11+)
set JAVA_HOME=C:\Program Files\Java\jdk-12.0.2
REM change this path
set REPOSITORIES_PATH=C:\Users\ojcch\Documents\Repositories\projects

REM -------------------------------------------------

set CUR_DIR=%CD%

set APPCORE_REPO_PATH=%REPOSITORIES_PATH%\appcore
set TXT_ANALYZER_REPO_PATH=%REPOSITORIES_PATH%\text-analyzer
set CODE_SEARCH_REPO_PATH=%REPOSITORIES_PATH%\code_search_ir

REM project building
cd "%APPCORE_REPO_PATH%\appcore" && call gradlew clean testClasses install && @echo on
cd "%TXT_ANALYZER_REPO_PATH%\text-analyzer" && call gradlew clean testClasses install && @echo on

REM install additional libraries
cd "%CODE_SEARCH_REPO_PATH%\lib"
call mvn install:install-file "-Dfile=ir4se-fwk-0.0.2.jar" "-DgroupId=edu.wayne.cs.severe" "-DartifactId=ir4se-fwk" "-Dversion=0.0.2" "-Dpackaging=jar"

cd "%CODE_SEARCH_REPO_PATH%" && call mvn package -DskipTests  && @echo on

call "%JAVA_HOME%/bin/java" -cp target/code_search_ir-1.0.jar MainClass

cd "%CUR_DIR%"
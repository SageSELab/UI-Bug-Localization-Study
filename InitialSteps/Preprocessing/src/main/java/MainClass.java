import edu.wayne.cs.severe.ir4se.processor.controllers.RetrievalEvaluator;
import edu.wayne.cs.severe.ir4se.processor.controllers.impl.DefaultRetrievalEvaluator;
import edu.wayne.cs.severe.ir4se.processor.controllers.impl.RAMRetrievalIndexer;
import edu.wayne.cs.severe.ir4se.processor.controllers.impl.lucene.LuceneRetrievalSearcher;
import edu.wayne.cs.severe.ir4se.processor.entity.Query;
import edu.wayne.cs.severe.ir4se.processor.entity.RelJudgment;
import edu.wayne.cs.severe.ir4se.processor.entity.RetrievalDoc;
import edu.wayne.cs.severe.ir4se.processor.entity.RetrievalStats;
import org.apache.commons.lang3.StringUtils;
import org.apache.lucene.store.Directory;
import seers.textanalyzer.PreprocessingOptionsParser;
import seers.textanalyzer.TextProcessor;
import seers.textanalyzer.entity.Sentence;
import seers.textanalyzer.entity.Token;

import java.util.*;
import java.util.stream.Collectors;
import java.util.stream.IntStream;
import java.io.*;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.nio.file.Path;
import org.apache.commons.io.FileUtils;
import java.nio.charset.StandardCharsets;
import org.json.simple.JSONArray;
import org.json.simple.JSONObject;
import org.json.simple.parser.*;
import com.opencsv.CSVWriter;
import java.lang.String;
import com.opencsv.*;

import net.sourceforge.argparse4j.ArgumentParsers;
import net.sourceforge.argparse4j.inf.ArgumentParser;
import net.sourceforge.argparse4j.inf.ArgumentParserException;
import net.sourceforge.argparse4j.inf.Namespace;

public class MainClass {

    private static String preprocessText(String text, List<String> stopWords) {

        String[] preprocessingOptions = {PreprocessingOptionsParser.CAMEL_CASE_SPLITTING,
                PreprocessingOptionsParser.NUMBERS_REMOVAL, PreprocessingOptionsParser.PUNCTUATION_REMOVAL,
                PreprocessingOptionsParser.SHORT_TOKENS_REMOVAL + " 3",
                PreprocessingOptionsParser.SPECIAL_CHARS_REMOVAL};

        if (StringUtils.isBlank(text)) return null;
        List<Sentence> prepSentences = TextProcessor.preprocessText(text, stopWords, preprocessingOptions);
        List<Token> allTokens = TextProcessor.getAllTokens(prepSentences);
        return allTokens.stream().map(Token::getLemma).collect(Collectors.joining(" "));
    }
    
    //https://stackoverflow.com/questions/3571223/how-do-i-get-the-file-extension-of-a-file-in-java
    private static String getFileExtension(File file) {
        String name = file.getName();
        int lastIndexOf = name.lastIndexOf(".");
        if (lastIndexOf == -1) {
            return ""; // empty extension
        }
        return name.substring(lastIndexOf);
    }

    //https://stackoverflow.com/questions/14676407/list-all-files-in-the-folder-and-also-sub-folders
    public static void listf(String directoryName, List<File> files) {
	    File directory = new File(directoryName);
	
	    // Get all files from a directory.
	    File[] fList = directory.listFiles();
	    if(fList != null) {
	        for (File file : fList) {      
	            if (file.isFile()) {
                    
                    String extension = getFileExtension(file);
                    if(extension.equals(".java")) {
                    	files.add(file);
                    }
	            } else if (file.isDirectory()) {
	                listf(file.getAbsolutePath(), files);
	            }
	        }
	    }
	}

    //https://stackoverflow.com/questions/12169038/read-csv-file-column-by-column
    private static List<String> getFiles(String bugID, String csvFile) throws Exception {
    	List<String> files = new ArrayList<String>();
		try {
			//csv file containing data
			String strFile = csvFile;
			CSVReader reader = new CSVReader(new FileReader(strFile));
			String [] nextLine;
			int lineNumber = 0;
			while ((nextLine = reader.readNext()) != null) {
				lineNumber++;

				if(bugID.equals(nextLine[0])) {
					files.add(nextLine[1]);
				}
			}
		} catch(Exception e) {
            e.printStackTrace();
        }
		return files;
    }

    public static List<String> removeDuplicates(List<String> myList)
    {
        Set<String> set = new HashSet<>();

        List<String>uniqueList = new ArrayList<String>();
        for(int i=0;i<myList.size();i++) {
            if(!set.contains(myList.get(i))) {
                uniqueList.add(myList.get(i));
                set.add(myList.get(i));
            }
        }
		return uniqueList;
    }

    private static String getActivitiesFragments(String bugID, String csvFile) throws Exception {
    	List<String> queryItems = new ArrayList<String>();
		try {
			//csv file containing data
			String strFile = csvFile;
			CSVReader reader = new CSVReader(new FileReader(strFile));
			String [] nextLine;
			int lineNumber = 0;
			while ((nextLine = reader.readNext()) != null) {
				lineNumber++;

				if(bugID.equals(nextLine[0])) {
					String[] activity_splits = nextLine[1].split("[, \\[\\]']");
					for(int i=0;i<activity_splits.length;i++) {
						queryItems.add(activity_splits[i]);
					}

					String[] fragment_splits = nextLine[2].split("[, \\[\\]']");
					for(int i=0;i<fragment_splits.length;i++) {
						queryItems.add(fragment_splits[i]);
					}
				}
			}
		} catch(Exception e) {
            e.printStackTrace();
        }

        queryItems = removeDuplicates(queryItems);
		return String.join(" ", queryItems);
    }

    private static String getActivitiesFragmentsInteractedIDs(String bugID, String csvFile) throws Exception {
    	List<String> queryItems = new ArrayList<String>();
		try {
			//csv file containing data
			String strFile = csvFile;
			CSVReader reader = new CSVReader(new FileReader(strFile));
			String [] nextLine;
			int lineNumber = 0;
			while ((nextLine = reader.readNext()) != null) {
				lineNumber++;

				if(bugID.equals(nextLine[0])) {
					String[] activity_splits = nextLine[1].split("[, \\[\\]']");
					for(int i=0;i<activity_splits.length;i++) {
						queryItems.add(activity_splits[i]);
					}

					String[] fragment_splits = nextLine[2].split("[, \\[\\]']");
					for(int i=0;i<fragment_splits.length;i++) {
						queryItems.add(fragment_splits[i]);
					}

					String[] interacted_component_splits = nextLine[3].split("[, \\[\\]']");
					for(int i=0;i<interacted_component_splits.length;i++) {
						queryItems.add(interacted_component_splits[i]);
					}
				}
			}
		} catch(Exception e) {
            e.printStackTrace();
        }

        queryItems = removeDuplicates(queryItems);
		return String.join(" ", queryItems);
    }

    private static String getInteractedIDs(String bugID, String csvFile) throws Exception {
        List<String> queryItems = new ArrayList<String>();
        try {
            //csv file containing data
            String strFile = csvFile;
            CSVReader reader = new CSVReader(new FileReader(strFile));
            String [] nextLine;
            int lineNumber = 0;
            while ((nextLine = reader.readNext()) != null) {
                lineNumber++;

                if(bugID.equals(nextLine[0])) {
                    String[] interacted_component_splits = nextLine[3].split("[, \\[\\]']");
                    for(int i=0;i<interacted_component_splits.length;i++) {
                        queryItems.add(interacted_component_splits[i]);
                    }
                }
            }
        } catch(Exception e) {
            e.printStackTrace();
        }

        queryItems = removeDuplicates(queryItems);
        return String.join(" ", queryItems);
    }


    private static String getActivitiesFragmentsAllGUIIDs(String bugID, String csvFile) throws Exception {
        List<String> queryItems = new ArrayList<String>();
        try {
            //csv file containing data
            String strFile = csvFile;
            CSVReader reader = new CSVReader(new FileReader(strFile));
            String [] nextLine;
            int lineNumber = 0;
            while ((nextLine = reader.readNext()) != null) {
                lineNumber++;

                if(bugID.equals(nextLine[0])) {
                    String[] activity_splits = nextLine[1].split("[, \\[\\]']");
                    for(int i=0;i<activity_splits.length;i++) {
                        queryItems.add(activity_splits[i]);
                    }

                    String[] fragment_splits = nextLine[2].split("[, \\[\\]']");
                    for(int i=0;i<fragment_splits.length;i++) {
                        queryItems.add(fragment_splits[i]);
                    }

                    String[] all_component_splits = nextLine[4].split("[, \\[\\]']");
                    for(int i=0;i<all_component_splits.length;i++) {
                        queryItems.add(all_component_splits[i]);
                    }
                }
            }
        } catch(Exception e) {
            e.printStackTrace();
        }

        queryItems = removeDuplicates(queryItems);
        return String.join(" ", queryItems);
    }

    private static String getAllGUIIDs(String bugID, String csvFile) throws Exception {
        List<String> queryItems = new ArrayList<String>();
        try {
            //csv file containing data
            String strFile = csvFile;
            CSVReader reader = new CSVReader(new FileReader(strFile));
            String [] nextLine;
            int lineNumber = 0;
            while ((nextLine = reader.readNext()) != null) {
                lineNumber++;
 
                if(bugID.equals(nextLine[0])) {
                    String[] all_component_splits = nextLine[4].split("[, \\[\\]']");
                    for(int i=0;i<all_component_splits.length;i++) {
                        queryItems.add(all_component_splits[i]);
                    }
                }
            }
        } catch(Exception e) {
            e.printStackTrace();
        }

        queryItems = removeDuplicates(queryItems);
        return String.join(" ", queryItems);
    }

    private static void write_to_text_file(String filename, String content) {
        try {
          FileWriter myWriter = new FileWriter(filename);
          myWriter.write(content);
          myWriter.close();
        } catch (IOException e) {
          System.out.println("An error occurred.");
          e.printStackTrace();
        }
    }

    private static void processResults(List<String> stopWords, String bugID, List<String>codeFileContent, 
    	List<String>codeFileNameList, CSVWriter writer) throws Exception{
        //preprocess files
        List<String> preprocessedCodeDocuments =
                codeFileContent.stream().map(text -> preprocessText(text, stopWords))
                        .collect(Collectors.toList());
        //build corpus
        List<RetrievalDoc> corpus = IntStream.range(0, preprocessedCodeDocuments.size())
                .mapToObj(i -> {
                    String docText = preprocessedCodeDocuments.get(i);
                    
                    if (StringUtils.isBlank(docText)) return null;
                    int docId = i;
                    String docName = codeFileNameList.get(i);

                    List<String> row = new ArrayList<String>();
                    row.add(docName);
                    row.add(docText);
                    String[] rowArray = new String[row.size()];

                    for (int l = 0; l < row.size(); l++) {
                        rowArray[l] = row.get(l);
                    }
                    writer.writeNext(rowArray);
                    return new RetrievalDoc(docId, docText, docName);
                })
                .filter(Objects::nonNull)
                .collect(Collectors.toList());

        writer.close();
    }

    private static void createDirectories(String filepath) {
        File file = new File(filepath);
        File parent = new File(file.getParent());
        if (!parent.exists()) {
            parent.mkdirs();
        }
    }

    private static void createDirectoryIfNotExist(String dir) {
        File parent = new File(dir);
        if (!parent.exists()) {
            parent.mkdirs();
        }
    }

    private static void processBugReport(String bugID, String bugReportContent, String infoFromGUI, List<String> stopWords, String queryGui, String preprocessDataFolder) {
        String preprocessedBugReport = preprocessText(bugReportContent, stopWords);
        Query query = new Query(1, preprocessedBugReport);

        String bug_report_preprocessed_file = preprocessDataFolder + "/Preprocessed_with_" + queryGui + "/bug_report_original/bug_report_" + bugID + ".txt";
        createDirectories(bug_report_preprocessed_file);
        write_to_text_file(bug_report_preprocessed_file, preprocessedBugReport);

        String preprocessedReplacedQuery = preprocessText(infoFromGUI, stopWords);
        String replacedQueryFile =  preprocessDataFolder + "/Preprocessed_with_" + queryGui + "/replaced_query/bug_report_" + bugID + ".txt";
        createDirectories(replacedQueryFile);
        if(preprocessedReplacedQuery==null || preprocessedReplacedQuery.length()<1) {
            preprocessedReplacedQuery = "";
        }
        write_to_text_file(replacedQueryFile, preprocessedReplacedQuery);

        String preprocessedQueryExpansion1 = preprocessText(bugReportContent + " " + infoFromGUI, stopWords);
        String queryExpansion1File =  preprocessDataFolder + "/Preprocessed_with_" + queryGui + "/query_expansion_1/bug_report_" + bugID + ".txt";
        createDirectories(queryExpansion1File);
        write_to_text_file(queryExpansion1File, preprocessedQueryExpansion1);

        String preprocessedQueryExpansion2 = preprocessText(bugReportContent + " " + infoFromGUI + " " + infoFromGUI, stopWords);
        String queryExpansion2File =  preprocessDataFolder + "/Preprocessed_with_" + queryGui + "/query_expansion_2/bug_report_" + bugID + ".txt";
        createDirectories(queryExpansion2File);
        write_to_text_file(queryExpansion2File, preprocessedQueryExpansion2);

        String preprocessedQueryExpansion3 = preprocessText(bugReportContent + " " + infoFromGUI + " " + infoFromGUI + " " + infoFromGUI, stopWords);
        String queryExpansion3File =  preprocessDataFolder + "/Preprocessed_with_" + queryGui + "/query_expansion_3/bug_report_" + bugID + ".txt";
        createDirectories(queryExpansion3File);
        write_to_text_file(queryExpansion3File, preprocessedQueryExpansion3);
    }

     private static void processBugReportTitle(String bugID, String bugReportContent, List<String> stopWords, String preprocessDataFolder) {
        String preprocessedBugReport = preprocessText(bugReportContent, stopWords);
        Query query = new Query(1, preprocessedBugReport);

        String bug_report_preprocessed_file = preprocessDataFolder + "/bug_report_titles/bug_title_" + bugID + ".txt";
        createDirectories(bug_report_preprocessed_file);
        if(bug_report_preprocessed_file==null || bug_report_preprocessed_file.length()<1) {
            bug_report_preprocessed_file = "";
        }
        write_to_text_file(bug_report_preprocessed_file, preprocessedBugReport);
    }

    //run this class/method using project directory as the working directory for the program
    public static void main(String[] args) throws Exception {
        //https://argparse4j.github.io
        ArgumentParser parser = ArgumentParsers.newFor("MainClass").build().defaultHelp(true).description("MainClass Arguments");
        parser.addArgument("-br", "--bug_reports");
        parser.addArgument("-qinfo", "--query_infos_file");
        parser.addArgument("-s", "--screens");
        parser.addArgument("-c", "--corpus_type");
        parser.addArgument("-preq", "--preprocess_data");
        parser.addArgument("-ctype", "--content_type");
        parser.addArgument("-bp", "--buggy_projects");

        Namespace ns = null;
        try {
            ns = parser.parseArgs(args);
        } catch (ArgumentParserException e) {
            parser.handleError(e);
            System.exit(1);
        }

        //read stop words
        String stopWordsPath = "src/main/resources/java-keywords-bugs.txt";
        List<String> stopWords = TextProcessor.readStopWords(stopWordsPath);

        //Bug IDs
        ArrayList<String> bug_issue_ids = new ArrayList<String>(Arrays.asList("2", "8", "10", "11", 
                "18", "19", "44", "45", "53", "54", "55", "56", "71", "76", "84", "87", "92", "106", "110",
                "117", "128", "129", "130", "135", "158", "159", "160", "162", "168", "191", "192", "193",
                "199", "200", "201", "206", "209", "227", "248", "256", "271", "275", "1028", "1073", 
                "1089", "1096", "1130", "1146", "1147", "1150", "1151", "1198", "1202", "1205", "1207",
                "1213", "1214", "1215", "1222", "1223", "1224", "1228", "1299", "1389", "1399", "1402",
                "1403", "1406", "1425", "1428", "1430", "1441", "1445", "1446", "1481", "1563", "1568", 
                "1640", "1641", "1645"));

        String screen_path = "Screen-" + ns.getString("screens");
        String corpus_path = screen_path + "/Corpus-" + ns.getString("corpus_type");
        String queryInfoFile = ns.getString("query_infos_file") + "/" + corpus_path + "/Queries.csv";  

        for(int b_index=0;b_index<bug_issue_ids.size();b_index++) {

            if (ns.getString("content_type").equals("Code")) {
                List<String>codeFileContent = new ArrayList<String>();
                List<String>codeFileNameList = new ArrayList<String>();
                createDirectoryIfNotExist(ns.getString("preprocess_data"));
                FileWriter preprocessedCodeFile = new FileWriter(ns.getString("preprocess_data") + "/bug-" + bug_issue_ids.get(b_index) + ".csv", true);
                CSVWriter writer = new CSVWriter(preprocessedCodeFile);
                String header[] = {"FilePath", "PreprocessedCode"};
                writer.flush();
                writer.writeNext(header);
                String path = ns.getString("buggy_projects") + "/bug-" + bug_issue_ids.get(b_index);
                List<File> files = new ArrayList<File>();
                listf(path,files);
                for(int i=0;i<files.size();i++) {
                	codeFileNameList.add(files.get(i).toString());
                	String content = FileUtils.readFileToString(files.get(i), StandardCharsets.UTF_8);
                	codeFileContent.add(content);
                }

                processResults(stopWords, bug_issue_ids.get(b_index), codeFileContent, codeFileNameList, writer);
            }

            else if (ns.getString("content_type").equals("Title")) {
                String bugReportTitlePath = ns.getString("bug_reports") + "/bug_title_" + bug_issue_ids.get(b_index) + ".txt";
                String bugReportTitle = FileUtils.readFileToString(new File(bugReportTitlePath), StandardCharsets.UTF_8);

                processBugReportTitle(bug_issue_ids.get(b_index), bugReportTitle, stopWords, ns.getString("preprocess_data") + "/" + screen_path);
            }
    
	        else if (ns.getString("content_type").equals("Content") || ns.getString("content_type").equals("BugReport")) {
                //bug report
                String bugReportFilePath = ns.getString("bug_reports") + "/bug_report_" + bug_issue_ids.get(b_index) + ".txt";
                String bugReportContent = FileUtils.readFileToString(new File(bugReportFilePath), StandardCharsets.UTF_8);

                List<String> query_types = new ArrayList<String>(Arrays.asList("GUI_States", "Interacted_GUI_Component_IDs", "GUI_State_and_Interacted_GUI_Component_IDs",
                     "All_GUI_Component_IDs", "GUI_State_and_All_GUI_Component_IDs"));

                String infoFromGUI = "";
                for (String query: query_types) {
                    if (query.equals("GUI_States")) {
                        infoFromGUI = getActivitiesFragments(bug_issue_ids.get(b_index), queryInfoFile);
                    } else if(query.equals("Interacted_GUI_Component_IDs")) {
                        infoFromGUI = getInteractedIDs(bug_issue_ids.get(b_index), queryInfoFile);
                    } else if(query.equals("GUI_State_and_Interacted_GUI_Component_IDs")) {
                        infoFromGUI = getActivitiesFragmentsInteractedIDs(bug_issue_ids.get(b_index), queryInfoFile);
                    } else if(query.equals("All_GUI_Component_IDs")) {
                        infoFromGUI = getAllGUIIDs(bug_issue_ids.get(b_index), queryInfoFile);
                    } else if(query.equals("GUI_State_and_All_GUI_Component_IDs")) {
                        infoFromGUI = getActivitiesFragmentsAllGUIIDs(bug_issue_ids.get(b_index), queryInfoFile);
                    }

                    processBugReport(bug_issue_ids.get(b_index), bugReportContent, infoFromGUI, stopWords, query, ns.getString("preprocess_data") + "/" + screen_path);
                }
            }
	        
            
        }
    }

}

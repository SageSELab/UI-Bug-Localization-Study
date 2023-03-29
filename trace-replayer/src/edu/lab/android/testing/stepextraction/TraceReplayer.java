/*******************************************************************************
 * Copyright (c) 2016, 
 * All rights reserved.
 *  
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *
 * 1. Redistributions of source code must retain the above copyright notice, this
 *    list of conditions and the following disclaimer.
 * 2. Redistributions in binary form must reproduce the above copyright notice,
 *    this list of conditions and the following disclaimer in the documentation
 *    and/or other materials provided with the distribution.
 *  
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
 * ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
 * WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
 * ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
 * (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
 * LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
 * ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 * SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 *  
 * The views and conclusions contained in the software and documentation are those
 * of the authors and should not be interpreted as representing official policies,
 * either expressed or implied, of the FreeBSD Project.
 *******************************************************************************/
package edu..android.testing.stepextraction;

import java.awt.Image;
import java.awt.image.BufferedImage;
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStream;
import java.io.PrintWriter;
import java.lang.reflect.Constructor;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.logging.Level;
import java.util.logging.Logger;

import javax.imageio.ImageIO;

import org.yaml.snakeyaml.Yaml;

import com.google.gson.Gson;
import com.google.gson.JsonElement;
import com.google.gson.JsonIOException;

import edu..android.testing.helpers.DeviceInfo;
import edu..android.testing.helpers.StepByStepEngine;
import edu..android.testing.helpers.TerminalHelper;
import edu..android.testing.helpers.Utilities;
import edu..android.testing.helpers.UiAutoConnector;
import edu..android.testing.helpers.UiAutoConnector.TypeDeviceEnum;
import edu..android.core.model.DynGuiComponentVO;
import edu..android.core.model.GUIEventVO;
import edu..android.core.model.Transition;
import edu..android.core.model.WindowVO;
import edu..android.testing.CrashScope;
import edu..android.testing.helpers.ClonerHelper;
import edu..android.testing.helpers.DeviceHelper;
import edu..android.testing.helpers.EventsFormatter;
import edu..android.testing.helpers.ScreenActionData;
import edu..android.testing.helpers.ScreenshotModifier;
import edu..android.core.entity.model.App;
import edu..android.core.entity.model.fusion.DynGuiComponent;
import edu..android.core.entity.model.fusion.DynamicTransition;
import edu..android.core.entity.model.fusion.Screen;

import edu..android.core.entity.model.fusion.Step;
import edu..android.core.entity.model.fusion.Execution;


import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.dataformat.yaml.YAMLFactory;

/**
 * 
 * This class generates takes as input a getevent file, and generates a list of
 * tuples that contain information about each step performed on a device.
 *
 * @since Feb 1, 2015
 */
public class TraceReplayer {
	private List<Step> steps = new ArrayList<Step>(); // Holds the steps of the current execution
	private DeviceHelper deviceHelper; // Provides APIs to interface with an Android device
	private int sequence = 0;
	public boolean takeScreenshots = false;
	private int executionCtr = 1;
	private ReplayerFeatures replayerFeatures;
	private String androidSDKPath;

	public TraceReplayer() {

	}

	/**
	 * @param args
	 * @throws Exception
	 */
	public static void main(String[] args) throws Exception {
		System.out.println("Reading... " + args[1]);
		TraceReplayer tracereplayer = new TraceReplayer();
		tracereplayer.runTraceReplayer(args);
	}
	
	//Read config file
	//https://stackabuse.com/reading-and-writing-yaml-files-in-java-with-jackson/
	public static TraceReplayerPaths readConfig(String[] args) throws Exception {
		InputStream inputStream = new FileInputStream(new File(args[1]));
		
		Yaml yaml = new Yaml();
		Map<String, Object> data = yaml.load(inputStream);

		//https://stackoverflow.com/questions/16428817/convert-a-mapstring-string-to-a-pojo
		Gson gson = new Gson();
		JsonElement jsonElement = gson.toJsonTree(data);
		TraceReplayerPaths traceReplayerPaths = gson.fromJson(jsonElement, TraceReplayerPaths.class);
		return traceReplayerPaths;
	}

	public void runTraceReplayer(String[] args) throws Exception {
		TraceReplayerPaths traceReplayerConfig = readConfig(args);
		androidSDKPath = traceReplayerConfig.getAndroidSDKPath();
		String pythonScriptsPath = traceReplayerConfig.getPythonScriptsPath();
		String device = ""; // If more than one emulator

		
		String apkPath = traceReplayerConfig.getApkPath();
		String aaptPath = traceReplayerConfig.getAaptPath();
		App appInfo = generateBugRepData(apkPath, aaptPath);
		
		String appName = appInfo.getName();
		appName = appName.replace("\s", "");
		appName = appName.toLowerCase();
//		String appName = "vinyl";
		String appPackage = appInfo.getPackageName();
//		String appPackage = "com.german_software_engineers.trainerapp";
		String appVersion = appInfo.getVersion();
//		String appVersion = "0.24.1";
		String mainActivity = appInfo.getMainActivity();
//		String mainActivity = "com.german_software_engineers.trainerapp.TrainingsSchedule";
		
		String geteventFile = traceReplayerConfig.getGetEventFile();
		String outputFolder = traceReplayerConfig.getOutputFolder();

		String avdPort = traceReplayerConfig.getAvdPort();
		String adbPort = traceReplayerConfig.getAdbPort();
		executionCtr = traceReplayerConfig.getExecutionNum();
		
		String executionType = "User-Trace-";
		TypeDeviceEnum deviceType = UiAutoConnector.TypeDeviceEnum.EMULATOR;
		DeviceHelper deviceHelper = new DeviceHelper(deviceType, androidSDKPath, avdPort, adbPort);
		steps.clear();
		boolean install = true;

		boolean keyboardActive = false;
		takeScreenshots = true;
		GUIEventVO oldComponent = null;
		boolean isSearchActivity = false;

		ArrayList<Integer> screenDims = null;
		ArrayList<Integer> maxLinuxScreenDims = null;

		Execution execution = new Execution();
		App app = new App();
		app.setName(appName);
		app.setPackageName(appPackage);
		app.setMainActivity(mainActivity);
		app.setApkPath(apkPath);
		app.setVersion(appVersion);

		execution.setApp(app);
		execution.setDeviceDimensions(Utilities.getScreenSize(androidSDKPath));
		execution.setOrientation(Utilities.getOrientation(androidSDKPath));
		execution.setAndroidVersion(Utilities.getAndroidVersion(androidSDKPath));
		execution.setDeviceName(Utilities.getDeviceVersion(androidSDKPath));
		execution.setMainActivity(app.getMainActivity());
		execution.setExecutionType(executionType);

		replayerFeatures = new ReplayerFeatures();

		replayerFeatures.setWidthScreen(Integer.parseInt(execution.getDeviceDimensions().split("x")[0]));
		replayerFeatures.setHeightScreen(Integer.parseInt(execution.getDeviceDimensions().split("x")[1]));
		
//		replayerFeatures.setWidthScreen(1080);
//		replayerFeatures.setHeightScreen(1920);
		
		replayerFeatures.setUiDumpLocation(outputFolder + File.separator + app.getPackageName() + "-" + app.getVersion()
				+ "-" + executionCtr + "-" + executionType);

		// Get dimensions
		screenDims = Utilities.getScreenDimensions(androidSDKPath, device);
		System.out.println(screenDims.toString());
		maxLinuxScreenDims = Utilities.getMaxScreenAbsValues(androidSDKPath, device);
		System.out.println(maxLinuxScreenDims.toString());
		// navBarDims = Utilities.getStatusBarDimensions();

		long startTime = System.currentTimeMillis();

		new File(outputFolder + File.separator).mkdirs();
		List<GUIEventVO> events = new ArrayList<GUIEventVO>();

		System.out.println("- Setting up the app " + appName);
		if (install) {
			StepByStepEngine.unInstallAndInstallApp(androidSDKPath, apkPath, appPackage, device);
		} else {
			StepByStepEngine.clearAppData(androidSDKPath, appPackage, device);
			StepByStepEngine.installApp(androidSDKPath, apkPath, appPackage);
		}

		System.out.println("- Getting step-by-step statements for file " + geteventFile);
		ArrayList<GUIEventVO> guiEvents = StepByStepEngine.getStepByStepStatementsFromEventLog(geteventFile,
				pythonScriptsPath);

		System.out.println("- Starting step-by-step execution (" + geteventFile + ") for " + appPackage + ", using ");

		StepByStepEngine.startAPK(androidSDKPath, appPackage, mainActivity, device);
		
		try {
			Files.createDirectories(Paths.get(outputFolder + File.separator + "screenshots"));
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}

		if (takeScreenshots) {
			String screenshot = appPackage + "_" + appVersion + "_" + appName + sequence + ".png";
			Utilities.getAndPullScreenshot(androidSDKPath, outputFolder + File.separator + "screenshots",
					appPackage + "." + "User-Trace" + "." + +executionCtr + "." + screenshot);
		}

		int screenWidth = replayerFeatures.getWidthScreen();
		int screenHeight = replayerFeatures.getHeightScreen();

		int i = 0;
		int cnt1 = 0;
		GUIEventVO vo = null;
		for (GUIEventVO guiEventVO : guiEvents) {
			// updated according to
			// https://source.android.com/devices/input/touch-devices.html#touch-device-driver-requirements
			long realInitialX = Math
					.round((guiEventVO.getInitialX()) / (maxLinuxScreenDims.get(0) + 10d) * screenDims.get(0));
			long realInitialY = Math
					.round((guiEventVO.getInitialY()) / (maxLinuxScreenDims.get(1) + 10d) * screenDims.get(1));

			long realFinalX = Math
					.round((guiEventVO.getFinalX()) / (maxLinuxScreenDims.get(0) + 10d) * screenDims.get(0));
			long realFinalY = Math
					.round((guiEventVO.getFinalY()) / (maxLinuxScreenDims.get(1) + 10d) * screenDims.get(1));

			guiEventVO.setRealInitialX((int) realInitialX);
			guiEventVO.setRealInitialY((int) realInitialY);

			guiEventVO.setRealFinalX((int) realFinalX);
			guiEventVO.setRealFinalY((int) realFinalY);

			//Thread.sleep(8000);

			WindowVO window = Utilities.detectTypeofWindow(androidSDKPath, screenDims.get(0), screenDims.get(1),
					TypeDeviceEnum.EMULATOR, device, null);
			// System.out.println(window.getTitle());
			// Set the best component matching
			UiAutoConnector.getComponent(androidSDKPath, guiEventVO, screenDims.get(0), screenDims.get(1), device,
					replayerFeatures.getUiDumpLocation() + sequence, avdPort, adbPort);
			String currentWindow = ((window.getWindow()
					+ (window.getTitle() != null && !window.getTitle().isEmpty() ? window.getTitle() : ""))).trim();
			// guiEventVO.setActivity(title);
			if (guiEventVO.getEventTypeId() != StepByStepEngine.SWIPE) {
				guiEventVO.getHvInfoComponent().setTitleWindow(window.getTitle());
			}

			UiAutoConnector.setComponentAreas(guiEventVO, androidSDKPath, screenDims.get(0), screenDims.get(1));

			ArrayList<DynGuiComponentVO> screenInfo = UiAutoConnector.getScreenInfoCache(androidSDKPath, screenWidth,
					screenHeight, true, false, device);

			System.out.println(guiEventVO.getHvInfoComponent());

			Screen screen = new Screen();
			screen.setActivity(Utilities.getCurrentActivity(androidSDKPath));
			screen.setWindow(window.getWindow());
			screen.setDynGuiComponents(StepByStepEngine.getEntityFromVO(screenInfo));

			String textEntry = StepByStepEngine.executeEvent(guiEventVO, androidSDKPath, appPackage, null, false,
					device);

			System.out.println("Event # = " + cnt1);
			cnt1++;

			Thread.sleep(3000);

			// Is Keyboard component?
			if (guiEventVO.getHvInfoComponent() != null
					&& (guiEventVO.getHvInfoComponent().getIdXml().equals("id/keyboard_view")
							|| guiEventVO.getHvInfoComponent().getIdXml().endsWith("id/calculator_keyboard"))) {
				if (!keyboardActive && oldComponent != null) {
					vo = (GUIEventVO) Utilities.cloneObject(oldComponent);
					events.add(events.size(), vo);
				}
				keyboardActive = true;
			} else {
				if (keyboardActive) {
//                    ArrayList<DynGuiComponentVO> screenInfoCache = UiAutoConnector
//                            .getScreenInfoNoCache(androidSDKPath, screenDims.get(0),
//                                    screenDims.get(1), true, false);
					sequence++;
					ArrayList<DynGuiComponentVO> screenInfoEmulator = UiAutoConnector.getScreenInfoEmulator(
							androidSDKPath, screenWidth, screenHeight, true, false, false, avdPort, adbPort,
							replayerFeatures.getUiDumpLocation() + sequence);

					boolean isLoginInfo = false;
					boolean error = true; // to check if there is any error in the UI implementation
					for (DynGuiComponentVO component : screenInfoEmulator) {
						if (component != null && vo.getHvInfoComponent() != null
								&& component.getIdXml().equals(vo.getHvInfoComponent().getIdXml())
								&& component.getText().length() > 0) {

							isLoginInfo = true;
							error = false;
							vo.setHvInfoComponent(component);
							vo.setText(component.getText());

							vo.setEventLabel("CLICK_TYPE");
							vo.setEventTypeId(StepByStepEngine.CLICK_TYPE);

							Step step = StepByStepEngine.getStepFromEvent(vo);
							step.setSequenceStep(sequence);
							step.setScreen(screen);
							step.setTextEntry("none");
//							Thread.sleep(1000);

							String screenshot = appPackage + "_" + appVersion + "_" + appName + sequence + ".png";

							String currstep = Integer.toString(sequence - 1); // Here the current step is actually the
																				// current sequence minus 1

							String currscreenshot = appPackage + "_" + appVersion + "_" + appName + currstep + ".png";

							Utilities.copyFiles(replayerFeatures.getUiDumpLocation() + (sequence - 1) + ".xml",
									replayerFeatures.getUiDumpLocation() + sequence + ".xml");
							Utilities.copyFiles(
									outputFolder + File.separator + "screenshots" + File.separator + appPackage + "."
											+ "User-Trace" + "." + +executionCtr + "." + currscreenshot,
									outputFolder + File.separator + "screenshots" + File.separator + appPackage + "."
											+ "User-Trace" + "." + +executionCtr + "." + screenshot);

							takeAugmentedScreenshot(step, screenWidth, screenHeight, outputFolder, appPackage,
									currscreenshot, screenshot);

							DynGuiComponent dynGuiComponent = step.getDynGuiComponent();

							String guiScreenShot = takeGUIScreenshot(dynGuiComponent, outputFolder, appPackage,
									screenshot, screenshot);
							step.getDynGuiComponent().setGuiScreenshot(guiScreenShot);
							steps.add(step);

							i++;
							break;
						}
					}

					if (!isLoginInfo) { // for search
						for (DynGuiComponentVO component : screenInfo) {
							if (component.isFocused() || component.getIdXml().endsWith("id/search_src_text")) {
								System.out.println(component);
								if (guiEventVO.getRealInitialY() > 1128 && Utilities.isKeyboardActive(androidSDKPath)) {
									isSearchActivity = true;
								}
								error = false;
								vo.setHvInfoComponent(component);
								vo.setText(component.getText());

								vo.setEventLabel("CLICK_TYPE");
								vo.setEventTypeId(StepByStepEngine.CLICK_TYPE);

								Step step = StepByStepEngine.getStepFromEvent(vo);
								step.setSequenceStep(sequence);
								step.setScreen(screen);
								step.setTextEntry("none");
//								Thread.sleep(1000);

								String screenshot = appPackage + "_" + appVersion + "_" + appName + sequence + ".png";

								String currstep = Integer.toString(sequence - 1); // Here the current step is actually
																					// the current sequence minus 1

								String currscreenshot = appPackage + "_" + appVersion + "_" + appName + currstep
										+ ".png";

								if (isSearchActivity) {
									Utilities.getAndPullScreenshot(androidSDKPath,
											outputFolder + File.separator + "screenshots",
											appPackage + "." + "User-Trace" + "." + +executionCtr + "." + screenshot);
								} else {
									Utilities.copyFiles(replayerFeatures.getUiDumpLocation() + (sequence - 1) + ".xml",
											replayerFeatures.getUiDumpLocation() + sequence + ".xml");
									Utilities.copyFiles(
											outputFolder + File.separator + "screenshots" + File.separator + appPackage
													+ "." + "User-Trace" + "." + +executionCtr + "." + currscreenshot,
											outputFolder + File.separator + "screenshots" + File.separator + appPackage
													+ "." + "User-Trace" + "." + +executionCtr + "." + screenshot);
								}

								takeAugmentedScreenshot(step, screenWidth, screenHeight, outputFolder, appPackage,
										currscreenshot, screenshot);

								DynGuiComponent dynGuiComponent = step.getDynGuiComponent();

								String guiScreenShot = takeGUIScreenshot(dynGuiComponent, outputFolder, appPackage,
										currscreenshot, screenshot);
								step.getDynGuiComponent().setGuiScreenshot(guiScreenShot);
								steps.add(step);
							}
						}
					}

					if (error) {
						sequence--;
					}

					keyboardActive = false;
				}

			}

			// System.out.println("Step: " + (i+1));
			System.out.println("Step: " + (sequence + 1));

			// Right now we are not recording keyboard events
			if (!keyboardActive && !isSearchActivity) {
				events.add(guiEventVO);
				oldComponent = guiEventVO;

				sequence++;

				Step step = StepByStepEngine.getStepFromEvent(guiEventVO);
				step.setSequenceStep(sequence);
				step.setScreen(screen);
				step.setTextEntry(textEntry);

				if (guiEventVO.getHvInfoComponent() != null
						&& guiEventVO.getHvInfoComponent().getName().endsWith("EditText")) {
					step.setAction(StepByStepEngine.CLICK_TYPE);
				}

				if (guiEventVO.getEventTypeId() != StepByStepEngine.SWIPE) {
					step.getDynGuiComponent().setCurrentWindow(currentWindow);
				}
//				Thread.sleep(1000);

				String screenshot = appPackage + "_" + appVersion + "_" + appName + sequence + ".png";

				String currstep = Integer.toString(sequence - 1); // Here the current step is actually the current
																	// sequence minus 1

				String currscreenshot = appPackage + "_" + appVersion + "_" + appName + currstep + ".png";

				Utilities.getAndPullScreenshot(androidSDKPath, outputFolder + File.separator + "screenshots",
						appPackage + "." + "User-Trace" + "." + +executionCtr + "." + screenshot);

				if (guiEventVO.getEventTypeId() != StepByStepEngine.SWIPE) {
					takeAugmentedScreenshot(step, screenWidth, screenHeight, outputFolder, appPackage, currscreenshot,
							screenshot);
					DynGuiComponent dynGuiComponent = step.getDynGuiComponent();
					String guiScreenShot = takeGUIScreenshot(dynGuiComponent, outputFolder, appPackage, currscreenshot,
							screenshot);
					step.getDynGuiComponent().setGuiScreenshot(guiScreenShot);
				} else {
					takeAugmentedScreenshotForSwipe(step, guiEventVO, screenWidth, screenHeight, outputFolder,
							appPackage, currscreenshot, screenshot);
				}

				steps.add(step);

				i++;
			} else {
				// To capture the latest screenshot during typing
				String screenshot = appPackage + "_" + appVersion + "_" + appName + sequence + ".png";
				Utilities.getAndPullScreenshot(androidSDKPath, outputFolder + File.separator + "screenshots",
						appPackage + "." + "User-Trace" + "." + +executionCtr + "." + screenshot);
			}
			isSearchActivity = false;

		}

		UiAutoConnector.getScreenInfoEmulator(androidSDKPath, screenWidth, screenHeight, true, false, false, avdPort,
				adbPort, replayerFeatures.getUiDumpLocation() + sequence);

		System.out.println("- Final steps (pulling files from device and stopping profiler/app)");

		execution.setSteps(getSteps());
		// execution.setCrash(false);

		long endTime = System.currentTimeMillis();
		execution.setElapsedTime(endTime - startTime);
		execution.setExecutionNum(executionCtr);

		Gson gson = new Gson();
		String json = gson.toJson(execution);
		PrintWriter gsonWriter = new PrintWriter(outputFolder + File.separator + "Execution-" + executionCtr + ".json");
		gsonWriter.println(json);
//		try {
//			Thread.sleep(1000);
//		} catch (InterruptedException e) {
//			// TODO Auto-generated catch block
//			e.printStackTrace();
//		}
		gsonWriter.close();

		StepByStepEngine.stopAPK(androidSDKPath, appPackage, device);

		System.out.println("- DONE");
		System.out.println("----------------------------------------------------");

	}

	public void takeAugmentedScreenshotForSwipe(Step step, GUIEventVO guiEventVO, int screenWidth, int screenHeight,
			String outputFolder, String appPackage, String currscreenshot, String screenshot) throws Exception {
		ScreenActionData data = new ScreenActionData(step.getAction(), guiEventVO.getRealInitialX(),
				guiEventVO.getRealInitialY(), guiEventVO.getRealFinalX(), guiEventVO.getRealFinalY(), screenWidth,
				screenHeight);
		ScreenshotModifier.augmentScreenShotTraceSwipe(step,
				outputFolder + File.separator + "screenshots" + File.separator + appPackage + "." + "User-Trace" + "."
						+ +executionCtr + "." + currscreenshot,
				outputFolder + File.separator + "screenshots" + File.separator + appPackage + "." + "User-Trace" + "."
						+ +executionCtr + "." + screenshot.replace(".png", "_augmented.png"),
				data);
		step.setScreenshot(appPackage + "." + "User-Trace" + "." + +executionCtr + "."
				+ screenshot.replace(".png", "_augmented.png"));
	}

	public void takeAugmentedScreenshot(Step step, int screenWidth, int screenHeight, String outputFolder,
			String appPackage, String currscreenshot, String screenshot) throws Exception {
		if (step != null) {
			ScreenActionData data = null;
			System.out.println("Augmenting the Previous Step # " + sequence + " Screenshot");
			// System.out.println("--- Augmenting " + currscreenshot); //For debugging
			if (step.getDynGuiComponent() != null) {
				data = new ScreenActionData(step.getAction(),
						(step.getDynGuiComponent().getWidth() / 2) + step.getDynGuiComponent().getPositionX(),
						(step.getDynGuiComponent().getHeight() / 2) + step.getDynGuiComponent().getPositionY(),
						screenWidth, screenHeight);

				ScreenshotModifier.augmentScreenShot(
						outputFolder + File.separator + "screenshots" + File.separator + appPackage + "." + "User-Trace"
								+ "." + +executionCtr + "." + currscreenshot,
						outputFolder + File.separator + "screenshots" + File.separator + appPackage + "." + "User-Trace"
								+ "." + +executionCtr + "." + screenshot.replace(".png", "_augmented.png"),
						data);
				step.setScreenshot(appPackage + "." + "User-Trace" + "." + +executionCtr + "."
						+ screenshot.replace(".png", "_augmented.png"));
			} else {
				step.setScreenshot(appPackage + "." + "User-Trace" + "." + +executionCtr + "." + screenshot);
			}
		}
	}

	public String takeGUIScreenshot(DynGuiComponent dynGuiComponent, String outputFolder, String appPackage,
			String currscreenshot, String screenshot) {
		String guiScreenShot = null;

		if (dynGuiComponent != null) {
			ScreenActionData data = null;
			Image orig = null;
			boolean ok = false;
			do {
				try {
					// https://stackoverflow.com/questions/13796611/imageio-read-with-mac
					orig = ImageIO.read(new File(outputFolder + File.separator + "screenshots" + File.separator
							+ appPackage + "." + "User-Trace" + "." + +executionCtr + "." + currscreenshot));
					ok = true;
				} catch (IOException e) {
					ok = false;
					e.printStackTrace();
				}
			} while (!ok);

			int x = dynGuiComponent.getPositionX();
			int y = dynGuiComponent.getPositionY();
			int w = dynGuiComponent.getWidth();
			int h = dynGuiComponent.getHeight();

			if (dynGuiComponent.getIdXml().equals("BACK_MODAL")) {
				x = 0;
				y = 1794;
				w = 400;
				h = 126;
			}

			BufferedImage bi = new BufferedImage(w, h, BufferedImage.TYPE_INT_ARGB);
			bi.getGraphics().drawImage(orig, 0, 0, w, h, x, y, x + w, y + h, null);

			try {
				ImageIO.write(bi, "png",
						new File(outputFolder + File.separator + "screenshots" + File.separator + appPackage + "."
								+ "User-Trace" + "." + +executionCtr + "."
								+ screenshot.replaceAll(".png", "_gui.png")));
			} catch (IOException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}

			guiScreenShot = appPackage + "." + "User-Trace" + "." + +executionCtr + "."
					+ screenshot.replaceAll(".png", "_gui.png");

		}
		return guiScreenShot;

	}

	/**
	 * @return the steps
	 */
	public List<Step> getSteps() {
		return steps;
	}

	/**
	 * @param steps the steps to set
	 */
	public void setSteps(List<Step> steps) {
		this.steps = steps;
	}
	
	public static App generateBugRepData(String appFile, String pathToAAPT) {
		// Create a list of apps

		String aaptCommand = "";
		String appInfo = "";
		String appName = "";
		String appPackageName = "";
		String appMainActivity = "";
		String appVersion = "";

		ArrayList<App> bugRepApps = new ArrayList<App>();
		App app = new App();

		String currFile = appFile;

		System.out.println("Current File: " + currFile);
		System.out.println();

		// Get the application info from aapt
		aaptCommand = pathToAAPT + File.separator + "aapt dump badging " + currFile;
		appInfo = TerminalHelper.executeCommand(aaptCommand);
		System.out.println(appInfo);
		// Parse the application
		appPackageName = appInfo.substring(appInfo.indexOf("name=") + 6, appInfo.indexOf("versionCode") - 2);
		System.out.println("Package Name: " + appPackageName);
		appName = appInfo.substring(appInfo.indexOf("application: label='") + 20, appInfo.indexOf("icon=") - 2);
		System.out.println("App Name: " + appName);
		appMainActivity = appInfo.substring(appInfo.indexOf("launchable-activity: name='") + 27);
		appMainActivity = appMainActivity.substring(0, appMainActivity.indexOf(' ') - 1);
		System.out.println("App Main Activity: " + appMainActivity);
		appVersion = appInfo.substring(appInfo.indexOf("versionName='") + 13);
		//appVersion = appVersion.substring(0, appVersion.indexOf(' ') - 1);
		appVersion = appVersion.substring(0, appVersion.indexOf("'"));
//		appVersion = "01.19";
		System.out.println("App Version: " + appVersion);
		System.out.println();

		app = new App();
		app.setName(appName);
		app.setPackageName(appPackageName);
		app.setMainActivity(appMainActivity);
		app.setVersion(appVersion);
		app.setApkPath(currFile);

		return app;
	}

}

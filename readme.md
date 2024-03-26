# EP-Detector: Automatic Detection of Error-prone Operation Anomalies in Android Applications

## Table of Contents

- [EP-Detector: Automatic Detection of Error-prone Operation Anomalies in Android Applications](#ep-detector-automatic-detection-of-error-prone-operation-anomalies-in-android-applications)
  - [Table of Contents](#table-of-contents)
  - [Error-prone Operation Anomaly(EPA)](#error-prone-operation-anomalyepa)
    - [EPA](#epa)
    - [Motivating Examples](#motivating-examples)
  - [Approach](#approach)
    - [Two-stage Navigation](#two-stage-navigation)
    - [Target Identification](#target-identification)
    - [Detection Execution](#detection-execution)
    - [Test Oracle](#test-oracle)
  - [Getting Started](#getting-started)
    - [Environment](#environment)
    - [Installation](#installation)
      - [1. Installing Appium (Version 1.22.3)](#1-installing-appium-version-1223)
      - [2. Setting Up ADB](#2-setting-up-adb)
      - [3. Cloning the GitHub Project](#3-cloning-the-github-project)
      - [4. Extending the appium-python-client](#4-extending-the-appium-python-client)
    - [Seamless Deployment](#seamless-deployment)
      - [1. Enabling USB Debugging on Android Device](#1-enabling-usb-debugging-on-android-device)
      - [2. Connecting the Android Device to Your Host via USB Cable](#2-connecting-the-android-device-to-your-host-via-usb-cable)
      - [3. Fine-Tuning Android Device Parameters](#3-fine-tuning-android-device-parameters)
      - [4.Initiating the Appium Service](#4initiating-the-appium-service)
    - [Usage](#usage)
  - [Result](#result)


## Error-prone Operation Anomaly(EPA)
### EPA
Error-prone Operation Anomaly (EPA) is a critical aspect in the design and interaction of Graphical User Interfaces (GUI) within Android applications. It refers to the propensity for misoperations caused by elements of the interface that are prone to errors, known as Error-prone GUI Elements (EPE). These anomalies are not mere trivialities but have profound implications for the functionality and user experience of an application.

As applications become more complex to meet the diverse and intricate demands of users, the likelihood of EPA occurrences has increased. For instance, Android's introduction of optional gesture systems since version 10.0, replacing traditional buttons with swipe gestures, has complicated user interactions. Such complexities can lead ordinary users to perform incorrect operations, often resulting from an unreasonable design of page elements.

The ramifications of EPAs are multifaceted and detrimental. Misoperations can lead to system freezes, crashes, and even security vulnerabilities. Furthermore, they can severely degrade the user experience, causing frustration and distrust in the application. The problem is exacerbated in mobile environments, where constraints such as limited screen size, CPU, RAM, and network resources increase the risk of misoperations.

Despite the glaring need to address this issue, there remains a lack of systematic study and precise detection of EPAs. The detection is especially challenging as EPAs can have diverse manifestations, and triggering them consistently is a complex task.

### Motivating Examples

This section motives our research with three error-prone user
events that occur in the same Android app. Figure 1 shows the
GUI of a well-known Chinese banking Android app, and illustrates
three irreversible error operations as follows.
![](./Figures/motivating.svg)
EPA 1: When a user opens the app, she will be directed to the home page. As shown in the figure above (a), an advertisement dialog pops up on top of the actual home page. If the user wants to close the advertisement and visit the home page, she may find that the closing button is small and somewhat hidden (as shown in (a)-○1 in the figure above). This can result in accidentally pressing the wrong area, which redirects the user to the advertisement page instead.

EPA 2: When the user visits the main operation page and wants to use the three-finger swipe for screenshot provided by the Huawei Harmony to save the key page information (as shown in (b)-○1 in the figure above), the system may wrongly recognize it as a click due to the excessive force of the first finger. The click may lead to the bank scan function ((b)-○2 in the figure above), and the app navigates to the scan page. If it happens that a payment QR code appears in front of the camera ((b)-○4 in the figure above), the app will be redirected to the payment transfer page.

EPA 3: The user intends to visit the "My Payment" page (as shown in (c)-○1 in the figure above) to set the payment limit. However, if the page loading is stuck due to, for example, network delay, the user may assume it’s her operation fault and repeatedly click on the screen ((c)-○2 in the figure above). When the “My Payment” page eventually loads, these additional clicks may inadvertently trigger actions if there are buttons placed in the same position on the “My Payment” page, e.g., the payment scan button (as shown in (c)-○3 in the figure above). As a result, these unintended clicks lead the app to the payment scan and subsequently to the payment transfer page if a payment QR code is detected in front of the camera.

## Approach
Given an app under test, the EP-Detector detects the EPAs for each widget through the following three modules, as shown in Figure below. The Target Navigation module navigates to the target pages and widgets relying on the page & widget identification. To reduce cost, the Event Trace during the navigation is logged in the Recorder to guide new navigation. The target pages and widgets are then fed into the Detection Execution module for the detection of three typical types of EPAs. Finally, the Test Oracle module has an automated oracle to compute the Diff function . for the EPAs. In this process, both the change of environment 𝐸𝑛𝑣𝑠𝑖𝑚 and page similarity P𝑠𝑖𝑚 before and after user events are computed, where the system environment is collected by the Resource Monitor, and the $P_{𝑠𝑖𝑚}$ is used to determine whether a target page is obtained in Target Navigation and Detection Execution.

![workflow](./Figures/workflow.png)

### Two-stage Navigation
To identify and locate widgets with error-prone operations (e.g., buttons, text editors, sliders), the EP-Detector adopts a widget-exploration approach, deviating from the commonly used path-exploration approach in the majority of existing model-based GUI testing. In this process, the Target Navigation module incorporates a two-stage navigation.
-  1: Page Navigation :Simulate user actions according to the Recorder until reaching the target test page.
-  2: Widget Navigation：Navigate to the target widget on the given page, in order to test this widget.

### Target Identification
In traditional model-based dynamic testing, page or state recognition relies on absolute matching, where specific encoding techniques abstract the properties of a page, followed by the identification of the page through matching these abstract results. However, in real-world applications, this method of absolute matching often fails due to the potential changes in page content caused by updates to dynamic elements such as advertisements and random animations. To address this issue, the concept of page similarity based on Jaccard distance has been proposed, which evaluates the similarity of two pages by calculating the ratio of the intersection to the union of their property sets. If the similarity exceeds a predefined threshold, the pages are considered to be the same. This relative matching approach is utilized during page navigation and test assertion phases to enhance navigation accuracy and to determine the execution path breakpoints in test assertions, and in the execution phase for state abstraction and clustering of page states. Additionally, the similarity calculation also considers environmental factors such as CPU, RAM, and network conditions to further optimize the accuracy and efficiency of testing.

### Detection Execution

EPAs  can be categorized into three types: confusing behaviors (bEPAs), unsuitable layout (aEPAs), and extreme resources (eEPAs). The section on confusing behaviors focuses on the complex interactions users have with widgets, especially those that may be disrupted by natural factors such as voice control and phone shaking. To address this challenge, the research shifts its emphasis towards user gesture events, summarizing user behaviors through the analysis of gesture-related classes in Android. Strategies are employed to filter out redundant and non-critical behaviors, ultimately identifying 12 typical user interactions. These behaviors are divided into three groups based on their confusion potential: click, long click, and scroll, with each group's confusion degree defined by variations in the number of operations, number of fingers used, operation distance, and duration.

Additionally, the unsuitable layout section discusses EPAs arising from improper widget design, with a focus on layout-related factors such as size and spacing, and defines conditions for unsuitable layouts. The extreme resources section examines EPAs caused by insufficient device resources, such as CPU, RAM, and network capacity, particularly under conditions of resource overload that may lead to execution anomalies like page freezing and operation failures, potentially resulting in user errors.

For these two types of EPAs, a dynamic analysis approach is proposed for detection, which includes simulating user interactions and recording the outcomes to identify bEPAs, and dynamically simulating operations to detect EPAs caused by unsuitable layouts and resource overloads.
###  Test Oracle

EP-Detector is an automated testing tool that employs various strategies to compute the Diff function to detect three types of execution path anomalies (EPAs): confusing behaviors (bEPA), unsuitable layouts (aEPA), and extreme resources (eEPA). For bEPAs, EP-Detector checks if the new page triggered by confusing behaviors differs from the original page or the page triggered by the base behavior; if so, a bEPA is identified. The detection of aEPAs is based on the principle that two identical operations performed within the safe area should yield the same outcomes, otherwise, anomalies may arise. The detection of eEPAs is two-fold: it checks whether the environmental change following continuous and repeated operations falls below a certain threshold, and whether unintended misoperations occur after a page jump. Additionally, EP-Detector dynamically determines the α and β parameters used to compute the Diff function, based on the calculated results of page similarity (Psim) and environmental similarity (Envsim).

## Getting Started

### Environment
- Operating System: Windows 10/11
- Android Device Version: Android 10~13
- Appium Version: v1.22.3 (See [Appium Installation Guide](http://appium.io/docs/en/2.0/))
- Android Debug Bridge (ADB) Version: 1.0.41
- Python Version: 3.8
### Installation
#### 1. Installing Appium (Version 1.22.3)

Find the complete guide to installing Appium [here](http://appium.io/docs/en/2.0/quickstart/install/).
#### 2. Setting Up ADB
ADB can be smoothly installed using either Google's standalone platform-tools or via Android Studio. Find the full instructions [here](https://source.android.google.cn/docs/setup/build/adb).
#### 3. Cloning the GitHub Project
Start by cloning the Python version of EP-Detector from GitHub using the following command:
```shell
git clone https://github.com/WordDealer/EP-Detector

```
We recommend using a Python 3.8 virtual environment to run the code, especially since the appium-python-client's source code will be custom modified for simulating user actions. Below are the essential Python packages required:

| Python Package     | Version |
|--------------------|---------|
| appium-python-client | 2.1.0   |
| numpy               | 1.23.5  |
| urllib3             | 1.26.15 |
| opencv-python       | 4.5.4.60|

A suggested practice is to use a conda virtual environment with the following steps:

```shell
conda create --name EPDetector python=3.8
conda activate EPDetector
conda install -c conda-forge appium-python-client==2.1.0
conda install -c conda-forge numpy==1.23.5
conda install -c conda-forge urllib3==1.26.15
conda install -c conda-forge opencv-python==4.5.4.60
```
#### 4. Extending the appium-python-client
To create a customized user experience, replace the existing `action_helpers.py` file with a newly modified version, [here](http://github.com/EP-Detector/EP-Detector/Appium_externed/action_helpers.py). The path is conveniently located at `python-client/appium/webdriver/extensions/`(Subordinate Directories within a Conda Virtual Environment or Python Environment).
### Seamless Deployment
#### 1. Enabling USB Debugging on Android Device
As an example, for OPPO Reno 5K, Android 13, you should enable these options:

- Developer Options
- Screen Stays Awake While Charging
- USB Debugging

And disable:

- Permission Monitoring

#### 2. Connecting the Android Device to Your Host via USB Cable
Once the environment is configured, connect the Android device to the host with a USB cable and use the command `adb devices` to list all connected devices and emulators.
```shell
$ adb devices  
List of devices attached  
3102847529001WC device
```
#### 3. Fine-Tuning Android Device Parameters
You'll need to modify the Main.py and MainForEnv.py files to change the device name and Android version to match your specific hardware.
```python
    desc['deviceName']='127.0.0.1:3102847529001WC'
    desc['platformVersion']='13'
```
#### 4.Initiating the Appium Service
You can easily start the Appium service with this simple command:
```
$ appium
[Appium] Welcome to Appium v1.22.3
[Appium] Appium REST http interface listener started on 0.0.0.0:4723
```
### Usage
Before diving into EP-Detector, ensure that every single step in the Installation and Deployment phases has been carefully followed.

Within the project, you'll find two main scripts that act as gateways for detecting aEPAs, bEPAs, and eEPAs. They function as follows:
| Script          | Description                               |
|-----------------|-------------------------------------------|
| Main.py         | Guides the detection of aEPAs and bEPAs.  |
| MainForEnvs.py  | Focused on eEPAs detection.               |

For detecting aEPAs and bEPAs, execute:
```shell
cd EP-Detector
conda activate EPDetector
python Main.py
```
For detecting eEPAs, follow:
```shell
cd EP-Detector
conda activate EPDetector
python MainForEnvs.py
```
## Result
The [dataset](./Data/Dataset/), [results](./Data/Result/), and [manually annotated results](./Data/Manual_Result/) for EP-Detector can be found here.
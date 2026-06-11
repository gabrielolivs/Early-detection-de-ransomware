# Early detection de ransomware

## Starting 

The Figure illustrates the experimentation scenario, which involves uploading binaries (binary.exe) to the tool and creating virtual machines through the VirtualBox software. The tool has an agent, created in Python, which monitors and captures all content and changes made by the binary during its execution. The tool in question is installed on a Dell Inspiron 15 3000 computer with Ubuntu 18.04 operating system.

![cuckoo drawio (2)](https://user-images.githubusercontent.com/51774020/222503136-20e0b5c2-c32f-42ee-bb48-5cfd0ae124e4.png)


Finally, the Jupyterlab development environment with the Python language was used to process the report resulting from the Cuckoo analysis. Such a report is generated in JavaScript Object Notation (JSON) format. From this file, 170 features were selected, such as system calls and operations performed by each executed binary. In this way, it was possible to build a dataset with malicious and legitimate samples (typical applications for common users).

In order to process the report resulting from the Cuckoo analysis, a script in the Python language called script.py was implemented, which is available in the aforementioned repository. Such a report, which is illustrated in the Figure, is generated in JavaScript Object Notation (JSON) format. From this file, 226 features were selected for WannaCry, 211 for Ryuk and also 211 CryptoLock, such as system calls and operations performed by each executed binary. In this way, it was possible to build 3 datasets with malicious (WannaCry, Ryuk, CryptoLocker) and legitimate samples (typical applications for common users). It is important to highlight that each generated dataset contains samples related to 35 legitimate binaries and 1 malicious binary. Therefore, what changes from one dataset to another are the malicious binary samples. That is, each dataset has samples of only one of the malicious binaries, in addition to samples relating to 35 legitimate binaries, which are the same for each database.

## Prerequisites

To run the created script, it is recommended to install the [Anaconda](https://www.anaconda.com/products/distribution) software and that the machine you are using has at least 8GB of RAM memory.

## Settings
First, you need to download the entire repository onto your machine.

Follow the steps shown below:

1 - On Windows, we will enter the repository in question, go to '<> code' and download the ZIP:
![githubcerto1](https://user-images.githubusercontent.com/51774020/222516384-c7829379-c5a8-4367-b400-dee54f5e7976.gif)

2 - In the location you want, we will extract all the files.
![image](https://user-images.githubusercontent.com/51774020/222519289-ab2eb524-e8a6-430f-a43a-77a1b9767e79.png)

When running the recommended software, we will use JupyterLab to execute and visualize our features. (Image illustrated below)
![githubgif](https://user-images.githubusercontent.com/51774020/222509797-9426c199-a253-4c82-8728-6cc57d2db0bb.gif)

![githubcerto3](https://user-images.githubusercontent.com/51774020/222519569-24796901-5d5a-442a-84b0-c05e6dc06264.gif)

Now, it is necessary to download the reports referring to the non-malicious binaries, which are available at the url below. GitHub has a file size limiter, so it's included in Google Drive:

[Clique aqui](https://drive.google.com/drive/folders/1LcO4pn-Op9xZvBIw7NUQFFybP99dZ58B?usp=share_link) e baixe os reports.
![githubcerto4](https://user-images.githubusercontent.com/51774020/222520921-9c5a89bd-36e7-454d-8b66-b25ec0f21215.gif)

![image](https://user-images.githubusercontent.com/51774020/222522272-6ad38570-3650-419b-889c-411bff79a8bd.png)

## Running

In JupyterLab, we will start executing the stript in question. in the 'main()' function, it is necessary for the reader to insert the location of the file in the folder where the JSON files are.

![image](https://user-images.githubusercontent.com/51774020/222523108-1651262c-6f2a-4909-839e-e5d1b59b0734.png)

Also change the name which will be the name of the referring CSV file

![image](https://user-images.githubusercontent.com/51774020/222524473-0061e80d-c54d-4006-9a76-87875eb9baa7.png)

Right after all the configuration, it's time to run. Just press CTRL+ENTER. The code will be in operation, and soon after, two result files will be created:

![image](https://user-images.githubusercontent.com/51774020/222534243-355ba71c-1c59-4e4b-8046-953440fbbfe5.png)

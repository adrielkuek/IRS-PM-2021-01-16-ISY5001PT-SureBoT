# IRS-PM-2021-01-16-ISY5001PT-SureBoT

## SECTION 1: PROJECT TITLE

## SureBoT - An automated end-to-end fact-checking Telegram chatbot

![surebot](https://user-images.githubusercontent.com/67159970/114734523-dfb7d280-9d76-11eb-9d84-a029fa6a5a29.gif)

## SECTION 2: EXECUTIVE SUMMARY / PAPER ABSTRACT

With the rapid advancement in technology and the push for digitalisation around the globe, news media outlets have gradually moved away from traditional print media to digital online news offerings. People can now get access to live news updates with just a simple click on their smart devices such as handphones or tablets. However, within the massive amount information on the Internet, not only are there genuine news, but there also exist a sizeable amount of fake news or misinformation shared for the purpose of deceiving and misguidance. When individuals cannot distinguish between genuine and fake news, there will be widespread sharing and spreading of false information due to its virality nature. This, unfortunately, can lead to major repercussions in a country’s economic, political and social areas.

Currently, to verify news of doubtful content, one must follow a series of steps to gather information online with authentic sources such as Factcheck.org and gov.sg/Factually, or news media providers such as The Straits Times (ST) and Channel News Asia (CNA). During information gathering, one would need to read and understand the article-in-context. In addition, there may also be the need to cross-reference to multiple sources to reach a decision. Such a verification process will take considerable time and not many people may be apprised of such methodology, especially the elderly and those who are not technology-savvy.

Our team of four would like to resolve this global issue by creating an intelligent chatbot to provide an end-to-end automated fact-checking tool. We established the chatbot on a common and popular messaging platform like Telegram to increase the accessibility to the masses. The beauty of the chatbot lies in its simplicity, ease-of-use and 24/7 availability. One only needs to input a claim to fact-check and the chatbot takes care of everything else. This minimalistic approach ensures that even the elderly will be able to use it as well.

By adopting the techniques acquired during the course, we designed the chatbot based on a cognitive framework that takes in a user input, applies feature extraction and knowledge reasoning techniques to produce a classification output that decides whether the supporting evidence “SUPPORTS” or “REFUTES” the input claim.

We believe that this chatbot has great value, as the shift towards digital news consumption through online will only increase exponentially. The chances of a person intentionally or unintentionally proliferating misinformation will only become higher. Through this project, we aim to provide to the masses a tool to combat the rise of fake news and improve digital literacy. That, in turn, can further reduce or eliminate negative societal impacts such as radicalisation, religious or racial discord.


## SECTION 3: CREDITS / PROJECT CONTRIBUTION

| Official Full Name | Student ID (MTech Applicable) | Work Items (Who Did What) | Email (Optional)
| ---- | ---- | ---- | ---- |
| KUEK YONG JIE ADRIEL  | A0229985H | 1. Market Research <br /> 2. System Architecture Design <br /> 3. Implementation of Model Pipeline <br /> 4. Video Creation <br /> 5. Project Report Writing | e0687393@u.nus.edu |
| CHUA HAO ZI | A0229960W | 1. Market Research <br /> 2. Implementation of Model Pipeline <br /> 3. Video Creation <br /> 4. Project Report Writing  | e0687368@u.nus.edu |
| M. LAVANYA  | A0229979B | 1. Market Research <br /> 2. Backend Development (Google Cloud & Telegram) <br /> 3. Implementation of Model Pipeline <br /> 4. Project Report Writing | e0687387@u.nus.edu |
| Chammanikodathu Louis Francis | A0079985B | 1. Market Research <br /> 2. Project Proposal | e0689729@u.nus.edu |


## SECTION 4: MARKETING VIDEO
[![Watch the video](https://img.youtube.com/vi/fJNA814xZsY/0.jpg)](https://youtu.be/fJNA814xZsY)

## SECTION 5: USER GUIDE

### Installation
Reccomend to use python 3.7 or higher. Requires Pytorch and Transformers from Huggingface

**Step 1: Get the repository**

Using `git clone`
```
git clone https://github.com/adrielkuek/IRS-PM-2021-01-16-ISY5001PT-SureBoT
```
**Step 2: Create a Conda Environment**

Create a new environment to sandbox your developmental workspace
```
conda create -n "YOUR_ENV_NAME" python=3.7
```
**Step 3: Install dependencies**

Enter folder using `cd` and install requirements using `pip`
```
cd Code
pip install -r requirements.txt
```
**Step 4: Download the Models**

**Download pretrained models**: https://drive.google.com/uc?id=1jxUd27-K51AkRX20yEHtban8Uvab7lkX

Unzip the file inside the directory **IRS-PM-2021-01-16-ISY5001PT-SureBoT/Code**

Alternatively you can run the script **DownloadModels.py** to download and unzip the models. Please replace **<MODEL-DOWNLOAD-URL>** with the above link in the script.

The folder structure will look like this:
```
pipeline_models/pretrained_models/BERT-Pair/
    	pytorch_model.bin
    	vocab.txt
    	bert_config.json
    	
pipeline_models/models/bart-large-cnn
	msmarco-distilroberta-base-v2
	pegasus-cnn_dailymail
	stsb-distilbert-base
	1layerbest.pth
	2layerbest.pth
	3layerbest.pth
	4layerbest.pth
```
**Step 5: Download Spacy Model**

Download ``en_core_web_sm`` via the following command
```
python -m spacy download en_core_web_sm
```
### Usage
We provide 3 methods to implement the system architecture: Command-Line Interface, Localhost Server Bot & Telegram Bot Deployment on GCE


**For details for Localhost and GCE deployment, please refer to Report Appendix for step-by-step guide to setup**

For Command-Line Interface: Quick way to test out fact-checking functionality:

**Step 1: Run**
```
python SureBoT_main.py
```
**Step 2: Input Query Claim**
```
SureBoT: Input a claim that you would like to fact-check!
```
**Step 3: Enter and Process Claim**

## SECTION 6: SYSTEM EXPLAINER VIDEO
[![Watch the video](https://img.youtube.com/vi/5dgpMpF1qrY/0.jpg)](https://youtu.be/5dgpMpF1qrY)

## SECTION 7: PROJECT REPORT / PAPER

`Refer to project report at Github Folder: Project_Report`

- Executive Summary
- Problem Description & Background
- Project Objective
- Proposed Measurement Metrics
- System Overview
- Knowledge Modelling & Representation
- System Architecture
- System Implementation
- Assumptions
- System Performance
- Limitations & Improvements
- Conclusions
- Appendix of report: Project Proposal
- Appendix of report: Installation & User Guide
- Appendix of report: 1-2 pages individual project report per project member
- Appendix of report: Mapped System Functionalities against knowledge, techniques and skills of modular courses
- Appendix of report: Performance Survey

**This [Machine Reasoning (MR)](https://www.iss.nus.edu.sg/executive-education/course-exams-finder/course-finder) course is part of the Analytics and Intelligent Systems and [Graduate Certificate in Intelligent Reasoning Systems (IRS)](https://www.iss.nus.edu.sg/stackable-certificate-programmes/intelligent-systems) series offered by [NUS-ISS](https://www.iss.nus.edu.sg/).**

**Lecturer: [GU Zhan (Sam)](https://www.iss.nus.edu.sg/about-us/staff/detail/201/GU%20Zhan)**

> **zhan.gu@nus.edu.sg**

=======


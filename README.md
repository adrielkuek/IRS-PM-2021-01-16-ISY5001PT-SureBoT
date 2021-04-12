# SECTION 1: PROJECT TITLE

# Fact-Check Bot: Sure_BoT

![image](https://user-images.githubusercontent.com/67159970/114393719-ee628600-9bcc-11eb-9266-472a2d3041da.png)


# SECTION 2: EXECUTIVE SUMMARY / PAPER ABSTRACT

With the rapid technological development happening around the globe, news media has gradually moved away from print media like newspaper to online media. People can get access to live news updates with just a simple click on their smart devices like handphones or tablets. In such a huge database of news within the Internet, not only are there genuine news, there are also fake news or misinformation which are shared by people with ulterior motives. When individuals cannot distinguish genuine news from fake news, believing and spreading of such fake news can lead to major repercussions in economic, political and social areas.

Currently, to verify these news of dubious contents, the reader has to check online with authentic sources like Factcheck.org or Factually (Singapore context). And the reader may need to fact-check with more than one data source to verify the authenticity of the news. Such verification will take quite some time and not many people will know how to do this check, especially the elderly and those who are not savvy with technology.

Our team of four would like to resolve this global issue by creating a chatbot on social media which can do the fact-check on behalf of the human users. By deploying the chatbot on the common social media platform like Telegram or Whatsapp, we can greatly increase the accessibility of the chatbot to the masses. And the simplicity of the bot (i.e. one just needs to input the claim and the chatbot will do the rest) ensures that even elderly can use it.

By adopting the techniques learnt in the course, we designed the chatbot such that it can take the input (statement or article URL link) and summarize the contents. Based on the summarized inputs, it will search online from authentic sources and extract a list of relevant articles, using similarity reasoning. It will then process through these articles and output scores that will either support or refute the claims. 

We believe that this chatbot has great value, as the masses are mostly turning to popular online medias like Facebook or Google for local news and news updates, which heightened the chance of the proliferation of fake news or misinformation. Through this chatbot, the masses can easily do their fact-check and receive authentic knowledge. That, in turn, can reduce or eliminate negative impacts like radicalization, religious and racial hatred.





















=======================================================================================================================
# FactCheck_SureBo-T
In fulfillment for Practice Module for Intelligent Reasoning Systems Graduate Certificate (AY2021-SEM2)
(NUS-Institute of System Sciences)

Creating an automated end-to-end fact checking and verification Bot using Telegram BOT API for timely intervention against mis/disinformation in Singapore.

The fact checking pipeline employs multiple NLP modules that aims to determine the context of the input query in relation to news articles presented as evidences which are intelligently scrapped from the internet. The core of the reasoning system is a fully connected graph network for evidence reasoning and aggregation, together with an automated framework for online evidence mining and ranking.

## Video Introductions
** TO INPUT VIDEO LINK HERE **

## Installation
Reccomend to use python 3.7 or higher. Requires Pytorch and Transformers from Huggingface

**Step 1: Get the repository**

Using `git clone`
```
git clone https://github.com/adrielkuek/SureBo_T
```
**Step 2: Create a Conda Environment**

Create a new environment to sandbox your developmental workspace
```
conda create -n "YOUR_ENV_NAME" python=3.7
```
**Step 3: Install dependencies**

Enter folder using `cd` and install requirements using `pip`
```
cd
pip install -r requirements.txt
```
**Step 4: Download the Models**

**Download BERT pretrained**: https://drive.google.com/drive/folders/10pCx4-IYxctOtrAJjBPDZ7kum87FoqjM?usp=sharing

**Download models**: https://drive.google.com/drive/folders/1EL90Wm1W5HW2jSLxQ8nSlDRBHwLQRTHj?usp=sharing

Place the folders ``models/`` and ``pretrained_models/`` into the code working directory

The folders will look like this:
```
pretrained_models/BERT-Pair/
    	pytorch_model.bin
    	vocab.txt
    	bert_config.json
    	
models/bart-large-cnn
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

## Getting Started
**Step 1: Input the query**

Create a sample input query to test pipeline in side SureBoT_main.py
```
query = "A bus driver has been arrested for careless driving following an accident at Loyang Avenue that killed a 31-year-old cyclist."
```
**Step 2: Run the test code**

Run the SureBoT_main.py
```
python SureBoT_main.py
```
## Reports


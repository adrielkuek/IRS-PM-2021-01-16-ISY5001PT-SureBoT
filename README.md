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


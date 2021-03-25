# FactCheck_SureBo-T
Practice Module for MTech_IS Intelligent Reasoning Course (AY2021-SEM2)

Creating an automated FactCheck Bot using Telegram BOT API for timely intervention against mis/disinformation in Singapore

Commit: 22/02/21, 9:46pm
First commit to test BERT's pipeline architecture with zero-shot-classification
Commit: 25/03/21, 16:51pm
End to end integration with Evidence Retrieval and GraphNet

## Installation
Reccomend to use python 3.7 or higher. Requires Pytorch and Transformers from Huggingface

**Step 1: Get the repository**

Using `git clone`
```
git clone https://github.com/adrielkuek/FactCheck_SureBo-T
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

Download BERT pretrained: https://drive.google.com/drive/folders/10pCx4-IYxctOtrAJjBPDZ7kum87FoqjM?usp=sharing
Download models: https://drive.google.com/drive/folders/1EL90Wm1W5HW2jSLxQ8nSlDRBHwLQRTHj?usp=sharing
Place the folders models/ and pretrained_models/ into the code working directory

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



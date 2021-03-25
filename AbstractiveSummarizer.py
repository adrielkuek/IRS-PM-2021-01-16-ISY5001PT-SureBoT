"""
Author: Adriel Kuek
Date Created: 19 March 2021
Version:
Email: adrielkuek@gmail.com
Status: Devlopment

Description:
The Pegasus model was proposed in PEGASUS: Pre-training with Extracted Gap-sentences 
for Abstractive Summarization by Jingqing Zhang, Yao Zhao, Mohammad Saleh 
and Peter J. Liu on Dec 18, 2019.

According to the abstract,
Pegasus’ pretraining task is intentionally similar to summarization: 
important sentences are removed/masked from an input document and are generated 
together as one output sequence from the remaining sentences, similar to an 
extractive summary.

Pegasus achieves SOTA summarization performance on all 12 downstream tasks, 
as measured by ROUGE and human eval.

-Each checkpoint is 2.2 GB on disk and 568M parameters.
-Summarizing xsum in fp32 takes about 400ms/sample, 
with default parameters on a v100 GPU.
"""

from transformers import PegasusForConditionalGeneration, PegasusTokenizer
from transformers import BartTokenizer, BartForConditionalGeneration
import torch
import time

# src_text = ['''No health care workers died after Alabama 
# began administering COVID-19 vaccines to them on Tuesday. 
# Yet posts online began falsely claiming that a nurse had 
# died after receiving the vaccine. The posts circulated on 
# Facebook and Twitter, with some users suggesting it was 
# their aunt who had died or they had received the information 
# from a close friend. Social media users shared screenshots of 
# text messages that said, “omg just found out my aunt dead,” 
# and also said that the woman’s family did not want her name 
# revealed. Some online posts suggested a nurse who died of 
# COVID-19 had instead died after receiving the vaccine. The 
# posts were shared by accounts that had previously shared 
# anti-vaccine misinformation. “And so it starts... A 42 y/o 
# nurse in Alabama found dead 8-10 hours after the vaccine,” 
# one post on Facebook said. After being contacted by the AP, 
# Alabama Department of Public Health officials checked with 
# the hospitals that administered the COVID-19 vaccine to 
# confirm that the information being shared online was false. 
# The department released a statement on social media to 
# combat the misinformation. “The posts are untrue,” the 
# department said. “No persons who received a COVID-19 vaccine 
# in Alabama have died.” The posts online claimed that the 
# nurse had died from a severe allergic reaction known as 
# anaphylaxis. Those with a history of allergic reactions 
# are being told to not get the vaccine after two health 
# care workers in England suffered reactions. Those two people 
# have since recovered. Pfizer, whose vaccine was granted 
# emergency use authorization by the U.S. Food and Drug 
# Administration on Dec. 11, has reported no serious adverse 
# effects from its clinical trials. The AP reported Tuesday 
# that Alabama received nearly 41,000 doses of the Pfizer and 
# BioNTech vaccine in its initial round of shipments, which 
# were delivered to 15 hospitals that could store that vaccine 
# at the necessary temperature. More than 4,254 people have 
# died from the virus in the state, and more than 305,640 have 
# tested positive for COVID-19, according to researchers from 
# Johns Hopkins.''']

src_text = ['''WhatsApp users in Singapore, belonging to a certain demographic, had their world rocked recently after they received messages informing them that they would have to pay for using "Good Morning" images.
If you are in WhatsApp group chats with family members that also include seniors, you would have probably received earnest and pure message greetings in pictures.
It can get pretty spammy and smarmy if you do not feel inspired by such feel-good vibes.
And it seems like someone really has had enough of receiving these pictures, so much so that a message has been spreading on WhatsApp claiming that a two-way charge will be imposed on the senders and receivers of such pictures.
The message has recently been circulating among many WhatsApp users in Singapore, to the extent it is causing some alarm and greatly reducing the number of images sent.
Many seniors were probably hurt by this announcement, which is both fortunately and unfortunately not real -- depending on who you empathise with.
The above message that has been "forwarded many times" is not real.
WhatsApp messages are secured with end-to-end encryption.
This means that when you send a message to another person, only you and the other party can read or listen to what was sent.
Even WhatsApp as a platform cannot see what kind of pictures or texts were sent.
Therefore, a "Good Morning" image will not be detected.
WhatsApp remains a free messaging app and does not require any payment details to be given prior to use.
WhatsApp is owned by Facebook.''']

model_dir = 'models/pegasus-cnn_dailymail'
device = 'cpu'
tokenizer = PegasusTokenizer.from_pretrained(model_dir)
model = PegasusForConditionalGeneration.from_pretrained(model_dir).to(device)
print('TOKENIZER AND MODEL LOADED')
start_time = time.time()
batch = tokenizer(src_text, truncation=True, padding='longest', return_tensors="pt").to(device)
translated = model.generate(**batch, length_penalty=1.5)
tgt_text = tokenizer.batch_decode(translated, skip_special_tokens=True)
print(f'TIME TAKEN: {time.time() - start_time}')
print('******************************************')
print(tgt_text)

##############################################################
# USE BART
# bart-large-cnn
# distilbart-cnn-12-6
##############################################################
# model_dir = 'models/bart-large-cnn'
# model = BartForConditionalGeneration.from_pretrained(model_dir)
# tokenizer = BartTokenizer.from_pretrained(model_dir)
# print('TOKENIZER AND MODEL LOADED')
# start_time = time.time()
# inputs = tokenizer(src_text, truncation=True, max_length=1024, return_tensors='pt')

# # Generate Summary
# summary_ids = model.generate(inputs['input_ids'], num_beams=4, max_length=100, early_stopping=True)
# print(f'TIME TAKEN: {time.time() - start_time}')
# print('******************************************')
# print([tokenizer.decode(g, skip_special_tokens=True, clean_up_tokenization_spaces=False) for g in summary_ids])
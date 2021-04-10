"""
Authors: Adriel Kuek, Chua Hao Zi, Lavanya, Francis Louis
Date Created: 25 March 2021
Version:
Email: hz29990@gmail.com, adrielkuek@gmail.com, francis.louis@gmail.com, lavanya2204@hotmail.com
Status: Devlopment

Description:
SureBo(T) is an end to end automatec fact-checking BOT based on
TELEGRAM API that retrieves multi document inputs for fact
verification based on a single input query. The input query currently
takes the form of a text message that is dubious in content.

In fulfilment of the requirements for the Intelligent Reasoning Systems
project under the Master of Technology (Intelligent Systems)
- NUS Institute of System Sciences (AY2021 - Semester 2)

"""
from newspaper import fulltext, Article, Config
import requests, time, os, numpy as np, pandas as pd
from transformers import AutoTokenizer, AutoModel, PegasusTokenizer, PegasusForConditionalGeneration
from sentence_transformers import SentenceTransformer, util
from pygooglenews import GoogleNews
from spacy.lang.en import English
from pprint import pprint
import validators
import torch
import matplotlib.pyplot as plt
import seaborn as sns
import re
import emoji
from celery.exceptions import SoftTimeLimitExceeded

from EvidenceRetrieval import EvidenceRetrieval
from GraphNetFC import graphNetFC

device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
print(f'DEVICE Available: {device}')

# Params - ER
length_penalty = 1.5
topN = 5
max_length = 128
dist_thres = 0.4
# Params - GraphNET
feature_num = 768
evidence_num = 5
graph_layers = 2
num_class = 3
sequence_length = 128
# Aggregating method: top, max, mean, concat, att, sum
graph_pool = 'att'


def executePipeline(query):
    #####################################################
    # Initialization
    #####################################################
    try:
        start = time.time()
        cwd = os.path.dirname(os.path.realpath(__file__))
        print(f'INITIALISE EVIDENCE RETRIEVAL PIPELINE . . .')
        ER_pipeline = EvidenceRetrieval(cwd, device)

        ################# SAMPLE QUERIES/URLS #####################
        # query = "A bus driver has been arrested for careless driving following an accident at Loyang Avenue that killed a 31-year-old cyclist."
        # query = "I will be charged for sending Whatsapp Good morning messages"
        # query = "Alabama nurse in the states has just had the vaccine and she died 8 hours later"
        # query = "https://www.straitstimes.com/singapore/bus-driver-arrested-for-careless-driving-after-cyclist-31-pronounced-dead-in-loyang?utm_source=Telegram&utm_medium=Social&utm_campaign=STTG"
        # query = "https://www.theonlinecitizen.com/2020/07/03/10-mil-population-debacle-sdp-questions-why-former-dpm-heng-did-not-refute-st-report-at-the-time-it-was-published/"
        # query = "https://newnaratif.com/podcast/an-interview-with-dr-paul-tambyah/"
        # query = "https://www.straitstimes.com/tech/tech-news/whatsapp-delays-data-sharing-change-after-backlash-sees-users-flock-to-rivals"

        # Commenting below statement because of UnicodeEncodeError when Emoji's are present
        # print(f'INPUT QUERY: {query}')

        # Check URL Validity
        '''
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.163 Safari/535.1'}
        query_urlstatus = validators.url(query)
        if query_urlstatus == True:
            querytext = fulltext(requests.get(query, headers=headers).text)
        else:
            querytext = query
        '''
        # Query Preprocessing
        querytext = query_preprocessing(query)

        # Use SPACY to get number of tokens
        nlp = English()
        myDoc = nlp(querytext)
        sentenceToken = []
        for token in myDoc:
            sentenceToken.append(token.text)

        print(f'TOTAL NO. OF TOKENS FROM QUERY: {len(sentenceToken)}')
        print(sentenceToken)

        # If tokens > 50 - Perform Abstractive Summary on Query
        # Else just skip and perform Doc Retrieval
        if len(sentenceToken) > 50:
            querytext = ER_pipeline.AbstractiveSummary(querytext, length_penalty)

        # Run ER pipeline
        start_time = time.time()
        Filtered_Articles = []
        Filtered_Articles = ER_pipeline.RetrieveArticles(querytext, topN)
        print(f'>>>>>>> TIME TAKEN - ER PIPELINE: {time.time() - start_time}')

        output_message = "===== FACT CHECK RESULTS ====="
        output_message += "\nTime-Taken: {} seconds".format(int(time.time() - start))
        output_message += "\nQuery Input: {}".format(query)

        print(len(Filtered_Articles))
        if len(Filtered_Articles) == 0:
            output_message += '\n\nNO MATCHING ARTICLES FOUND. NOT ENOUGH EVIDENCE!'
            print(f'NO MATCHING ARTICLES FOUND. NOT ENOUGH EVIDENCE!')
        else:
            # Run Fact Verification - Graph NET
            graphNet = graphNetFC(cwd, device, feature_num, evidence_num, graph_layers,
                                  num_class, graph_pool, sequence_length)

            FactVerification_List = []
            for i in range(len(Filtered_Articles)):
                pred_dict, outputs, heatmap = graphNet.predict(querytext, Filtered_Articles[i][1])

                FactVerification_List.append(pred_dict['predicted_label'])
                print(pred_dict)
                print('[SUPPORTS, REFUTES, NOT ENOUGH INFO]')
                print((np.array(outputs)))

                # Plot Attention Heat map to visualize
                # ax = sns.heatmap(heatmap, linewidth=1.0, cmap="YlGnBu")
                # plt.show()
                # plt.clf()

            maj_vote = 0
            for i in range(len(Filtered_Articles)):
                print(f'ARTICLE: {Filtered_Articles[i][2]} - {FactVerification_List[i]}')
                if FactVerification_List[i] == 'SUPPORTS':
                    maj_vote += 1

            if (maj_vote / len(Filtered_Articles)) > 0.6:
                final_score = 'SUPPORTS'
                print(f'************** FINAL SCORE: SUPPORTS')
            elif (maj_vote / len(Filtered_Articles)) == 0.5:
                final_score = 'NOT ENOUGH EVIDENCE'
                print(f'************** FINAL SCORE: NOT ENOUGH SUPPORTING EVIDENCE')
            else:
                final_score = 'REFUTES'
                print(f'************** FINAL SCORE: REFUTES')

            output_message += '\n\nFINAL SCORE: ' + final_score
            output_message += "\n\n----- Total Articles Found: {} -----".format(len(Filtered_Articles))
            for i in range(len(Filtered_Articles)):
                output_message += "\n\nURL {}".format(i+1)
                output_message += '\n' + Filtered_Articles[i][2] + '\n*[Summary]* '
                for j in range(len(Filtered_Articles[i][1])):
                    output_message += Filtered_Articles[i][1][j]
    except Exception as e:
        if isinstance(e, SoftTimeLimitExceeded):
            raise
        else:
            output_message = 'Exception occurred in pipeline'

    return output_message


def remove_emoji(text):
    return emoji.get_emoji_regexp().sub(u'', text)


def query_preprocessing(query):
    # Remove all EMOJI's from query
    query = query.encode('utf-16', 'surrogatepass').decode('utf-16')
    query = remove_emoji(query)

    # Extract all URL's and replace them with the text in the URL
    link_regex = re.compile('(?P<url>https?://[^\s]+)', re.DOTALL)
    links = re.findall(link_regex, query)

    for link in links:
        # Check URL Validity
        try:
            headers = {
                'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.163 Safari/535.1'}
            query_urlstatus = validators.url(link)
            if query_urlstatus:
                url_text = fulltext(requests.get(link, headers=headers).text)
            else:
                url_text = link
            query = query.replace(link, url_text)
        except:
            print('Exception when extracting full text from URL')

    # Need to check if replacing of special characters is necessary for pegasus model
    # query = re.sub("[\n!@#$%^&*()\[\]{};:/<>?|`~\-=_+\t]", " ", query)
    # query = re.sub("\n", " ", query)
    return query


if __name__ == "__main__":
    text = "Malaysia is a Asian country"
    result = executePipeline(text)
    result = result.encode('utf-16', 'surrogatepass').decode('utf-16')
    print('Result is: ' + result)

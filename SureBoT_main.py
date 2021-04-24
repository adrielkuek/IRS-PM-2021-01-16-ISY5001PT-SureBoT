"""
Authors: Adriel Kuek, Chua Hao Zi, Lavanya, Francis Louis
Date Created: 25 March 2021
Version:
Email: hz29990@gmail.com, adrielkuek@gmail.com, francis.louis@gmail.com, lavanya2204@hotmail.com
Status: Development

Description:
SureBo(T) is an end to end automatic fact-checking BOT based on
TELEGRAM API that retrieves multi document inputs for fact
verification based on a single input query. The input query currently
takes the form of a text message that is dubious in content.

In fulfilment of the requirements for the Intelligent Reasoning Systems
project under the Master of Technology (Intelligent Systems)
- NUS Institute of System Sciences (AY2021 - Semester 2)

"""
from newspaper import fulltext
import requests, time, os, numpy as np
from spacy.lang.en import English
import validators
import torch
import re
import emoji
from celery.exceptions import SoftTimeLimitExceeded
import logging

from EvidenceRetrieval import EvidenceRetrieval
from GraphNetFC import graphNetFC
from pyfiglet import Figlet

device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
device_cpu = 'cpu'

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


def executePipeline(query, surebot_logger):
    #####################################################
    # Initialization
    #####################################################
    try:
        print(f'DEVICE Available: {device}')
        surebot_logger.info(f'\n=============== NEW QUERY ===============')
        surebot_logger.info(f'DEVICE Available: {device}')
        start = time.time()
        cwd = os.path.dirname(os.path.realpath(__file__))
        print(f'INITIALISE EVIDENCE RETRIEVAL PIPELINE . . .')
        surebot_logger.info(f'INITIALISE EVIDENCE RETRIEVAL PIPELINE . . .')
        ER_pipeline = EvidenceRetrieval(cwd, device, surebot_logger)

        # Query Preprocessing
        querytext = query_preprocessing(query, surebot_logger)

        # Use SPACY to get number of tokens
        nlp = English()
        myDoc = nlp(querytext)
        sentenceToken = []
        for token in myDoc:
            sentenceToken.append(token.text)

        print(f'TOTAL NO. OF TOKENS FROM QUERY: {len(sentenceToken)}')
        surebot_logger.info(f'TOTAL NO. OF TOKENS FROM QUERY: {len(sentenceToken)}')
        print(sentenceToken)
        surebot_logger.info(sentenceToken)

        # If tokens > 50 - Perform Abstractive Summary on Query
        # Else just skip and perform Doc Retrieval
        if len(sentenceToken) > 50:
            querytext = ER_pipeline.AbstractiveSummary(querytext, length_penalty)

        # Run ER pipeline
        start_time = time.time()
        Filtered_Articles = []
        Filtered_Articles = ER_pipeline.RetrieveArticles(querytext, topN)
        print(f'>>>>>>> TIME TAKEN - ER PIPELINE: {time.time() - start_time}')
        surebot_logger.info(f'>>>>>>> TIME TAKEN - ER PIPELINE: {time.time() - start_time}')

        print(f'===== ARTICLES RETRIEVAL RESULTS =====')
        surebot_logger.info(f'===== ARTICLES RETRIEVAL RESULTS =====')
        print(f'Number of Articles After Filtering: {len(Filtered_Articles)}')
        surebot_logger.info(f'Number of Articles After Filtering: {len(Filtered_Articles)}')

        output_message = "===== FACT CHECK RESULTS ====="
        output_message += "\nTime-Taken: {} seconds".format(int(time.time() - start))
        output_message += "\nQuery Input: {}".format(query)

        if len(Filtered_Articles) == 0:
            output_message += '\n\nNO MATCHING ARTICLES FOUND. NOT ENOUGH EVIDENCE!'
            print(f'NO MATCHING ARTICLES FOUND. NOT ENOUGH EVIDENCE!')
            surebot_logger.info(f'NO MATCHING ARTICLES FOUND. NOT ENOUGH EVIDENCE!')
        else:
            # Run Fact Verification - Graph NET
            graphNet = graphNetFC(cwd, device_cpu, feature_num, evidence_num, graph_layers,
                                  num_class, graph_pool, sequence_length, surebot_logger)

            FactVerification_List = []
            for i in range(len(Filtered_Articles)):
                pred_dict, outputs, heatmap = graphNet.predict(querytext, Filtered_Articles[i][1])

                FactVerification_List.append(pred_dict['predicted_label'])
                print(pred_dict)
                surebot_logger.info(pred_dict)
                print('[SUPPORTS, REFUTES, NOT ENOUGH INFO]')
                surebot_logger.info('[SUPPORTS, REFUTES, NOT ENOUGH INFO]')
                print((np.array(outputs.detach().cpu())))
                surebot_logger.info((np.array(outputs.detach().cpu())))

                # Plot Attention Heat map to visualize
                # ax = sns.heatmap(heatmap, linewidth=1.0, cmap="YlGnBu")
                # plt.show()
                # plt.clf()

            maj_vote = 0
            for i in range(len(Filtered_Articles)):
                print(f'ARTICLE: {Filtered_Articles[i][2]} - {FactVerification_List[i]}')
                surebot_logger.info(f'ARTICLE: {Filtered_Articles[i][2]} - {FactVerification_List[i]}')
                if FactVerification_List[i] == 'SUPPORTS':
                    maj_vote += 1

            if (maj_vote / len(Filtered_Articles)) > 0.6:
                final_score = 'SUPPORTS'
                print(f'************** FINAL SCORE: SUPPORTS')
                surebot_logger.info(f'************** FINAL SCORE: SUPPORTS')
            elif (maj_vote / len(Filtered_Articles)) == 0.5:
                final_score = 'NOT ENOUGH EVIDENCE'
                print(f'************** FINAL SCORE: NOT ENOUGH SUPPORTING EVIDENCE')
                surebot_logger.info(f'************** FINAL SCORE: NOT ENOUGH SUPPORTING EVIDENCE')
            else:
                final_score = 'REFUTES'
                print(f'************** FINAL SCORE: REFUTES')
                surebot_logger.info(f'************** FINAL SCORE: REFUTES')

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


def query_preprocessing(query, logger_handle):
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
            logger_handle.info('Exception when extracting full text from URL')

    return query


def configure_logger(chat):
    surebot_logger = logging.getLogger(chat)
    surebot_logger.setLevel(logging.INFO)
    logDir = './SurebotLog/'
    if not os.path.exists(logDir):
        os.makedirs(logDir)

    LogDir = logDir
    timing = time.asctime(time.localtime(time.time()))
    # logFile = logDir + '/' + timing.replace(' ','_') + '.log'
    logFile = logDir + '/chat_' + str(chat) + '.log'
    handler = logging.FileHandler(logFile)

    formatter = logging.Formatter('')
    handler.setFormatter(formatter)
    surebot_logger.addHandler(handler)

    return surebot_logger


if __name__ == "__main__":

    chat = 0
    surebot_logger = configure_logger(chat)
    custom_fig = Figlet(font='slant')
    surebot_banner = custom_fig.renderText("SureBoT")
    print('\n')
    print(surebot_banner + "version1.0\n")
    surebot_logger.info('\n')
    surebot_logger.info(surebot_banner + "version1.0\n")

    while True:
        print(f'\n\nSureBoT: Input a claim that you would like to fact-check!')
        surebot_logger.info(f'SureBoT: Input a claim that you would like to fact-check!')
        input_claim = str(input("Claim: "))
        print(f'\n\nProcessing your claim......')
        surebot_logger.info(input_claim)
        result = executePipeline(input_claim, surebot_logger)
        result = result.encode('utf-16', 'surrogatepass').decode('utf-16')
        print('Result is: ' + result)

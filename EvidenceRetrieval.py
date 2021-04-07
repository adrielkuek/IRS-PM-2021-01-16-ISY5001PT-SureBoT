"""
Author: Hao Zi/Adriel
Date Created: 25 March 2021
Version:
Email: hz29990@gmail.com, adrielkuek@gmail.com
Status: Devlopment

Description:
Evidence Retrieval is a multi-stage document retrieval framework that takes an input
query, crawls the web for relevant articles and outputs the most relevant summarized
articles for downstream processing

1. Input query into GoogleNews to generate list of relevant Articles
2. Employ Newspaper3k and requests API to retrieve full raw text articles from top 5 match
3. Perform Abstractive Summarization using PegasusSummarizer to get salient points
4. Perform SentenceBERT semantic similar of summarized articles with input query to
retrieve top relevant articles
5. Return summarized articles as a list

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

# Params
length_penalty = 1.5
topN = 5
max_length = 128
dist_thres = 0.4


class EvidenceRetrieval(object):
    def __init__(self, filepath, device):
        self.device = device
        self.filepath = filepath
        # Initialise GoogleNews API
        self.pygn = GoogleNews(lang="en")
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.163 Safari/535.1'}

        # Load Models
        start_time = time.time()
        print(f'LOADING PEGASUS MODEL . . .')
        PegasusModel_dir = self.filepath + '/pipeline_models/models/pegasus-cnn_dailymail'
        self.PegasusTokenizer = PegasusTokenizer.from_pretrained(PegasusModel_dir)
        self.PegasusModel = PegasusForConditionalGeneration.from_pretrained(PegasusModel_dir).to(self.device)
        print('\n*******PEGASUS TOKENIZER AND MODEL LOADED*******')
        print(f'LOADING SENTENCE-BERT MODEL . . .')
        # SentenceModel_dir = self.filepath + '/pipeline_models/models/stsb-distilbert-base'
        SentenceModel_dir = self.filepath + '/pipeline_models/models/msmarco-distilroberta-base-v2'
        self.sentenceTokenizer = AutoTokenizer.from_pretrained(SentenceModel_dir)
        self.sentenceBERT = AutoModel.from_pretrained(SentenceModel_dir)
        print('\n*******DISTILROBERTA MODEL LOADED*******')
        print(f'>>>>>>> TIME TAKEN - MODELS LOADING: {time.time() - start_time}')

    def AbstractiveSummary(self, input_text, length_penalty):
        start_time = time.time()
        batch = self.PegasusTokenizer(input_text, truncation=True, padding='longest', return_tensors="pt").to(
            self.device)
        translated = self.PegasusModel.generate(**batch, length_penalty=length_penalty)
        summary = self.PegasusTokenizer.batch_decode(translated, skip_special_tokens=True)
        print('\n******************************************')
        summary = "".join(summary)
        print(summary)
        print(f'>>>>>>> TIME TAKEN - ABSTRACTIVE SUMMARY: {time.time() - start_time}')
        return summary

    def RetrieveArticles(self, input_text, topN):
        #####################################################
        # Search Googlenews & Extract Articles
        #####################################################
        search = self.pygn.search(input_text)
        articleurls, articlesummarylist, similaritylist = [], [], []

        # Extract list of article urls
        for article_num in range(len(search["entries"])):
            article_info = search["entries"][article_num]["links"]
            articleurls.append(article_info[-1]["href"])
        print(f'\n******* Found No. of articles = {len(articleurls)} *******')

        # Summarize the article (take TopN where N is number of articles)
        for article_url in articleurls[:topN]:
            try:
                articletext = fulltext(requests.get(article_url, headers=self.headers).text)

                # ************************#
                # RUN PEGASUS
                # ************************#
                print(f'PERFORMING ABSTRACTION - ARTICLE: {article_url} . . .')
                articlesummary = self.AbstractiveSummary(articletext, length_penalty)
                articlesummarylist.append("".join(articlesummary))

            except Exception as e:
                articlesummarylist.append("")

        # pprint(articlesummarylist)

        # Retrieve Sentence Embeddings for input query
        query_embedding = self.semanticSimilarity(input_text, max_length)

        # Retreive Sentence Embeddings for articles
        for summary in articlesummarylist:
            article_embedding = self.semanticSimilarity(summary, max_length)
            # Cosine Distance Scoring
            similarityscore = util.pytorch_cos_sim(query_embedding, article_embedding)
            similaritylist.append(similarityscore.detach().cpu().numpy())

        print(f'SIMILARITY LIST SCORES: {similaritylist}')

        #####################################################
        # Filter Relevant Articles - Distance Threshold > 0.4
        #####################################################
        articlesimilarity = [list(x) for x in zip(np.array(similaritylist), articlesummarylist, articleurls)]
        filteredarticles = [[article[0], article[1].split(sep="<n>"), article[2]]
                            for article in articlesimilarity if article[0] > dist_thres]

        pprint(filteredarticles)

        # Output to excel/csv file [Optional]
        # df = pd.DataFrame(filteredarticles, columns=["Score", "Summarized Content", "URL"])
        # df.to_excel(self.filepath + "/Output.xlsx", sheet_name="Query")

        return filteredarticles

    def semanticSimilarity(self, input_text, max_length):
        #############################################
        # Sentence Bert Comparision
        #############################################
        start_time = time.time()
        encoded_input = self.sentenceTokenizer(input_text, padding=True, truncation=True, max_length=max_length,
                                               return_tensors='pt')
        # query_embedding = sentenceBERT.encode(querysummary)
        with torch.no_grad():
            model_output = self.sentenceBERT(**encoded_input)
        sentence_embeddings = self.mean_pooling(model_output, encoded_input['attention_mask'])
        print(f'>>>>>>> TIME TAKEN - SEMANTIC COMPARISON: {time.time() - start_time}')
        return sentence_embeddings

    # Mean Pooling - Take attention mask into account for correct averaging
    def mean_pooling(self, model_output, attention_mask):
        token_embeddings = model_output[0]  # First element of model_output contains all token embeddings
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        sum_embeddings = torch.sum(token_embeddings * input_mask_expanded, 1)
        sum_mask = torch.clamp(input_mask_expanded.sum(1), min=1e-9)
        return sum_embeddings / sum_mask


def main():
    device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
    print(f'DEVICE Available: {device}')

    #####################################################
    # Initialization
    #####################################################
    start = time.time()
    cwd = os.path.dirname(os.path.realpath(__file__))
    print(f'INITIALISE EVIDENCE RETRIEVAL PIPELINE . . .')
    ER_pipeline = EvidenceRetrieval(cwd, device)

    ################# SAMPLE QUERIES/URLS #####################
    query = "A bus driver has been arrested for careless driving following an accident at Loyang Avenue that killed a 31-year-old cyclist."
    # query = "I will be charged for sending Whatsapp Good morning messages"
    # query = "https://news.nestia.com/detail_share/5599913?media_type=1&nestiaShareChannel=whatsapp"
    # query = "https://www.straitstimes.com/singapore/bus-driver-arrested-for-careless-driving-after-cyclist-31-pronounced-dead-in-loyang?utm_source=Telegram&utm_medium=Social&utm_campaign=STTG"
    # query = "https://www.theonlinecitizen.com/2020/07/03/10-mil-population-debacle-sdp-questions-why-former-dpm-heng-did-not-refute-st-report-at-the-time-it-was-published/"
    # query = "https://newnaratif.com/podcast/an-interview-with-dr-paul-tambyah/"
    # query = "https://www.straitstimes.com/tech/tech-news/whatsapp-delays-data-sharing-change-after-backlash-sees-users-flock-to-rivals"
    print(f'INPUT QUERY: {query}')

    # Check URL Validity
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.163 Safari/535.1'}
    query_urlstatus = validators.url(query)
    if query_urlstatus == True:
        querytext = fulltext(requests.get(query, headers=headers).text)
    else:
        querytext = query

    # Use SPACY to get number of tokens
    nlp = English()
    myDoc = nlp(querytext)
    sentenceToken = []
    for token in myDoc:
        sentenceToken.append(token.text)

    print(f'TOTAL NO. OF TOKENS FROM QUERY: {len(sentenceToken)}')

    # If tokens > 50 - Perform Abstractive Summary on Query
    # Else just skip and perform Doc Retrieval
    if len(sentenceToken) > 50:
        querytext = ER_pipeline.AbstractiveSummary(querytext, length_penalty)

    # Run ER pipeline
    start_time = time.time()
    Filtered_Articles = []
    Filtered_Articles = ER_pipeline.RetrieveArticles(querytext, topN)
    print(f'>>>>>>> TIME TAKEN - ER PIPELINE: {time.time() - start_time}')


if __name__ == "__main__":
    main()

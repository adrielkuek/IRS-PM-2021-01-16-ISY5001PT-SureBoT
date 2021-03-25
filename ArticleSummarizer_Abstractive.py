from newspaper import fulltext, Article, Config
import requests, time, os, numpy as np, pandas as pd
from transformers import *
from sentence_transformers import SentenceTransformer, util
from pygooglenews import GoogleNews
# import pprint, nltk, validators
import pprint, validators

#####################################################
# Initialization
#####################################################

cwd = os.path.dirname(__file__)
start = time.time()
pygn = GoogleNews(lang="en")
# nltk.download('punkt')#1 time download of the sentence tokenizer
headers = {'user-agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.163 Safari/535.1'}

#####################################################
# Query Claim (User Input)
#####################################################

############## Sample URLS #######################
query = "A bus driver has been arrested for careless driving following an accident at Loyang Avenue that killed a 31-year-old cyclist."
# query = "I will be charged for sending Whatsapp Good morning messages"
# query = "https://news.nestia.com/detail_share/5599913?media_type=1&nestiaShareChannel=whatsapp"
# query = "https://www.straitstimes.com/singapore/bus-driver-arrested-for-careless-driving-after-cyclist-31-pronounced-dead-in-loyang?utm_source=Telegram&utm_medium=Social&utm_campaign=STTG"
# query = "https://www.theonlinecitizen.com/2020/07/03/10-mil-population-debacle-sdp-questions-why-former-dpm-heng-did-not-refute-st-report-at-the-time-it-was-published/"
# query = "https://newnaratif.com/podcast/an-interview-with-dr-paul-tambyah/"
# query = "https://www.straitstimes.com/tech/tech-news/whatsapp-delays-data-sharing-change-after-backlash-sees-users-flock-to-rivals"

query_urlstatus = validators.url(query)

if query_urlstatus == True:
    querytext = fulltext(requests.get(query, headers=headers).text)
else: 
    querytext = query

print(f'QUERY: {querytext}')

#************************#
# Pegasus Summarizer
#************************#

model_dir = cwd + '/models/pegasus-cnn_dailymail'
device = 'cpu'
tokenizer = PegasusTokenizer.from_pretrained(model_dir)
# model = PegasusForConditionalGeneration.from_pretrained(model_dir).to(device)
print('\n*******TOKENIZER AND MODEL LOADED*******')
batch = tokenizer(querytext, truncation=True, padding='longest', return_tensors="pt").to(device)
print(batch['input_ids'].shape)
# translated = model.generate(**batch, length_penalty=0.5)
# querysummary = tokenizer.batch_decode(translated, skip_special_tokens=True)
# print('\n******************************************')
# querysummary = "".join(querysummary)
# print(querysummary)

# #####################################################
# # Search Googlenews & Extract Articles
# #####################################################

# # Search Topic in Google News
# search = pygn.search(querysummary)
# articleurls, articlesummarylist, similaritylist = [] , [],  []

# # Extract list of article urls
# for article_num in range(len(search["entries"])):
#     article_info = search["entries"][article_num]["links"]
#     articleurls.append(article_info[-1]["href"])
# print("\n******* No of articles = {} *******" .format(str(len(articleurls))))

# # Summarize the article (take top 10)
# for article_url in articleurls[:10]:
#     try: 
#         articletext = fulltext(requests.get(article_url, headers=headers).text)

#         #************************#
#         # Pegasus Summarizer
#         #************************#

#         batch = tokenizer(articletext, truncation=True, padding='longest', return_tensors="pt").to(device)
#         translated = model.generate(**batch, length_penalty=1.5)
#         articlesummary = tokenizer.batch_decode(translated, skip_special_tokens=True)
#         articlesummarylist.append("".join(articlesummary))

#     except Exception as e:
#         articlesummarylist.append("")

# pprint.pprint(articlesummarylist)

# #############################################
# # Sentence Bert Comparision
# #############################################

# modelsentence = SentenceTransformer('msmarco-distilroberta-base-v2')
# query_embedding = modelsentence.encode(querysummary)

# for summary in articlesummarylist:
#     passage_embedding = modelsentence.encode(summary)
#     similarityscore = util.pytorch_cos_sim(query_embedding, passage_embedding)
#     similaritylist.append(similarityscore)

# print("*****************")
# print(np.array(similaritylist))

# #############################################
# # Filter Relevant Articles
# #############################################

# articlesimilarity = [list(x) for x in zip(np.array(similaritylist), articlesummarylist, articleurls)]
# filteredarticles = [[article[0], article[1].split(sep="<n>"), article[2]] for article in articlesimilarity if article[0] >0.4]
# pprint.pprint(filteredarticles)

# df = pd.DataFrame(filteredarticles, columns=["Score", "Summarized Content", "URL"])
# df.to_excel(cwd + "/Output.xlsx", sheet_name="Query")

# print("\nProgram Executed in "+str(time.time() - start)) 




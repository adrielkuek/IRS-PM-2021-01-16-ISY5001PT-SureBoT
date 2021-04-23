# from transformers import pipeline
# from transformers import AutoTokenizer, AutoModelForSequenceClassification
# import json

# tokenizer = AutoTokenizer.from_pretrained("facebook/bart-large-mnli")
# model = AutoModelForSequenceClassification.from_pretrained("facebook/bart-large-mnli")

# nlpClassify = pipeline(task='zero-shot-classification', tokenizer=tokenizer, model=model)

# sequences = 'COVID 19 vaccination causes death!'
# labels = ['misinformation', 'politics', 'health care', 'jokes']

# results = nlpClassify(sequences=sequences, candidate_labels=labels, multi_class=False)
# resultStr = json.dumps(results)
# print(type(results))
# print(results)
# print(resultStr)

# import textwrap
# from itertools import islice
n = 5

# filehandle = open('celery_log.log', 'r')
# while True:
#     n_lines = list(islice(filehandle, n))
#     if not n_lines:
#         break
#     print(n_lines)
# sampleText = open('celery_log.log', 'r')
# data = sampleText.read()
# data_line = sampleText.readline(2)
# sampleText.close()
# # data_short = textwrap.wrap(data, 10)
# print(data_line)
# print(len(data))

filehandle = open('celery_log.log', 'r')
while True:
    # read a single line
    # for i in range(n):
    line = filehandle.readline()
    for i in range(n):
        if not line:
            break
        line += filehandle.readline()
        line += filehandle.readline()
        line += filehandle.readline()
        line += filehandle.readline()
    if not line:
        break
    print(line)
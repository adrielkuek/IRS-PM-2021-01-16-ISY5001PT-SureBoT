from transformers import pipeline
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import json

tokenizer = AutoTokenizer.from_pretrained("facebook/bart-large-mnli")
model = AutoModelForSequenceClassification.from_pretrained("facebook/bart-large-mnli")

nlpClassify = pipeline(task='zero-shot-classification', tokenizer=tokenizer, model=model)

sequences = 'COVID 19 vaccination causes death!'
labels = ['misinformation', 'politics', 'health care', 'jokes']

results = nlpClassify(sequences=sequences, candidate_labels=labels, multi_class=False)
resultStr = json.dumps(results)
print(type(results))
print(results)
print(resultStr)
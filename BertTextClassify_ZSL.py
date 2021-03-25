"""
Test Programme to evaluate Bert's Zero-Shot-Learning Classification
Model is very large. Caution: When loaded into memory, CPU may hang
Ensure that com has enough RAM or use GPU where possible. (Kill Chrome)

SequenceClassification NLI Models:
- facebook/bart-large-mnli
- joeddav/xlm-roberta-large-xnli
- valhalla/distilbart-mnli-12-3 (distilbart-mnli is the distilled version of 
bart-large-mnli created using the No Teacher Distillation technique proposed 
for BART summarisation by Huggingface,)
"""

from transformers import pipeline
from transformers import AutoTokenizer, AutoModelForSequenceClassification
tokenizer = AutoTokenizer.from_pretrained("facebook/bart-large-mnli")
model = AutoModelForSequenceClassification.from_pretrained("facebook/bart-large-mnli")

nlpClassify = pipeline(task='zero-shot-classification', tokenizer=tokenizer, model=model)

sequences = 'COVID 19 vaccination causes death!'
labels = ['misinformation', 'politics', 'health care', 'jokes']

results = nlpClassify(sequences=sequences, candidate_labels=labels, multi_class=False)
print(results)

#------------------------------------------------------------------
# Alternatvely, if either ones of the above model doesn't fit, can
# try a smaller model to do Sentiment Analysis as a start
# Comment out the above piece of code and run the bottom one
#-----------------------------------------------------------------

from transformers import pipeline

# Initiate the classifier pipeline - This by default uses the DistillBERT
# architecture which  has been fine-tuned on SST-2 dataset which is 
# sentiment analysis dataset
nlpClassify = pipeline('sentiment-analysis')

# Sample text to input
input_text = 'We are happy today to have with us Batman to help clean up Gothem City.'
results = nlpClassify(input_text)
print(results)

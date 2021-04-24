"""
Author: Adriel Kuek
Date Created: 06 March 2021
Version:
Email: adrielkuek@gmail.com
Status: Development

Description:
GraphNetFC is a Fact Checking model based on GEAR pipeline for claim-evidences fact-checking
based on this paper: https://arxiv.org/abs/1908.01843
GEAR: Graph-based Evidence Aggregating and Reasoning for Fact Verification.

Method  employs a 3-step pipeline including Sentence Feature Extraction using BERT sentence encoder,
followed by a fully-connected evidence graph - Evidence Reasoning Network (ERNet) to propagate
information among evidence and reason over the graph. Finally, utilise an evidence aggregator to infer
prediction results.

"""

import numpy as np
import os
import time
import matplotlib.pyplot as plt
import seaborn as sns

import torch
from torch.utils.data import TensorDataset
from pytorch_pretrained_bert.tokenization import BertTokenizer
from pytorch_pretrained_bert.modeling import BertModel

from utils import load_bert_features_claim_inference
from Models import GEAR

BERTpretrained_dir = 'pipeline_models/pretrained_models/BERT-Pair/'
graphNet_model_dir = 'pipeline_models/models/2layerbest.pth.tar'

feature_num = 768
evidence_num = 5
graph_layers = 2
num_class = 3
sequence_length = 128
# Aggregating method: top, max, mean, concat, att, sum
graph_pool = 'att'


class InputField(object):

    def __init__(self, text_a, text_b, is_claim):
        self.text_a = text_a
        self.text_b = text_b
        self.is_claim = is_claim

class InputFeatures(object):
    """A single set of features of data."""

    def __init__(self, tokens, input_ids, input_mask, input_type_ids, is_claim):
        self.tokens = tokens
        self.input_ids = input_ids
        self.input_mask = input_mask
        self.input_type_ids = input_type_ids
        self.is_claim = is_claim

class graphNetFC(object):
    def __init__(self, filepath, device, feature_num, evidence_num, 
                graph_layers, num_class, graph_pool, sequence_length, loggerHandle):
        self.filepath = filepath
        self.device = device
        self.logger = loggerHandle

        print(f'LOADING BERT PRETRAINED . . .')
        self.logger.info(f'LOADING BERT PRETRAINED . . .')
        # Load BERT pretrained
        self.tokenizer = BertTokenizer.from_pretrained(self.filepath + '/pipeline_models/pretrained_models/BERT-Pair/', do_lower_case=True)
        self.BERTmodel = BertModel.from_pretrained(self.filepath + '/pipeline_models/pretrained_models/BERT-Pair/')
        self.BERTmodel.to(self.device)
        self.BERTmodel.eval()

        print(f'LOADING GEAR PRETRAINED . . .')
        self.logger.info(f'LOADING GEAR PRETRAINED . . .')
        self.GEAR_model = self.filepath + '/pipeline_models/models/2layerbest.pth.tar'
        # self.BERT_pretrainedMODEL = BERTpretrained_model
        # self.GEAR_model = GEAR_model
        
        self.feature_num = feature_num
        self.evidence_num = evidence_num
        self.graph_layers = graph_layers
        self.num_class = num_class
        self.graph_pool = graph_pool
        self.sequence_length = sequence_length
    
    def extractFeatures(self, InputSentence, seq_length, tokenizer):
        features = []
        for (ex_index, inputs) in enumerate(InputSentence):

            tokens_a = tokenizer.tokenize(inputs.text_a)

            tokens_b = None
            if inputs.text_b:
                tokens_b = tokenizer.tokenize(inputs.text_b)

            if tokens_b:
                # Modifies `tokens_a` and `tokens_b` in place so that the total
                # length is less than the specified length.
                # Account for [CLS], [SEP], [SEP] with "- 3"
                self.truncate_seq_pair(tokens_a, tokens_b, (seq_length - 3))
            else:
                # Account for [CLS] and [SEP] with "- 2"
                if len(tokens_a) > seq_length - 2:
                    tokens_a = tokens_a[0:(seq_length - 2)]

            # The convention in BERT is:
            # (a) For sequence pairs:
            #  tokens:   [CLS] is this jack ##son ##ville ? [SEP] no it is not . [SEP]
            #  type_ids: 0   0  0    0    0     0       0 0    1  1  1  1   1 1
            # (b) For single sequences:
            #  tokens:   [CLS] the dog is hairy . [SEP]
            #  type_ids: 0   0   0   0  0     0 0
            #
            # Where "type_ids" are used to indicate whether this is the first
            # sequence or the second sequence. The embedding vectors for `type=0` and
            # `type=1` were learned during pre-training and are added to the wordpiece
            # embedding vector (and position vector). This is not *strictly* necessary
            # since the [SEP] token unambigiously separates the sequences, but it makes
            # it easier for the model to learn the concept of sequences.
            #
            # For classification tasks, the first vector (corresponding to [CLS]) is
            # used as as the "sentence vector". Note that this only makes sense because
            # the entire model is fine-tuned.

            tokens = []
            input_type_ids = []
            tokens.append("[CLS]")
            input_type_ids.append(0)
            for token in tokens_a:
                tokens.append(token)
                input_type_ids.append(0)
            tokens.append("[SEP]")
            input_type_ids.append(0)

            if tokens_b:
                for token in tokens_b:
                    tokens.append(token)
                    input_type_ids.append(1)
                tokens.append("[SEP]")
                input_type_ids.append(1)

            input_ids = tokenizer.convert_tokens_to_ids(tokens)

            # The mask has 1 for real tokens and 0 for padding tokens. Only real
            # tokens are attended to.
            input_mask = [1] * len(input_ids)

            # Zero-pad up to the sequence length.
            while len(input_ids) < seq_length:
                input_ids.append(0)
                input_mask.append(0)
                input_type_ids.append(0)

            assert len(input_ids) == seq_length
            assert len(input_mask) == seq_length
            assert len(input_type_ids) == seq_length

            if ex_index < 5:
                print(f'*** SENTENCE {ex_index} ***')
                print("tokens: %s" % " ".join([str(x) for x in tokens]))
                # print("input_ids: %s" % " ".join([str(x) for x in input_ids]))
                self.logger.info(f'*** SENTENCE {ex_index} ***')
                self.logger.info("tokens: %s" % " ".join([str(x) for x in tokens]))
                # self.logger.info("input_ids: %s" % " ".join([str(x) for x in input_ids]))
                # print("input_mask: %s" % " ".join([str(x) for x in input_mask]))
                # print("input_type_ids: %s" % " ".join([str(x) for x in input_type_ids]))

            features.append(
                InputFeatures(
                    tokens=tokens,
                    input_ids=input_ids,
                    input_mask=input_mask,
                    input_type_ids=input_type_ids,
                    is_claim=inputs.is_claim))
        return features


    def truncate_seq_pair(self, tokens_a, tokens_b, max_length):
        """Truncates a sequence pair in place to the maximum length."""

        # This is a simple heuristic which will always truncate the longer sequence
        # one token at a time. This makes more sense than truncating an equal percent
        # of tokens from each, since if one sequence is very short then each token
        # that's truncated likely contains more information than a longer sequence.
        while True:
            total_length = len(tokens_a) + len(tokens_b)
            if total_length <= max_length:
                break
            if len(tokens_a) > len(tokens_b):
                tokens_a.pop()
            else:
                tokens_b.pop()

    def get_predicted_label(self, items):
        # labels = ['SUPPORTS', 'REFUTES', 'NOT ENOUGH INFO']
        labels = ['SUPPORTS', 'REFUTES']
        binary_items = np.array(items)
        binary_items = binary_items[0][0:2]
        # return labels[np.argmax(np.array(items))]
        # Predict and return only binary classification - We ignore NEI class
        return labels[np.argmax(binary_items)]

    def predict(self, input_claim, input_evidence):
        
        # Start timer to track prediction timing
        start_time = time.time()

        # 2. Chain the inputs together               
        # Store the Claims Field
        combined_input = []
        combined_input.append(InputField(text_a=input_claim, text_b=None, is_claim=True))
        for evidence in input_evidence:
            combined_input.append(InputField(text_a=evidence, text_b=input_claim, 
                                        is_claim=False))

        # 3. Extract features from the input. Sequence length is limited to 128
        features = self.extractFeatures(combined_input, self.sequence_length, self.tokenizer)

        # 5. Store feature fields into torch tensor
        all_input_ids = torch.tensor([f.input_ids for f in features], dtype=torch.long)
        all_input_mask = torch.tensor([f.input_mask for f in features], dtype=torch.long)
        all_segment_ids = torch.tensor([f.input_type_ids for f in features], dtype=torch.long)
        all_example_index = torch.arange(all_input_ids.size(0), dtype=torch.long)

        # Unsqueeze
        all_input_ids = all_input_ids.unsqueeze(0)
        all_input_mask = all_input_mask.unsqueeze(0)
        all_segment_ids = all_segment_ids.unsqueeze(0)
        all_example_index = all_example_index.unsqueeze(0)
        eval_data = TensorDataset(all_input_ids, all_input_mask, all_segment_ids, all_example_index)

        # Perfrom BERT embeddings retrieval
        sentence_embeddings = []
        for input_ids, input_mask, segment_ids, example_indices in eval_data:
            input_ids = input_ids.to(self.device)
            input_mask = input_mask.to(self.device)
            segment_ids = segment_ids.to(self.device)

            # 6. Loop through and extract sentence embeddings
            # Don't propagate gradients
            with torch.no_grad():
                _, pooled_output = self.BERTmodel(input_ids=input_ids, token_type_ids=segment_ids, 
                                    attention_mask=input_mask, output_all_encoded_layers=False)

            sentence_embeddings.extend(pooled_output.detach().cpu().numpy())

        # 7. Set up claims field
        all_is_claim = [f.is_claim for f in features]
        
        # Set up instance dictionary
        instances = {}

        # 8. Save sentence embeddedings into dictionary
        for i in range(len(sentence_embeddings)):
            is_claim = all_is_claim[i]
            embedding = sentence_embeddings[i]
            if is_claim:
                instances['claim'] = embedding
                instances['evidences'] = []
            else:
                instances['evidences'].append(embedding)

        # 9. Load GraphNet pretrained checkpoint for prediction
        test_features, test_claims = load_bert_features_claim_inference(instances)
        print(f'***** ATTENTION WEIGHTS *****')
        self.logger.info(f'***** ATTENTION WEIGHTS *****')
        graphNet_model= GEAR(nfeat=self.feature_num, nins=self.evidence_num, nclass=self.num_class, 
                                    nlayer=self.graph_layers, pool=self.graph_pool, 
                                    device=self.device, loggerhandle=self.logger)
        checkpoint = torch.load(self.GEAR_model, map_location=self.device)
        graphNet_model.load_state_dict(checkpoint['model'])
        # Set Graph Net to inference
        graphNet_model.eval()

        # 10. Retrieve Graph Net output scores
        outputs, heatmap = [], []
        with torch.no_grad():
            test_features = test_features.to(self.device)
            test_claims = test_claims.to(self.device)
            graphNet_model = graphNet_model.to(self.device)
            outputs, heatmap = graphNet_model(test_features, test_claims)

        answer = {}
        answer["predicted_label"] = self.get_predicted_label(outputs.detach().cpu())
        print(f'>>>>>>> TIME TAKEN - GraphNET: {time.time()- start_time}')
        self.logger.info(f'>>>>>>> TIME TAKEN - GraphNET: {time.time()- start_time}')

        return answer, outputs, heatmap

def main():

    device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
    print(f'DEVICE Available: {device}')
    # Sample Inputs
    # input_claim = 'John is a Singaporean'
    # input_evidence = ['John is born in Mount Elizabeth hospital', 
    #                     'Mount Elizabeth hospital is located in Novena', 
    #                     'Novena is a district located in Singapore',
    #                     'People who are born in Singapore are Singaporeans']

    # input_claim = 'WhatsApp users do not require to pay when sending "Good Morning" messages!'
    # input_evidence = [ 
    #  'The message has recently been circulating among many WhatsApp users in Singapore',
    #  'The above message that has been "forwarded many times" is not real', 
    #  'WhatsApp remains a free messaging app and do not require payment details to be given prior to use']

    # input_claim = 'A bus driver has been arrested for careless driving following an accident at Loyang Avenue that
    # killed a 31-year-old cyclist.' input_evidence =  ["The cyclist who was killed along Loyang Avenue near the
    # T-junction with Pasir Ris Drive 1 on Friday, March 19 has been identified as a 31-year-old man from the
    # Philippines.", "The deceased man has been identified as German Gonzales from the Philippines.", "He has been
    # working in Singapore for two years as an aircraft technician.", "The victim and his wife have two sons,
    # aged eight and nine. Marie resides in the Philippines with the couple's children.", "Following the accident,
    # a bus driver, 63, was arrested for careless driving causing death."]

    input_claim = 'A nurse in the states has just had the vaccine and she died 8 hours later. Politicians in the West including Pfizer CEO have NOT Taken the vaccine.'
    input_evidence = ['No health care workers died after Alabama began administering COVID-19 vaccines on Tuesday',
    'Some online posts falsely claimed that a nurse had died after receiving the vaccine',
    'Alabama Department of Public Health officials checked with hospitals that administered the vaccine to confirm that the information was false',
    'The department released a statement on social media to combat the misinformation']

    cwd = os.path.dirname(__file__)

    graphNet = graphNetFC(cwd, device, feature_num, evidence_num, graph_layers, 
                            num_class, graph_pool, sequence_length)

    answer, outputs, heatmap = graphNet.predict(input_claim, input_evidence)
   
    print(answer)
    print('[SUPPORTS, REFUTES, NOT ENOUGH INFO]')
    print((np.array(outputs)))

    # Plot Attention Heat map to visualize
    ax = sns.heatmap(heatmap, linewidth=1.0, cmap="YlGnBu")
    ax.set(title='Attention Weights Heatmap')
    plt.savefig('2_layerER_Alabama.png', dpi=300)
    plt.show()


if __name__ == "__main__":
    main()




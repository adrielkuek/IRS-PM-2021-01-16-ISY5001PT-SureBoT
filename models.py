import math
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.nn import BatchNorm1d, Linear, ReLU

evidence_num = []

# Select CUDA is GPU is availble, else use CPU
# device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')

class SelfAttentionLayer(nn.Module):
    def __init__(self, nhid, nins, device, loggerHandle):
        super(SelfAttentionLayer, self).__init__()
        self.nhid = nhid
        self.nins = nins
        self.project = nn.Sequential(
            Linear(nhid, 64),
            ReLU(True),
            Linear(64, 1)
        )
        self.device = device
        self.logger = loggerHandle

    def forward(self, inputs, index, claims):
        tmp = None
        if index > -1:
            # idx = torch.LongTensor([index]).cuda()
            idx = torch.LongTensor([index]).to(self.device)
            own = torch.index_select(inputs, 1, idx)
            own = own.repeat(1, self.nins, 1)
            tmp = torch.cat((own, inputs), 2)
        else:
            claims = claims.unsqueeze(1)
            claims = claims.repeat(1, self.nins, 1)
            tmp = torch.cat((claims, inputs), 2)
        # before
        attention = self.project(tmp)
        weights = F.softmax(attention.squeeze(-1), dim=1)
        print(weights)
        self.logger.info(weights)
        evidence_num.append(weights.detach().cpu().numpy())
        outputs = (inputs * weights.unsqueeze(-1)).sum(dim=1)
        return outputs


class AttentionLayer(nn.Module):
    def __init__(self, nins, nhid, device, loggerHandle):
        super(AttentionLayer, self).__init__()
        self.nins = nins
        self.attentions = [SelfAttentionLayer(nhid=nhid * 2, nins=nins, device=device, loggerHandle=loggerHandle) for _ in range(nins)]

        for i, attention in enumerate(self.attentions):
            self.add_module('attention_{}'.format(i), attention)

    def forward(self, inputs):
        # outputs = torch.cat([att(inputs) for att in self.attentions], dim=1)
        outputs = torch.cat([self.attentions[i](inputs, i, None) for i in range(self.nins)], dim=1)
        outputs = outputs.view(inputs.shape)
        return outputs


class GEAR(nn.Module):
    def __init__(self, nfeat, nins, nclass, nlayer, pool, device, loggerhandle):
        super(GEAR, self).__init__()
        self.nlayer = nlayer

        self.attentions = [AttentionLayer(nins, nfeat, device, loggerhandle) for _ in range(nlayer)]
        self.batch_norms = [BatchNorm1d(nins) for _ in range(nlayer)]
        for i, attention in enumerate(self.attentions):
            self.add_module('attention_{}'.format(i), attention)

        self.pool = pool
        if pool == 'att':
            self.aggregate = SelfAttentionLayer(nfeat * 2, nins, device, loggerhandle)
        # self.index = torch.LongTensor([0]).cuda()
        self.index = torch.LongTensor([0]).to(device)

        self.weight = nn.Parameter(torch.FloatTensor(nfeat, nclass))
        self.bias = nn.Parameter(torch.FloatTensor(nclass))

        stdv = 1. / math.sqrt(self.weight.size(1))
        self.weight.data.uniform_(-stdv, stdv)
        self.bias.data.uniform_(-stdv, stdv)

    def forward(self, inputs, claims):
        for i in range(self.nlayer):
            inputs = self.attentions[i](inputs)

        if self.pool == 'att':
            inputs = self.aggregate(inputs, -1, claims)
        if self.pool == 'max':
            inputs = torch.max(inputs, dim=1)[0]
        if self.pool == 'mean':
            inputs = torch.mean(inputs, dim=1)
        if self.pool == 'top':
            inputs = torch.index_select(inputs, 1, self.index).squeeze()
        if self.pool == 'sum':
            inputs = inputs.sum(dim=1)

        evi_map = []
        for x in range(len(evidence_num)):
            intermediate_value = evidence_num[x][0]
            evi_map.append(list(intermediate_value))
 
        inputs = F.relu(torch.mm(inputs, self.weight) + self.bias)
        evidence_num.clear()
        return F.log_softmax(inputs, dim=1), evi_map

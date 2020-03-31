import os
os.environ["JAVA_HOME"] = "/usr/lib/jvm/jdk-11.0.2"
from pyserini.search import pysearch
from tqdm import tqdm
import numpy as np 
from transformers import BertForQuestionAnswering, BertTokenizer
import torch
import pandas as pd
import json

# Adds Java for Lucene
searcher = pysearch.SimpleSearcher('lucene-index-covid-2020-03-27/')

# Uses Lucene in order to find the words
query = 'What collaborations are happening within 2019-nCoV research community'
keywords = 'international, collaboration, global, coronavirus, novel coronavirus, sharing'

hits = searcher.search(query + ', ' + keywords)
n_hits = len(hits)

hit_dictionary = {}
for i in range(0, n_hits):
    doc_json = json.loads(hits[i].raw)
    idx = int(hits[i].docid)
    hit_dictionary[idx] = doc_json
    hit_dictionary[idx]['title'] = hits[i].lucene_document.get("title")
    hit_dictionary[idx]['authors'] = hits[i].lucene_document.get("authors")
    hit_dictionary[idx]['doi'] = hits[i].lucene_document.get("doi")

question_list = []
kw_list = []

question_list.append("What adjunctive or supportive methods can help patients")
kw_list.append("2019-nCoV, SARS-CoV-2, COVID-19, adjunctive, supportive")


# Load in model for transformers
tokenizer = BertTokenizer.from_pretrained('bert-large-uncased-whole-word-masking-finetuned-squad')
model = BertForQuestionAnswering.from_pretrained('bert-large-uncased-whole-word-masking-finetuned-squad')

def makeBERTSQuADPrediction(model, document, question):
    input_ids = tokenizer.encode(question, document)
    tokens = tokenizer.convert_ids_to_tokens(input_ids)
    sep_index = input_ids.index(tokenizer.sep_token_id)
    num_seg_a = sep_index + 1
    num_seg_b = len(input_ids) - num_seg_a
    segment_ids = [0]*num_seg_a + [1]*num_seg_b
    assert len(segment_ids) == len(input_ids)
    n_ids = len(segment_ids)
    #print(n_ids)
    if n_ids < 512:
        start_scores, end_scores = model(torch.tensor([input_ids]), 
                                 token_type_ids=torch.tensor([segment_ids]))
    else:
        #this cuts off the text if its more than 512 words so it fits in model space
        #need run multiple inferences for longer text. add to the todo
        start_scores, end_scores = model(torch.tensor([input_ids[:512]]), 
                                 token_type_ids=torch.tensor([segment_ids[:512]]))
    answer_start = torch.argmax(start_scores)
    answer_end = torch.argmax(end_scores)
    answer = tokens[answer_start]

    for i in range(answer_start + 1, answer_end + 1):
        if tokens[i][0:2] == '##':
            answer += tokens[i][2:]
        else:
            answer += ' ' + tokens[i]
            
    full_txt = ''
    
    for t in tokens:
        if t[0:2] == '##':
            full_txt += t[2:]
        else:
            full_txt += ' ' + t
            
    abs_returned = full_txt.split('[SEP] ')[1]
            
    ans={}
    ans['answer'] = answer
    
    if answer.startswith('[CLS]') or answer.endswith('[SEP]'):
        ans['confidence'] = -1.0
    else:
        confidence = torch.max(start_scores) + torch.max(end_scores)
        confidence = np.log(confidence.item())
        ans['confidence'] = confidence/(1.0+confidence)
    ans['start'] = answer_start
    ans['end'] = answer_end
    ans['abstract_bert'] = abs_returned
    return ans

def searchAbstracts(hit_dictionary, model, question):
    """searchAbstracts
    """
    abstractResults = {}
    for k,v in tqdm(hit_dictionary.items()):    
        abstract = v['abstract_full']
        emptyToken = -1
        if abstract:
            ans = makeBERTSQuADPrediction(model, abstract, question)
            confidence = ans['confidence']
            abstractResults[confidence]={}
            abstractResults[confidence]['answer'] = ans['answer']
            abstractResults[confidence]['start'] = ans['start']
            abstractResults[confidence]['end'] = ans['end']
            abstractResults[confidence]['abstract_bert'] = ans['abstract_bert']
            abstractResults[confidence]['idx'] = k
        else:
            abstractResults[emptyToken]={}
            abstractResults[emptyToken]['answer'] = []
            abstractResults[emptyToken]['start'] = []
            abstractResults[emptyToken]['end'] = []
            abstractResults[emptyToken]['abstract_bert'] = []
            abstractResults[emptyToken]['confidence'] = k
            emptyToken -= 1
    return abstractResults

def displayResults(hit_dictionary, answers, question, displayHTML=False, displayTable=True):
    
    confidence = list(answers.keys())
    confidence.sort(reverse=True)
    
    confidence = list(answers.keys())
    confidence.sort(reverse=True)
        
    for i,c in enumerate(confidence):
        if i < 3:
            if 'idx' not in  answers[c]:
                continue
            idx = answers[c]['idx']
            full_abs = answers[c]['abstract_bert']
            bert_ans = answers[c]['answer']
            split_abs = full_abs.split(bert_ans)
            sentance_beginning = split_abs[0][split_abs[0].rfind('.')+1:]
            if len(split_abs) == 1:
                sentance_end_pos = len(full_abs)
                sentance_end =''
            else:
                sentance_end_pos = split_abs[1].find('. ')+1
                if sentance_end_pos == 0:
                    sentance_end = split_abs[1]
                else:
                    sentance_end = split_abs[1][:sentance_end_pos]
                
            sentance_full = sentance_beginning + bert_ans+ sentance_end
            if c> 0.5:
                color = 'green'
            elif c > 0.25:
                color = '#CCCC00'
            else:
                color = 'red'
    
    pandasData = []
    print("the confidence is")
    print(confidence)
    for c in confidence:
        if c>0 and c <= 1:
            if 'idx' not in  answers[c]:
                continue
            rowData = []
            idx = answers[c]['idx']
            title = hit_dictionary[idx]['title']
            authors = hit_dictionary[idx]['authors'] + ' et al.'
            doi = '<a href="https://doi.org/'+hit_dictionary[idx]['doi']+'" target="_blank">source</a>'
            
            rowData += [idx]

            full_abs = answers[c]['abstract_bert']
            bert_ans = answers[c]['answer']
    print("The pandas data is")
    print(pandasData)
    return pandasData

def searchDatabase(question, keywords, lucene_database, BERTSQuAD_Model, displayTable=True, displayHTML=False):
    ## search the lucene database with a combination of the question and the keywords
    searcher = pysearch.SimpleSearcher(lucene_database)
    hits = searcher.search(question + '. ' + keywords)
    
    ## collect the relevant data in a hit dictionary
    hit_dictionary = {}
    for i in range(0, n_hits):
        doc_json = json.loads(hits[i].raw)
        idx = int(hits[i].docid)
        hit_dictionary[idx] = doc_json
        hit_dictionary[idx]['title'] = hits[i].lucene_document.get("title")
        hit_dictionary[idx]['authors'] = hits[i].lucene_document.get("authors")
        hit_dictionary[idx]['doi'] = hits[i].lucene_document.get("doi")
        
    ## scrub the abstracts in prep for BERT-SQuAD
    for idx,v in hit_dictionary.items():
        abs_dirty = v['abstract']
        # looks like the abstract value can be an empty list
        v['abstract_paragraphs'] = []
        v['abstract_full'] = ''

        if abs_dirty:
            # looks like if it is a list, then the only entry is a dictionary wher text is in 'text' key
            # looks like it is broken up by paragraph if it is in that form.  lets make lists for every paragraph
            # and a new entry that is full abstract text as both could be valuable for BERT derrived QA


            if isinstance(abs_dirty, list):
                for p in abs_dirty:
                    v['abstract_paragraphs'].append(p['text'])
                    v['abstract_full'] += p['text'] + ' \n\n'

            # looks like in some cases the abstract can be straight up text so we can actually leave that alone
            if isinstance(abs_dirty, str):
                v['abstract_paragraphs'].append(abs_dirty)
                v['abstract_full'] += abs_dirty + ' \n\n'
    ## Search collected abstracts with BERT-SQuAD
    answers = searchAbstracts(hit_dictionary, BERTSQuAD_Model, question)
    print("ANSWERSW IS")
    print(answers)
    ## display results in a nice format
    return displayResults(hit_dictionary, answers, question, displayTable=displayTable, displayHTML=displayHTML)




import os
os.environ["JAVA_HOME"] = "/usr/lib/jvm/jdk-11.0.2"
from pyserini.search import pysearch

import pandas as pd
from IPython.core.display import display, HTML
import json

N_HITS = 10
KEYWORDS = 'inter-sectorial, international, collaboration, global, coronavirus, novel coronavirus, sharing'

from transformers import DistilBertForQuestionAnswering, DistilBertTokenizer
import numpy as np
import torch

model = DistilBertForQuestionAnswering.from_pretrained('distilbert-base-uncased-distilled-squad')
tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased-distilled-squad')

document = "Victoria has a written constitution enacted in 1975, but based on the 1855 colonial constitution, passed by the United Kingdom Parliament as the Victoria Constitution Act 1855, which establishes the Parliament as the state's law-making body for matters coming under state responsibility. The Victorian Constitution can be amended by the Parliament of Victoria, except for certain 'entrenched' provisions that require either an absolute majority in both houses, a three-fifths majority in both houses, or the approval of the Victorian people in a referendum, depending on the provision."
input_ids = tokenizer.encode('Why is this strange thing here?')
start_positions = torch.tensor([1])
end_positions = torch.tensor([3])
start_scores, end_scores = model(torch.tensor([input_ids[:512]]))

def makeBERTSQuADPrediction(model, document, question):
    input_ids = tokenizer.encode(question, document)
    tokens = tokenizer.convert_ids_to_tokens(input_ids)
    sep_index = input_ids.index(tokenizer.sep_token_id)
    num_seg_a = sep_index + 1
    num_seg_b = len(input_ids) - num_seg_a
    segment_ids = [0]*num_seg_a + [1]*num_seg_b
    assert len(segment_ids) == len(input_ids)
    n_ids = len(segment_ids)
    # TODO: This was stolen from example. Figure out what start positions and 
    # end positions mean here.
    start_positions = torch.tensor([1])
    end_positions = torch.tensor([3])
    start_scores, end_scores = model(torch.tensor([input_ids[:512]]))
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
            
    ans = {}
    ans['answer'] = answer
    if answer.startswith('[CLS]') or answer.endswith('[SEP]'):
        ans['confidence'] = -1.0
    else:
        confidence = torch.max(start_scores) + torch.max(end_scores)
        confidence = np.log(confidence.item())
        ans['confidence'] = round(confidence/(1.0+confidence), 2)
    ans['start'] = answer_start
    ans['end'] = answer_end
    ans['abstract_bert'] = abs_returned
    return ans

document = "Victoria has a written constitution enacted in 1975, but based on the 1855 colonial constitution, passed by the United Kingdom Parliament as the Victoria Constitution Act 1855, which establishes the Parliament as the state's law-making body for matters coming under state responsibility. The Victorian Constitution can be amended by the Parliament of Victoria, except for certain 'entrenched' provisions that require either an absolute majority in both houses, a three-fifths majority in both houses, or the approval of the Victorian people in a referendum, depending on the provision."
q = 'Who enacted the constitution'
answer = makeBERTSQuADPrediction(model, document, q)

from tqdm import tqdm

def searchAbstracts(hit_dictionary, model, question):
    """Search through abstracts found in text
    """
    abstractResults = {}
    for k,v in tqdm(hit_dictionary.items()):
        
        abstract = v['abstract_full']
        emptyToken = -1
        if abstract:
            ans = makeBERTSQuADPrediction(model, abstract, question)
            confidence = ans['confidence']
            abstractResults[confidence] = {}
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

# answers = searchAbstracts(hit_dictionary, model, query)

# probs = list(answers.keys())
# probs.sort(reverse=True'.'
def displayResults(hit_dictionary, answers, question, displayHTML=False, displayTable=True):
    """Display Results
    """
    question_HTML = '<div style="font-family: Times New Roman; font-size: 28px; padding-bottom:28px"><b>Query</b>: '+ question +'</div>'
    confidence = list(answers.keys())
    confidence.sort(reverse=True)
    
    all_HTML_txt = '<div style="font-family: Times New Roman; font-size: 20px; padding-bottom:12px"><b>Highlights</b>:</div>'
    confidence = list(answers.keys())
    confidence.sort(reverse=True)
    
    HTML_list_text = '<div style="font-family: Times New Roman; font-size: 20px; padding-bottom:12px"> <ul style="list-style-type:disc;">' 
    
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
            HTML_list_text += '<li>'+sentance_full +"<font color='"+color+"'> score: " + str(c) +' </font> </li>'
    HTML_list_text += '</ul> </div>'
    
    all_HTML_txt += HTML_list_text
    
    htmlDir = os.path.join('.', 'htmlFiles')
    if not os.path.exists(htmlDir):
        os.mkdir(htmlDir)
    
    htmlFileName = os.path.join(htmlDir, question.replace(' ',''))+'.html'
    pandasData = []
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

            all_HTML_txt += '<div style="font-family: Times New Roman; font-size: 18px; padding-bottom:12px"><b>Document</b>: '+\
                 F'{authors} et al. ' +\
                 F'{title}. ' + \
                 doi +' Confidence: ' + F'{c}' +\
                 '</div>'

            
            full_abs = answers[c]['abstract_bert']
            bert_ans = answers[c]['answer']
            
            
            split_abs = full_abs.split(bert_ans)
            sentance_beginning = split_abs[0][split_abs[0].rfind('.')+1:]
            sentance_end_pos = split_abs[1].find('. ')+1
            if sentance_end_pos == 0:
                sentance_end = split_abs[1]
            else:
                sentance_end = split_abs[1][:sentance_end_pos]
                
            sentance_full = sentance_beginning + bert_ans+ sentance_end
            
            rowData += [sentance_full, c, doi]
            split_abs = full_abs.split(sentance_full)

            all_HTML_txt += '<div style="font-family: Times New Roman; font-size: 16px; padding-bottom:12px"><b>Abstract</b>: ' + \
                         split_abs[0] + " <font color='red'>"+sentance_full+"</font> "+split_abs[1]+'</div>'
            #rowData += ['<a href="http://'+htmlFileName+'" target="_blank">link</a>']
            pandasData.append(rowData)
    
    with open(htmlFileName, 'w') as f:
        f.write(all_HTML_txt)
    display(HTML(question_HTML))
    if displayTable:
        df = pd.DataFrame(pandasData, columns = ['Lucene ID', 'Text', 'Confidence', 'Source'])
        display(HTML(df.to_html(render_links=True, escape=False)))
    df = pd.DataFrame(pandasData, columns = ['Lucene ID', 'Text', 'Confidence', 'Source'])
    return df.to_dict('records')

def searchDatabase(question, keywords=KEYWORDS, pysearch=pysearch, lucene_database='lucene-index-covid-2020-03-27/', BERTSQuAD_Model=model, 
    displayTable=True, displayHTML=False):
    """Search Database
    """
    ## search the lucene database with a combination of the question and the keywords
    searcher = pysearch.SimpleSearcher(lucene_database)
    hits = searcher.search(question + '. ' + keywords)
    
    ## collect the relevant data in a hit dictionary
    hit_dictionary = {}
    for i in range(0, N_HITS):
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
    # print(answers)
    ## display results in a nice format
    return displayResults(hit_dictionary, answers, question, displayTable=displayTable, displayHTML=displayHTML)


print(searchDatabase(question="What is the new virus", 
    keywords=KEYWORDS, pysearch=pysearch, lucene_database='lucene-index-covid-2020-03-27/', BERTSQuAD_Model=model, 
    displayTable=True, displayHTML=False))

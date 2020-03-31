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
            pandasData.append(rowData)
    
    return pandasData

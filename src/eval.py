#!/usr/bin/env python3

import os, sys, json, time
from bleu_score import corpus_bleu, sentence_bleu, SmoothingFunction, NgramInst
from amr_graph import AMRGraph
import penman

import nltk
from nltk.util import ngrams
from nltk.corpus import stopwords
from rank_bm25 import BM25Okapi
from itertools import combinations

def read_amr(path):
    ids = []
    id_dict = {}
    amrs = []
    amr_str = ''
    lines = []
    for line in open(path,'r'):
        if line.startswith('#') or  line.startswith('s'):
            if line.startswith('# :: snt'):
                string = line.split("Sentence:")[1].strip()
                lines.append(string)
            if line.startswith('# ::id'):
                id = line.strip().split()[2]
                ids.append(id)
                id_dict[id] = len(ids)-1
            continue
        line = line.strip()
        if line == '':
            if amr_str != '':
                amrs.append(amr_str.strip())
                amr_str = ''
        else:
            amr_str = amr_str + line + ' '

    if amr_str != '':
        amrs.append(amr_str.strip())
        amr_str = ''
    return amrs, lines


def get_amrs(path, filter_ans=None):
    data = []
    lines,txts =  read_amr(path)
    for line, txt in zip(lines,txts):
        try:
            amr = AMRGraph(line.strip())
        except AssertionError:
            print(line)
            assert False
        if "Answer V4_Q1" not in txt and filter_ans:
            continue
        data.append(line)
        # print(penman.encode(penman.decode(line)))
    return data




def get_amr_ngrams(path, filter_ans=None):
    data = []
    lines,txts =  read_amr(path)
    for line, txt in zip(lines,txts):
        try:
            amr = AMRGraph(line.strip())
        except AssertionError:
            print(line)
            assert False
        if "Answer V4_Q1" not in txt and filter_ans:
            continue
        amr.revert_of_edges()
        ngrams = amr.extract_ngrams(3, multi_roots=True) # dict(list(tuple))


        concept_dict = {}
        if "2" in ngrams.keys():
            for subj, rel, obj in ngrams[2]:
                if subj not in concept_dict:
                    concept_dict[subj] = set()
                concept_dict[subj].add(obj)
            
            # Step 2: For each concept, get all pairs of its associated objects
            result = []
            for entities in concept_dict.values():
                entities = list(entities)
                if len(entities) > 1:
                    for a, b in combinations(entities, 2):
                        result.append((a, b))
                result.append((b, a))
            ngrams[4]=result
            # print(result)
    
        data.append(NgramInst(ngram=ngrams, length=len(amr.edges)))
        # print(penman.encode(penman.decode(line)))
    return data

def read_text(path):
    ids = []
    id_dict = {}
    lines = []
    for line in open(path,'r'):
        if line.startswith('#'):
            if line.startswith('# :: snt'):
                string = line.split("Sentence:")[1].strip()
                lines.append(string)
    return lines


def get_text_ngrams(path, filter_ans=None):
    data = []
    for line in read_text(path):
        if "Answer V4_Q1" not in line and filter_ans:
            continue
        ngram = {}
        ngram[1] = list(ngrams(line.split(),1))
        ngram[2] = list(ngrams(line.split(),2))
        ngram[3] = list(ngrams(line.split(),3))
        data.append(NgramInst(ngram=ngram,length=len(line.split())))
    return data

def get_string(path, filter_ans=None):
    data = []
    for line in read_text(path):
        if "Answer V4_Q1" not in line and filter_ans:
            continue
        data.append(line)
    return data

def get_max_index(data):
    max_value = max(data)
    return data.index(max_value)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('python this-script ans-file ref-file')
        sys.exit(0)
    print('loading ...')
    print(sys.argv)

    smoofunc = getattr(SmoothingFunction(), 'method3')

    # if len(sys.argv) == 4 and sys.argv[3] == "text":
    answers_txt = [x for x in get_text_ngrams(sys.argv[1])]
    golden_ref_txt = [[x] for x in get_text_ngrams(sys.argv[2],True)]

    answers_amr = [x for  x in get_amr_ngrams(sys.argv[1])]
    golden_ref_amr = [[x] for  x in get_amr_ngrams(sys.argv[2],True)]

    answers_amr_lines =  get_amrs(sys.argv[1])
    golden_ref_amr_lines =  get_amrs(sys.argv[2],True)

    # print(answers_amr[0])
    answers_string = [x for x in get_string(sys.argv[1])]
    golden_ref_string = [[x] for x in get_string(sys.argv[2],True)]

    print("length of TEXT |||   ans v.s. ref ")
    print(str(len(answers_txt)) +" v.s " + str(len(golden_ref_txt)))
    
    print("length of AMR |||   ans v.s. ref ")
    print(str(len(answers_amr)) +" v.s " + str(len(golden_ref_amr)))
    
    print("length of AMR lines|||   ans v.s. ref ")
    print(str(len(answers_amr_lines)) +" v.s " + str(len(golden_ref_amr_lines)))

    print("length of string |||   ans v.s. ref ")
    print(str(len(answers_string)) +" v.s " + str(len(golden_ref_string)))


    if len(sys.argv) == 4 and sys.argv[3] == "bm25":

        corpus = [x for x in get_string(sys.argv[1])]
        
        print(corpus)

        tokenized_corpus = [doc.split(" ") for doc in corpus]
        
        bm25 = BM25Okapi(tokenized_corpus)

        queries = [x for x in get_string(sys.argv[2],True)]
        for ref_indx, query in enumerate(queries):
            print()
            print("querying method: BM25")
            tokenized_query = query.split(" ")
            print("query: " + query)
            doc_scores = bm25.get_scores(tokenized_query).tolist()
            max_index = get_max_index(doc_scores)
            print("result: " + str(bm25.get_top_n(tokenized_query, corpus, n=1)))
            print("score: "+ str(doc_scores[max_index]/ sum(doc_scores)))
            print('evaluating ...')
            weights = (0.5, 0.35, 0.15)
            hy = answers_amr[max_index]
            ref = golden_ref_amr[ref_indx]
            
            corpus_bleu([ref],[hy], weights=weights, smoothing_function=smoofunc, auto_reweigh=True)

    else:


        print("processing answers from students:")
        print('evaluating ...')
        
        # st = time.time()
        # print('time:', time.time()-st, 'secs')
        for ref_indx, ref in enumerate(golden_ref_amr):
            for index_amr in range(len(answers_amr)):
            
                print("matching score")
                print("student:")
                hy = answers_string[index_amr]
                ref = golden_ref_string[ref_indx]
                print(ref)
                print("index")
                print(ref_indx)
                # for amr in golden_ref_amr_lines:
                #     print(penman.encode(penman.decode(amr)))
                print(penman.encode(penman.decode(golden_ref_amr_lines[ref_indx])))
                print("v.s.")
                print()
                print(hy)
                print(penman.encode(penman.decode(answers_amr_lines[index_amr])))
                print()
                
                weights = (0.5, 0.35, 0.05,0.1)
                hy = answers_amr[index_amr]
                ref = golden_ref_amr[ref_indx]
                if len(hy.ngram.keys()) == 3:
                    weights = (0.5, 0.35, 0.15)
                
                
                print(corpus_bleu([ref],[hy], weights=weights, smoothing_function=smoofunc, auto_reweigh=True))
                print()
                # weights = (0.5, 0.35, 0.15)
                # print("Surface TEXT:")
                # # weights = (0.34, 0.33, 0.34)
                # hy = answers_txt[index_amr]
                # ref = golden_ref_txt[ref_indx]
                # print(corpus_bleu([ref],[hy], weights=weights, smoothing_function=smoofunc, auto_reweigh=True))
             
    
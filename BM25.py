import argparse
import itertools
from math import log
import math
import os
import sys

import numpy as np
from parsers import QrelsParser, ResultsParser
import gzip
from BooleanAND import read_json
from IndexEngine import tokenize_line

def from_cmd():
    parser = argparse.ArgumentParser(description='BM25')
    parser.add_argument('--output-folder', required=True, help='Path to output folder with latimes')
    parser.add_argument('--queries-trec', required=True, help='Path to query trec topics')
    parser.add_argument('--qrel', required=True, help='Path to NIST qrels')
    parser.add_argument('--use-porter-stemmer', action='store_true', help='Use Porter Stemmer (optional)')
    parser.add_argument('--tune-k1-b', action='store_true', help='Tune K1 and b (optional)')

    
    try:
        cli = parser.parse_args()
    except Exception as e:
        print("An error occurred:", str(e))
        sys.exit(1)
    # except :
        sys.exit('Verify cmd line input')
    use_porter_stemmer = cli.use_porter_stemmer

   
    if use_porter_stemmer:
        run_tag = 'adestefaBM25stem'
    else:
        run_tag = 'adestefaBM25noStem'
    try:
        base_output_folder = cli.output_folder
    except:
        sys.exit('Verify base folder')

    try:
        queries_file = cli.queries_trec
    except:
        sys.exit('Verify queries file')


    try:
        qrel = QrelsParser(cli.qrel).parse()
    except:
        sys.exit('Verify Qrel file')

    read_metadata_into_memory(base_output_folder)

  # label all function parameters
    initalize_BM25(_run_tag = run_tag, _base_output_folder = base_output_folder, _queries_file = queries_file, _use_porter_stemmer = use_porter_stemmer, _inverted_index = inverted_index, _lexicon = lexicon)

    BM25_module()
    # BM25_term_at_a_time(query_line, query_id, number_of_results=1000, use_porter_stemmer = False):

# hyperparameters
k1 = 1.2
b = 0.75

doc_length = []
partial_scores = {}
output_file = []
# output_file = []
# results = []


def initalize_BM25(_run_tag, _base_output_folder, _inverted_index, _lexicon, _use_porter_stemmer=False, _queries_file = '', Number_of_docs_total = 0, average_doc_length = 0):
    global run_tag, base_output_folder, use_porter_stemmer, inverted_index, lexicon, queries_file
    run_tag = _run_tag
    base_output_folder = _base_output_folder
    queries_file = _queries_file
    use_porter_stemmer = _use_porter_stemmer
    # Number_of_docs_total = _Number_of_docs_total
    # average_doc_length = _average_doc_length
    inverted_index = _inverted_index
    lexicon = _lexicon

    count_average_doc_length(base_output_folder)



def count_average_doc_length(base_output_folder):

    doc_length_file = base_output_folder + '/doc_lengths.gz'

    with gzip.open(doc_length_file, 'rt') as gz_file:
        for line in gz_file:
            stripped_line = int(line.strip())
            doc_length.append(stripped_line)

    global Number_of_docs_total
    Number_of_docs_total = len(doc_length)
    global average_doc_length
    average_doc_length = sum(doc_length) / Number_of_docs_total

doc_no_map = []

def get_doc_internal_id_map(base_output_folder):

    with gzip.open(base_output_folder + '/metadata_mapping.gz','rt') as gzip_file:
        for line in gzip_file:
            docno = line.split(':')[1].strip()
            doc_no_map.append(docno)
    return doc_no_map

def get_k(doc_id : int):

    k = k1*((1-b) + b*doc_length[doc_id]/average_doc_length)

    return k


def calculate_term_BM25_score(term : str):

    term_id = lexicon.get(term)

    try:
        term_posting_list = inverted_index[term_id]
    except TypeError:
        term_posting_list = []

    number_of_term_docs = len(term_posting_list)/2


    for doc_id, term_freq in zip(term_posting_list[::2], term_posting_list[1::2]):

        k = get_k(doc_id)
        partial_BM25 = (term_freq/(k+term_freq)) * log((Number_of_docs_total - number_of_term_docs + 0.5) / (number_of_term_docs + 0.5))
        partial_scores[doc_id] = partial_scores.get(doc_id, 0.0) + partial_BM25

def BM25_term_at_a_time(query_line, query_id, number_of_results=1000, use_porter_stemmer = False):

    # tokenize query from index engine
    query_terms = []

    query_results = []

    # global output_file
    # output_file = []

    tokenize_line(query_terms,query_line, use_porter_stemmer)
    # zz check that query_terms gets reset each time or is global an issue
    for term in query_terms:
        calculate_term_BM25_score(term)

    # sort accumulator BM25
    BM25_score_sorted = dict(sorted(partial_scores.items(), key=lambda item: item[1], reverse=True))

    for rank, (doc_id, score) in enumerate(itertools.islice(BM25_score_sorted.items(), number_of_results)):

        # save into output file 
        query_results.append([query_id, 'Q0', doc_no_map[doc_id], rank+1, score, run_tag])

    partial_scores.clear()
    output_file.extend(query_results)

    return query_results

def read_metadata_into_memory(base_output_folder):

    # Inverted index: term id -> posting list
    # Posting list: doc id -> term freq
    global inverted_index
    inverted_index_file_path = base_output_folder +'\inverted_index.json'
    inverted_index = read_json(inverted_index_file_path)

    # term -> term id
    global lexicon
    lexicon_path = base_output_folder + '\lexicon.json'
    lexicon = read_json(lexicon_path)

    docno_to_id_map = get_doc_internal_id_map(base_output_folder)

    count_average_doc_length(base_output_folder)

    return inverted_index, lexicon, docno_to_id_map

def save_trec_results(output_file_path, data):

    directory = os.path.dirname(output_file_path)

    # Check if the directory exists, and create it if it doesn't
    if not os.path.exists(directory):
        os.makedirs(directory)

    with open(output_file_path, 'wt') as file:

        for row in data:
            for item in row:
                file.write(str(item) + ' ')
            file.write('\n')

def BM25_module():
    # zz remove?
    query_topicID = 0
    # queries_file = ''
    with open(queries_file,'rt') as file:
        for line in file:
            # get topic id then go next
            if (query_topicID == 0):
                query_topicID = line.removesuffix('\n')
                continue

            BM25_term_at_a_time(query_line = line, query_id = query_topicID)

            query_topicID = 0
    
    if use_porter_stemmer:
        save_trec_results(base_output_folder + '/hw4-bm25-stem-adestefa.txt', output_file)
    else:
        save_trec_results(base_output_folder + '/hw4-bm25-baseline-adestefa.txt', output_file)



if __name__ == '__main__':
    
    from_cmd()
    

    
    # initalize_BM25()
    # BM25_module()

import csv
import gzip
import json
from pathlib import Path
import sys
from IndexEngine import tokenize_line

def read_json(filepath):
    with open(filepath, 'r') as json_file:
        return json.load(json_file)

def booleanAND(inverted_index, lexicon, query):

    old_results = []
    new_results = []

    first_word = True

    for word in query:
        old_results = new_results
        new_results = []

        term_id = lexicon.get(word)

        # if word not in lexicon, skip word (Campuswire 68)
        if (term_id is None):
            continue
        
        if (first_word):
            first_word = False
            new_results.extend(inverted_index[term_id])
            continue # if in lexicon must be in at least 1 doc
        
        # if there are no matching values
        elif (old_results == []):
            return []

        results_idx = 0
        ii_index = 0

        while (results_idx < len(old_results) and ii_index < len(inverted_index[term_id])):
            
            # Intersect
            if (old_results[results_idx] == inverted_index[term_id][ii_index]):
                new_results.append(old_results[results_idx])
                new_results.append(old_results[results_idx+1])
                results_idx += 2
                ii_index += 2
            
            elif (old_results[results_idx] < inverted_index[term_id][ii_index]):
                results_idx += 2
            else:
                ii_index += 2

    return new_results

def main():

    if len(sys.argv) != 4:
        sys.exit('Please enter 3 args')

    index_directory = sys.argv[1] 
    queries_path =  sys.argv[2]
    
    search_output_path =  sys.argv[3]

    index_path = index_directory+'\inverted_index.json'

    if (not Path(index_directory).exists()):
        sys.exit('Please enter the correct index_directory file path')
    
    if (not Path(queries_path).exists()):
        sys.exit('Please enter the correct queries file path')
    
    if (Path(search_output_path).exists()):
        sys.exit('The desired results output path already exists')

    
    lexicon_path = index_directory + '\lexicon.json'
    metadata_mapping_path = index_directory + '\metadata_mapping.gz'

    if (not Path(lexicon_path).exists()):
        sys.exit('The desired lexicon path does not exist')

    if (not Path(metadata_mapping_path).exists()):
        sys.exit('The desired metadata mapping path does not exist')
   
    topicID = 0

    # read index into memory (make dict again)
    inverted_index = read_json(index_path)

    with open(lexicon_path, 'r') as file:
        lexicon = json.load(file)

    metadata_mapping = []
    with gzip.open(metadata_mapping_path,'rt') as gzip_file:
        for line in gzip_file:
            metadata_mapping.append(line.split(':')[1].strip())


    output_file = []

    with open(queries_path,'rt') as file:
        for line in file:
            # get topic id then go next
            if (topicID == 0):
                topicID = line.removesuffix('\n')
                continue
            
            query = []
            tokenize_line(query,line)

            
            matched_posting_list = booleanAND(inverted_index, lexicon, query)
            matched_docs = matched_posting_list[0::2]
            rank = 0
            score = len(matched_docs)

            for doc in matched_docs:
                rank += 1
                score -= 1
                docno = metadata_mapping[doc]

                output_file.append([topicID, 'Q0', docno, rank, score, 'adestefa'])

            topicID = 0

    with open(search_output_path,'wt') as file:
        for row in output_file:
            for item in row:
                file.write(str(item) + ' ')
            file.write('\n') 

if __name__ == "__main__":
    main()

import csv
from datetime import datetime
import json
import re
import sys
import os
from pathlib import Path
import gzip
from collections import Counter
from PorterStemmer import PorterStemmer
import argparse


# py IndexEngine.py .\latimes.gz .\OutputFolder

# https://stackoverflow.com/questions/3368969/find-string-between-two-substrings
def find_between(s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return "NOTHING_FOUND"

# convert DOCNO to date 
def get_date(DOCNO):

    date_str = DOCNO[2:8]
    date_format = '%m%d%y'

    date_obj = datetime.strptime(date_str, date_format)

    return date_obj

def tokenize_line(alphanumeric_list, line, use_porter_stemmer = False):

    words = line.split()
    for word in words:
        if not word.startswith('<') and not word.endswith('>'):
            
            cleaned_text = re.sub(r'[^a-zA-Z0-9]', '',  word.lower())
            alphanumeric_word = re.findall(r'\w+', word.lower())


            if use_porter_stemmer:
            
                # alphanumeric_list
                p = PorterStemmer()
                stemmed_words = [p.stem(w, 0, len(w)-1) for w in alphanumeric_word]
                alphanumeric_list.extend(stemmed_words)
            
            else:
                alphanumeric_list.extend(alphanumeric_word)

    return alphanumeric_list
                

def update_lexicon(lexicon, doc_term_list):

    current_id = len(lexicon)

    for term in doc_term_list:
        # Check if the term is already in the lexicon
        if term not in lexicon:
            lexicon[term] = current_id
            current_id += 1

# recieves the lexicon map, all_doc_text, and doc id. Creates a map of freq of that term in the document
def update_inverted_index(inverted_index, lexicon, doc_internal_id, doc_term_list):

    inverted_index.extend([[] for _ in range(len(lexicon) - len(inverted_index))])

    # find freq of term in wordlist
    word_freq = Counter(doc_term_list)

    for word, frequency in word_freq.items():

        term_id = lexicon.get(word)
        #ensure the term id exists in the lexicon
        if term_id is not None:

            inverted_index[term_id].extend([doc_internal_id, frequency])

def gz_save_to_disk(filepath, my_list, Optional_is_numbers_only = None):
    
    with gzip.open(filepath, 'wt') as gz_file:
        if (Optional_is_numbers_only):
            gz_file.writelines(f"{x}\n" for x in my_list)
        else:
            gz_file.write('\n'.join(my_list))

def json_save_to_disk(filepath, list):
    with open(filepath, 'w') as file:
        json.dump(list, file)


def main():
    # ensure correct number of args were entered 
    # if len(sys.argv) != 3:
    #     sys.exit('Please enter 2 args')

    # latimes_file_path = sys.argv[1] 
    # base_output_file_path =  sys.argv[2] 
    
    parser = argparse.ArgumentParser(description='IndexEngine')    
    parser.add_argument('--latimes', required=True, help='Path to query latimes file')
    parser.add_argument('--output-folder', required=True, help='Path to output folder with latimes')
    parser.add_argument('--use-porter-stemmer', action='store_true', help='Use Porter Stemmer')
    
    try:
        cli = parser.parse_args()
    except:
        sys.exit('Verify cmd line input')

    latimes_file_path = cli.latimes
    base_output_file_path = cli.output_folder
    use_porter_stemmer = cli.use_porter_stemmer


    # latimes_file_path = '.\latimes_test.gz'
    # base_output_file_path = '.\OutputFolder_test'
 
    if (not Path(latimes_file_path).exists()):
        sys.exit('Please enter the correct latimes file path')

    try:
        os.mkdir(base_output_file_path)
    except FileExistsError:
        sys.exit("Folder %s already exists" % base_output_file_path)

    inverted_index_file_path = base_output_file_path +'\inverted_index.json'
    doc_lengths_file_path = base_output_file_path +'\doc_lengths.gz'
    lexicon_file_path = base_output_file_path + '\lexicon.json'

    date_file_path = 'EMPTY'
    docno = "EMPTY"

    record_whole_headline = False
    whole_headline = "EMPTY"
    headline = "EMPTY"

    docno_date = 0

    doc_internal_id = -1
    current_document_lines = []

    metadata_mapping = []
    header_text = []

    outputfile = ''
    date_file_path = ''

    record_start_tags = ['<TEXT>', '<HEADLINE>', '<GRAPHIC>']
    record_end_tags = ['</TEXT>', '</HEADLINE>', '</GRAPHIC>']
    record_text_for_token = False
    all_doc_text = []
    doc_lengths = []
    lexicon = dict()
    inverted_index = []

    with gzip.open(latimes_file_path,'rt') as gzip_file:
        for line in gzip_file:

            # record each line to be output once document is fully read in
            current_document_lines.append(line)

            # increment at each new document
            if ('<DOC>' in line):
                doc_internal_id += 1

            # when document is finished, save files (EOD)
            elif ('</DOC>' in line):
                
                outputfile =  str(date_file_path) + '/' + str(docno) + '.gz'
                with gzip.open(outputfile, 'wt', encoding='utf-8') as gz_file:
                    # remove extra newlines
                    headline = re.sub(r'\n+', ' ', headline.strip())
                    
                    header_text.append('docno: ' + docno)
                    header_text.append('internal id: ' + str(doc_internal_id))
                    header_text.append('date: ' + str(docno_date.strftime('%B %#d, %Y')))
                    header_text.append('headline: ' + headline.strip())

                    gz_file.write(''.join(current_document_lines))
                        
                current_document_lines = []
                headline = "EMPTY"
                
                doc_lengths.append(len(all_doc_text))

                update_lexicon(lexicon, all_doc_text)
                update_inverted_index(inverted_index, lexicon, doc_internal_id, all_doc_text)

                all_doc_text = []

            # find the DOCNO between the tags
            elif ('<DOCNO>' in line):
                docno = find_between(line,'<DOCNO>','</DOCNO>')
                docno = docno.strip()
                docno_date = get_date(docno)

                # save metadata file at the end of processing all the documents for that date
                if (Path(date_file_path).exists() and docno.endswith("-0001") and doc_internal_id > 1 ):
                    
                    outputfile =  str(date_file_path) + '/metadata.gz'
                    with gzip.open(outputfile, 'wt', encoding='utf-8') as gz_file:
                        saved_header_lines =  '\n'.join(header_text) 
                        gz_file.write(saved_header_lines)

                    header_text = []

                # Save mapping for metadata, id:docno
                metadata_mapping.append(str(doc_internal_id) + ':' + str(docno))

                # Create folder structure (if doesnt already exist) based on date
                date_file_path = base_output_file_path + '/' + docno_date.strftime('%y/%B/%#d/')
                date_file_path = Path(date_file_path)

                date_file_path.mkdir(parents=True, exist_ok=True)
            
            # record at the start of the headline tag
            elif ('<HEADLINE>' in line):
                record_whole_headline = True
                headline = 'EMPTY'
                whole_headline = 'EMPTY'

            # record between headline tags
            if (record_whole_headline):
                whole_headline = whole_headline + line

                # find the headline between the headline and page tags
                if ('</HEADLINE>' in whole_headline):
                    record_whole_headline = False
                    headline = find_between(whole_headline,'<P>','</P>')

            if any(term in line for term in record_start_tags):
                record_text_for_token = True
                
            elif any(term in line for term in record_end_tags):
                record_text_for_token = False

                
            if (record_text_for_token):
                
                tokenize_line(all_doc_text, line, use_porter_stemmer=use_porter_stemmer)            

    # Save final document
    if (Path(date_file_path).exists()):
            outputfile =  str(date_file_path) + '/metadata.gz'
            
            gz_save_to_disk(outputfile, header_text)

    # save doc length
    gz_save_to_disk(doc_lengths_file_path, doc_lengths, True)

    # save inverted index
    json_save_to_disk(inverted_index_file_path, inverted_index)

    # save lexicon
    json_save_to_disk(lexicon_file_path, lexicon)

    # save the metadata file
    gz_save_to_disk(base_output_file_path + '/metadata_mapping.gz', metadata_mapping)

   


if __name__ == "__main__":
    main()

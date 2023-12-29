import argparse
from pathlib import Path
import re
import sys
import time
from BM25 import BM25_term_at_a_time, initalize_BM25, tokenize_line, read_metadata_into_memory as bm25_read_metadata_into_memory
from GetDoc import get_metadata, print_document,get_text_between_tags  

def read_metadata_into_memory():
    global inverted_index, lexicon, id_to_docno_map
    inverted_index, lexicon, id_to_docno_map = bm25_read_metadata_into_memory(base_output_folder)
    initalize_BM25(_run_tag = 'S_E', _inverted_index = inverted_index, _lexicon = lexicon, _base_output_folder = base_output_folder, )

def remove_between_tags(text, start_tag):

    end_tag = start_tag.replace('<', '</')

    pattern = re.compile(f'{re.escape(start_tag)}\s*.*?\s*{re.escape(end_tag)}', re.DOTALL)

    cleaned_text = re.sub(pattern, '', text)

    return cleaned_text

def remove_tags(text, start_tag):
    end_tag = start_tag.replace('<', '</')

    pattern = re.compile(f'{re.escape(start_tag)}|{re.escape(end_tag)}', re.DOTALL)
    
    cleaned_text = re.sub(pattern, '', text)

    return cleaned_text

def split_into_sentences(text):

    # remove unneeded tags and text within those tags
    for tag in ['<HEADLINE>', '<BYLINE>', '<DOCID>', '<DOCNO>', '<DATE>', '<LENGTH>', '<TYPE>', '<SECTION>', '<DATELINE>']:
        text =  remove_between_tags(text, tag)

    for tag in ['<GRAPHIC>', '<P>', '<TEXT>', '<SUBJECT>', '<DOC>']:
        text =  remove_tags(text, tag)


    # Use regular expression to split text into sentences
    sentences = re.split(r'(?<=[.!?])', text)
    
    # Remove empty strings and leading/trailing whitespaces from the list
    sentences = [sentence.strip() for sentence in sentences ]
    # print(sentences, end="\n")
    return sentences

def get_sentence_rank(sentences, query):
    tokenized_sentences = []

    for sentence in sentences:
        tokenized_sentences.append(' '.join(tokenize_line([],sentence)))

    sentence_to_score_map = {}
    # [L, C, D, K, H]
    split_query = query.split()
    for line_number, sentence in enumerate(tokenized_sentences):
        L = C = D = K = H = 0
        
        L = max(0, 2-line_number)
        
        # C = number of query terms in sentence
        for word in split_query:
            if word in sentence:
                C += 1

        # D = number of distinct query terms in sentence
        D = len(set(query.split()) & set(sentence.split()))

        # K is longest continuous run of query terms in sentence
        unique_query_terms = set(split_query)
        sentence_terms = sentence.split()

        current_run = 0
        longest_run = 0

        for term in sentence_terms:
            if term in unique_query_terms:
                # current_run.append(term)
                current_run += 1
            else:
                # If the current run is longer than the previous longest run, update it
                # longest_run = max(longest_run, current_run, key=len)
                longest_run = max(longest_run, current_run)
                # current_run = []
                current_run = 0

        # Check for the last run in case it extends to the end of the sentence
        longest_run = max(longest_run, current_run)
        K = longest_run

        # Once the L = C = D = K = H values are calculated, sum them up to get the sentence score
        # as mentioned when asked Prof, we can use 1:1 ratio (no weights)
        sentence_to_score_map[line_number] = L + C + D + K + H

    return sentence_to_score_map


def query_snippet(docno, query):
    

    # get doc return raw text only
    # raw_text = get_raw_text(base_output_folder, docno)
    
    raw_text = get_text_between_tags(base_output_folder, docno, '<TEXT>')
    if len(raw_text) == 0:
        raw_text = get_text_between_tags(base_output_folder, docno, '<GRAPHIC>')

    sentences = split_into_sentences(raw_text)
    
    # remove sentences under 5 words
    # original_sentences = sentences.copy()

    # for sentence in sentences:
    #     if len(sentence.split()) < 5:
    #         sentences.remove(sentence)
    
    original_sentences = sentences.copy()

    sentence_rank = get_sentence_rank(sentences, query)

    # sort sentences by rank descending
    sentence_rank_sorted = dict(sorted(sentence_rank.items(), key=lambda item: item[1], reverse=True))

    # # print("####################################### POSSIBLE QUERIES #######################################\n")
    # for key_linenumber in list(sentence_rank_sorted.keys()):
    #     if sentence_rank_sorted[key_linenumber] >= zzHighest_score:
    #         print(f"possible snippet: {original_sentences[key_linenumber]}")

    top_sentences = []
    # get top 2 sentences
    for key_linenumber in list(sentence_rank_sorted.keys())[:2]:
        top_sentences.append(original_sentences[key_linenumber])

    # top_sentences_merged = []
    # for sentence in top_sentences:
    #     top_sentences_merged.extend(sentence)

    top_sentences_str = ' '.join(top_sentences)

    return top_sentences_str

     
def get_user_input():
    while True:

        try:
            user_input = input("Please enter your query: ")
            start_time = time.time()

            user_input = user_input.lower()
            user_input = ' '.join(tokenize_line([], user_input))

            top_results = BM25_term_at_a_time(query_line = user_input, query_id = 0, number_of_results=10)
            # tokenize query
            # tokenize_line()
            # print()
            result_docno = {}

            # ensure there are enough results
            if len(top_results) == 0:
                print("No results found for that query")
            elif len(top_results) < 10:
                print("There are only", len(top_results), "results for this query")

            # [query_id, 'Q0', doc_no_map[doc_id], rank+1, score, run_tag])
            else:
               print(f"\nResults:")

            for query_id, Q_naut, docno, rank, score, runtag in top_results:
                
                result, docno, internal_id, date, headline = get_metadata(docno, base_output_folder)
                #query snippet is first 
                snippet = query_snippet(docno, user_input)

                # If a document does not have a headline, simply use the first 50 characters from the snippet and
                # add an ellipse. For example, LA010189-0007 at rank 5
                if headline == 'EMPTY':
                    headline = snippet[:50] + '...'

                result_docno[rank] = docno

                print(f"{rank}. {headline} ({date})")
                print(f"{snippet} ({docno})\n")
                # print(f"Score: {score}\n")
            elapsed_time = time.time() - start_time
            print(f"Query time: {elapsed_time:.2f} seconds\n")

        except Exception as e:
            print("An error occurred:", str(e))
            sys.exit(1)

        while True:
            try:

                user_input = input("Enter the rank of a document to view, 'N' for new query, or 'Q' to quit: ")
                # start_time = time.time()
                if user_input.isdigit():
                    rank = int(user_input)

                    print(f"\nDocument {rank} selected:")
                    print_document(base_output_folder, result_docno[rank])
                    break

                        
                    # Your code to display the full document based on the rank here
                elif user_input.upper() == 'N':
                    # Go back to step B and prompt for a new query
                    break
                elif user_input.upper() == 'Q':
                    # return  # Exit the program
                    sys.exit(0)
                else:
                    print("Invalid input. Please try again.")
                
            except Exception as e:
                print("An error occurred:", str(e))


if __name__ == "__main__":

    global base_output_folder
    base_output_folder = '.\OutputFolder'
    parser = argparse.ArgumentParser(description='IndexEngine')    
    parser.add_argument('--output-folder', required=True, help='Path to query latimes file')
    
    try:
        cli = parser.parse_args()
        base_output_folder = cli.output_folder

        if (not Path(base_output_folder).exists()):
            sys.exit('Please verify output folder exists')

    except Exception as e:
        print("Please verify output folder", str(e))
        sys.exit(1)

    print("Reading metadata into memory...")
    read_metadata_into_memory()
    get_user_input()





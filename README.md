# LA Times Search Engine

The Los Angeles Times (LA Times) Search Engine matches user queries with related LA Times articles.

The search engine is comprised of an Indexer, Lexicon, Ranker, Snippet Generator, Metadata Store, and Query Front End. The search engine is designed to efficiently manage and retrieve information from LA Times data, providing a user-friendly interface enhanced with natural language processing capabilities for intuitive querying.

Due to copyright restrictions, the LA Times data is unable to be uploaded or shared as part of this repository.

# General Setup

Install Python: https://code.visualstudio.com/docs/python/python-tutorial

Install requirements: `pip install -r requirements.txt`

## Search Engine
usage: search_engine.py [-h] --output-folder OUTPUT_FOLDER

Example:  
`py .\search_engine.py --output-folder OutputFolder`

Where output folder is from the Index Engine program

# Programs:

## Index Engine

usage: IndexEngine.py [-h] --latimes LATIMES --output-folder OUTPUT_FOLDER [--use-porter-stemmer]

Example:
```py IndexEngine.py --latimes latimes.gz --output-folder .\OutputFolderPorter```

Note: the '#' character used to format the date is Windows only. Linux/MacOS should replace it with '-'

## BM25

usage: bm25.py [-h] --output-folder OUTPUT_FOLDER --queries-trec QUERIES_TREC --qrel QREL [--use-porter-stemmer] [--tune-k1-b]

Example:
```py BM25.py --output-folder ./OutputFolder --queries-trec ./queries.txt --qrel ./qrels/LA-only.trec8-401.450.minus416-423-437-444-447.txt```


## Evaluate Engine

usage: Evaluate_engine.py [-h] --qrel QREL --results RESULTS --max-results MAX_RESULTS --eval-method EVAL_METHOD

Example:  
```py evaluate_engine.py --qrel .\qrels\LA-only.trec8-401.450.minus416-423-437-444-447.txt --results .\OutputFolder\hw4-bm25-baseline-adestefa.txt --max-results 1000 --eval-method ap```

## Get Doc

usage: GetDoc.py [-h] --output-folder OUTPUT_FOLDER --identifier {docno,id} --value VALUE

Example:
`py GetDoc.py --output-folder "./OutputFolder" --identifier  "id", --value "0"`  
or  
`py GetDoc.py --output-folder "./OutputFolder" --identifier  "docno", --value "LA010189-0018"`

## Acknowledgements
This program utilizes code written by Nimesh Ghelani based on code by Mark D. Smucker, including parsers, Qrels, and Results. It also uses Porter Stemmer code written by Vivake Gupta.

import argparse
import gzip
import re
import sys
from pathlib import Path
from datetime import datetime

def format_metadata(result):

    for line in result:
        if 'docno' in line:
            docno = line.split(':')[1].strip()
        elif 'internal id' in line:
            internal_id = line.split(':')[1].strip()
        elif 'date' in line:
            date = line.split(':')[1].strip()
        elif 'headline' in line:
            # headline = line.split(':')[1:].strip()
            headline = line.replace("headline: ", '')
        else:
            # zz confirm
            sys.exit('Please ensure the metadata in the file you are searching for is correct')

    return docno, internal_id, date, headline

def get_metadata(docno, base_path):
    result = []

    docno_date = get_date(docno)
    date_file_path = base_path + '/' + docno_date.strftime('%y/%B/%#d/') 

    if (not Path(date_file_path).exists()):
        sys.exit('Please ensure the file you are searching for exists')


    with gzip.open(Path(date_file_path + 'metadata.gz'),'rt') as gzip_file:
        found_docno = False
        for line in gzip_file:
            if found_docno and("docno" in line):
                break

            if (docno in line or found_docno):
                found_docno = True
                result.append(line.strip())

    docno, internal_id, date, headline = format_metadata(result)
    
    return result, docno, internal_id, date, headline

def get_date(DOCNO):

    try:
        date_str = DOCNO[2:8]
        date_format = '%m%d%y'
        date_obj = datetime.strptime(date_str, date_format)
    except:
        sys.exit('Please ensure the file you are searching for exists')

    return date_obj

def get_raw_text(base_path, docno):
    docno_date = get_date(docno)
    date_file_path = base_path + '/' + docno_date.strftime('%y/%B/%#d/')
    # read file
    raw_text = []
    with gzip.open(Path(date_file_path + docno + '.gz'),'rt') as gzip_file:
        for line in gzip_file:
            # print(line, end="")
            raw_text.append(line)
    return raw_text

def get_text_between_tags(base_path, docno, start_tag):
    docno_date = get_date(docno)
    date_file_path = base_path + '/' + docno_date.strftime('%y/%B/%#d/')
    # read file
    end_tag = start_tag.replace('<', '</')
    raw_text = []
    with gzip.open(Path(date_file_path + docno + '.gz'),'rt') as gzip_file:
        for line in gzip_file:
            # print(line, end="")
            raw_text.append(line)

    raw_text = ''.join(raw_text).replace('\n', '')

    pattern = re.compile(f'{re.escape(start_tag)}\s*.*?\s*{re.escape(end_tag)}', re.DOTALL)
    raw_text = re.findall(pattern, raw_text)
    raw_text_str = ''.join(raw_text)
    return raw_text_str

def print_document(base_path, docno):
    raw_text = get_raw_text(base_path, docno)
    for line in raw_text:
        print(line, end="")

def print_doc_and_metadata(base_output_folder, identifier, value):

    base_path = base_output_folder

    if (not Path(base_path).exists()):
        sys.exit('Please enter the correct base path (no slash at end)')

    docno = -1
    internal_id = 0

    # assign docno from args
    if (identifier == 'docno'):
        docno = value

    # assign internal id from args
    elif (identifier == 'id'):
        internal_id = value

        # zz see if fast enough, else pass it in as a parameter when reading in the metadata
        # need to find corresponding docno
        with gzip.open(base_path + '/metadata_mapping.gz','rt') as gzip_file:
            for line in gzip_file:
                # print (line.split(':')[0])
                if (internal_id == line.split(':')[0]):
                    docno = line.split(':')[1].strip()
                    break

    else:
        sys.exit('Please verify args entered correctly')

    # get the file path from the date
    if (docno == -1):
        sys.exit('Please ensure the file you are searching for exists')
    # else:
    #     docno_date = get_date(docno)
    #     date_file_path = base_path + '/' + docno_date.strftime('%y/%B/%#d/') 

    # if (not Path(date_file_path).exists()):
    #     sys.exit('Please ensure the file you are searching for exists')


    # zz see if fast enough, else pass it in as a parameter when reading in the metadata
    # read related metadate header:
    metadata, _, _, _, _ = get_metadata(docno, base_path)
    docno_date = get_date(docno)
    date_file_path = base_path + '/' + docno_date.strftime('%y/%B/%#d/')
    
    for m in metadata:
        print(m)

    print("raw document:")
    print_document(base_path, docno)
    # raw_text = get_raw_text(base_path, docno)
    # for line in raw_text:
    #     print(line, end="")
    # # read file
    # with gzip.open(Path(date_file_path + docno + '.gz'),'rt') as gzip_file:
    #     for line in gzip_file:
    #         print(line, end="")


def from_cmd():

    try:    
        parser = argparse.ArgumentParser(description='GetDoc')
        parser.add_argument('--output-folder', required=True, help='Path to output folder with latimes data')
        parser.add_argument('--identifier', required=True, choices=['docno', 'id'], help='Choose either "docno" or "id" as the identifier')
        parser.add_argument('--value', required=True, help='Specify the value for the identifier (docno or id)')

        cli = parser.parse_args()
        base_output_folder = cli.output_folder
        identifier = cli.identifier
        value = cli.value

    except argparse.ArgumentError as e:
        print(f"Error: {e}")
        parser.print_help()

    print_doc_and_metadata(base_output_folder, identifier, value)


if __name__ == '__main__':
    from_cmd()

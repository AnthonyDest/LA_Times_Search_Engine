
import argparse

import numpy as np
from parsers import QrelsParser, ResultsParser
import sys
import math
# py .\ExampleCode\example.py --qrel .\qrels\LA-only.trec8-401.450.minus416-423-437-444-447.txt --results .\results-files\student1.results --max-results 1000
# Author: Nimesh Ghelani based on code by Mark D. Smucker

# py .\ExampleCode\evaluate_engine.py --qrel .\qrels\LA-only.trec8-401.450.minus416-423-437-444-447.txt --results .\results-files\student1.results --max-results 1000 --eval-method ap

parser = argparse.ArgumentParser(description='todo: insert description')
parser.add_argument('--qrel', required=True, help='Path to qrel')
parser.add_argument('--results', required=True, help='Path to file containing results')
parser.add_argument('--max-results', type=int, required=True, help='')
parser.add_argument('--eval-method', required=True, help='\'ap\' for Average Precision, \'P_10\' for P@10, \'ndcg_cut_10\' for NDCG@10, \'ndcg_cut_1000\' for NDCG@1000')

try:
    cli = parser.parse_args()
except:
    sys.exit('Verify cmd line input')
try:
    qrel = QrelsParser(cli.qrel).parse()
# except QrelsParser.QrelsParseError as e:
except:
    sys.exit('Verify Qrel file')
    # sys.exit(e)
try:    
    results = ResultsParser(cli.results).parse()
# except ResultsParser.ResultsParseError as e:
except:
    # sys.exit(e)
    sys.exit('Verify Results file')

try:
    max_results = cli.max_results
except:
    sys.exit('Verify max results')

try:
    eval_method = cli.eval_method
except:
    sys.exit('Verify eval method')

query_ids = sorted(qrel.get_query_ids())

def average_precision():
    meanAP = 0
    for query_id in query_ids:
            try:
                query_result = sorted(results[1].get_result(query_id))
            except TypeError:
                #  sys.stderr.write(query_id+' has no results, but it exists in the qrels.\n')
                print(f"ap  {query_id}  0.0000")
                continue

            # Size of QRELS is number of max docids in each query
            total_relevant_docs = len(qrel.query_2_reldoc_nos[query_id])
            
            idx = 0
            found_docs_qty = 0
            precision = []
            for result in query_result[:max_results]:
                idx += 1
                relevance = qrel.get_relevance(query_id, result.doc_id)
                # if statement is an implicity 1 or 0
                if (relevance > 0):
                    if (idx <= max_results):
                        found_docs_qty += 1
                        precision.append(found_docs_qty / idx)

            # sum of all P@i
            precision_sum = 0
            average_precision = 0
            for p in precision:
                precision_sum += p
            
            average_precision = precision_sum / total_relevant_docs
            
            print(f"ap  {query_id}  {average_precision:.4f}")
            meanAP += round(average_precision,4)

    meanAP /= 45
    print(f"meanAP: {meanAP:.3f}")

def p_at_10():
    meanP_10 = 0
    for query_id in query_ids:
        try:
            query_result = sorted(results[1].get_result(query_id))
        except TypeError:
            #  sys.stderr.write(query_id+' has no results, but it exists in the qrels.\n')
            print(f"P_10  {query_id}  0.0000")
            continue
        
        idx = 0
        precision = []
        found_docs_qty = 0

        for result in query_result[:max_results]:
            idx += 1
            
            relevance = qrel.get_relevance(query_id, result.doc_id)
            if (relevance > 0):
                found_docs_qty += 1
            
            precision.append(found_docs_qty / idx)

        while len(precision) < 10:
            idx += 1
            precision.append(found_docs_qty / idx)

        print(f"P_10  {query_id}  {precision[9]:.4f}")
        meanP_10 += round(precision[9],4)
    meanP_10 /= 45
    print(f"meanP_10: {meanP_10:.3f}")

def ndcg_cut(maxrank):
    meanNDCG_n = 0
    for query_id in query_ids:
        try:
            query_result = sorted(results[1].get_result(query_id))
        except TypeError:
            #  sys.stderr.write(query_id+' has no results, but it exists in the qrels.\n')
            print(f"ndcg_cut_{maxrank}  {query_id}  0.0000")
            continue
        
        dcg = 0
        idx = 0
        total_relevant_docs = len(qrel.query_2_reldoc_nos[query_id])

        for result in query_result[:maxrank]:
            idx += 1
            relevance = qrel.get_relevance(query_id, result.doc_id)
            if (relevance > 0):
                dcg += (1/math.log2(idx+1))

        idcg = 0
        idx = 0
        for g in range(min(total_relevant_docs,maxrank)):
            idx += 1
            idcg += (1/math.log2(idx+1))

        if (idcg > 0):
            ndcg = dcg / idcg
        else:
            ndcg = 0

        print(f"ndcg_cut_{maxrank}  {query_id}  {ndcg:.4f}")
        meanNDCG_n += round(ndcg,4)
    meanNDCG_n /= 45
    print(f"meanNDCG_{maxrank} {meanNDCG_n:.3f}")

def ndcg_cut_batch(maxrank):
    meanNDCG_n = 0
    for query_id in query_ids:
        try:
            query_result = sorted(results[1].get_result(query_id))
        except TypeError:
            #  sys.stderr.write(query_id+' has no results, but it exists in the qrels.\n')
            # print(f"ndcg_cut_{maxrank}  {query_id}  0.0000")
            continue
        
        dcg = 0
        idx = 0
        total_relevant_docs = len(qrel.query_2_reldoc_nos[query_id])

        for result in query_result[:maxrank]:
            idx += 1
            relevance = qrel.get_relevance(query_id, result.doc_id)
            if (relevance > 0):
                dcg += (1/math.log2(idx+1))

        idcg = 0
        idx = 0
        for g in range(min(total_relevant_docs,maxrank)):
            idx += 1
            idcg += (1/math.log2(idx+1))

        if (idcg > 0):
            ndcg = dcg / idcg
        else:
            ndcg = 0

        # print(f"ndcg_cut_{maxrank}  {query_id}  {ndcg:.4f}")
        meanNDCG_n += round(ndcg,4)
    meanNDCG_n /= 45
    # print(f"meanNDCG_{maxrank} {meanNDCG_n:.3f}")
    return meanNDCG_n

def batch_ndcg10():

    b_min = 0
    b_max = 1
    b_step = 0.05

    # k1_min = 0 
    k1_min = 0.3
    k1_max = 10
    k1_step = 0.1

    base_output_folder = 'C:/Users/Anthony/Documents/School/4A/MSCI_541/A4/msci-541-f23-hw4-AnthonyDest/OutputFolder'
    run_tag = 'adestefaBM25stem'

    ndcg_mean = []
    best_values = [float("-inf"), 0, 0]
  
    for k1 in np.arange(k1_min, k1_max+k1_step, k1_step):
        for b in np.arange(b_min, b_max + b_step, b_step):

            filepath = f"{base_output_folder}/defined-k1-b/hw4-results-{run_tag}-K1-{k1:.1f}-b-{b:.2f}.gz"

            global results
            results = ResultsParser(filepath).parse_gzip()
            results = ResultsParser("no_name").parse_list()

            # ndcg_mean.append([ndcg_cut_batch(10)])
            mean = [ndcg_cut_batch(10)]
            ndcg_mean.append(['k1:', k1, 'b:', b, 'mean:', mean])

            if (mean > best_values[0]):
                best_values[0] = mean
                best_values[1] = k1
                best_values[2] = b

    for item in ndcg_mean:
        print(f"{' '.join(map(str, item))}")

    print(f"\nBest value: {best_values[0]} from k1: {best_values[2]} b: {best_values[2]}")

    

def main():

    run_batch = False
    if run_batch:
        batch_ndcg10()
        sys.exit()


    if eval_method == 'ap':
        average_precision()
    elif eval_method == 'P_10':
        p_at_10()
    elif eval_method == 'ndcg_cut_10':
        ndcg_cut(10)
    elif eval_method == 'ndcg_cut_1000':
        ndcg_cut(1000)
    else:
        sys.stderr.write('Verify evaluation method selection')
        pass

if __name__ == '__main__':
    main()

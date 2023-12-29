
import gzip
from Qrels import Qrels, Judgement
from Results import Results, Result

# Author: Nimesh Ghelani based on code by Mark D. Smucker

class ResultsParser:
    class ResultsParseError(Exception):
        pass

    def __init__(self, filename):
        self.filename = filename

    def parse(self):
        global_run_id = None
        history = set()
        results = Results()
        with open(self.filename) as f:
            for line in f:
                line_components = line.strip().split()
                if len(line_components) != 6:
                    raise ResultsParser.ResultsParseError('lines in results file should have exactly 6 columns')

                query_id, _, doc_id, rank, score, run_id = line_components
                try:
                    rank = int(rank)
                except ValueError:
                    raise ResultsParser.ResultsParseError('Rank is not valid in results file')

                try:
                    score = float(score)
                except ValueError:
                    raise ResultsParser.ResultsParseError('Score is not valid in results file')

                if global_run_id is None:
                    global_run_id = run_id
                elif global_run_id != run_id:
                    raise ResultsParser.ResultsParseError('Mismatching runIDs in results file')

                key = query_id + doc_id
                if key in history:
                    raise ResultsParser.ResultsParseError('Duplicate query_id, doc_id in results file')
                history.add(key)

                results.add_result(query_id, Result(doc_id, score, rank))

        return global_run_id, results
    
    def parse_list(self, output_list):
        global_run_id = None
        history = set()
        results = Results()
        # with open(self.filename) as f:
        for line in output_list:
            # line_components = line.strip().split()
            # if len(line_components) != 6:
            #     raise ResultsParser.ResultsParseError('lines in results file should have exactly 6 columns')

            query_id, _, doc_id, rank, score, run_id = line
            try:
                rank = int(rank)
            except ValueError:
                raise ResultsParser.ResultsParseError('Rank is not valid in results file')

            try:
                score = float(score)
            except ValueError:
                raise ResultsParser.ResultsParseError('Score is not valid in results file')

            if global_run_id is None:
                global_run_id = run_id
            elif global_run_id != run_id:
                raise ResultsParser.ResultsParseError('Mismatching runIDs in results file')

            key = query_id + doc_id
            if key in history:
                raise ResultsParser.ResultsParseError('Duplicate query_id, doc_id in results file')
            history.add(key)

            results.add_result(query_id, Result(doc_id, score, rank))

        return global_run_id, results

    def parse_gzip(self):
        global_run_id = None
        history = set()
        results = Results()

        with gzip.open(self.filename, 'rt') as f:  # 'rt' is used to open the file in text mode
            for line in f:
                line_components = line.strip().split()
                if len(line_components) != 6:
                    raise ResultsParser.ResultsParseError('lines in results file should have exactly 6 columns')

                query_id, _, doc_id, rank, score, run_id = line_components
                try:
                    rank = int(rank)
                except ValueError:
                    raise ResultsParser.ResultsParseError('Rank is not valid in results file')

                try:
                    score = float(score)
                except ValueError:
                    raise ResultsParser.ResultsParseError('Score is not valid in results file')

                if global_run_id is None:
                    global_run_id = run_id
                elif global_run_id != run_id:
                    raise ResultsParser.ResultsParseError('Mismatching runIDs in results file')

                key = query_id + doc_id
                if key in history:
                    raise ResultsParser.ResultsParseError('Duplicate query_id, doc_id in results file')
                history.add(key)

                results.add_result(query_id, Result(doc_id, score, rank))

        return global_run_id, results

class QrelsParser:
    class QrelsParseError(Exception):
        pass

    def __init__(self, filename):
        self.filename = filename

    def parse(self):
        qrels = Qrels()
        with open(self.filename) as f:
            for line in f:
                line_components = line.strip().split()
                if len(line_components) != 4:
                    raise QrelsParser.QrelsParseError("Line should have 4 columns")
                query_id, _, doc_id, relevance = line_components
                relevance = int(relevance)
                qrels.add_judgement(Judgement(query_id, doc_id, relevance))
        return qrels


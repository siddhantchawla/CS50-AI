import nltk
import sys
import glob
import os
import string
import math

FILE_MATCHES = 1
SENTENCE_MATCHES = 1


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python questions.py corpus")

    # Calculate IDF values across files
    files = load_files(sys.argv[1])
    file_words = {
        filename: tokenize(files[filename])
        for filename in files
    }
    file_idfs = compute_idfs(file_words)

    # Prompt user for query
    query = set(tokenize(input("Query: ")))

    # Determine top file matches according to TF-IDF
    filenames = top_files(query, file_words, file_idfs, n=FILE_MATCHES)

    # Extract sentences from top files
    sentences = dict()
    for filename in filenames:
        for passage in files[filename].split("\n"):
            for sentence in nltk.sent_tokenize(passage):
                tokens = tokenize(sentence)
                if tokens:
                    sentences[sentence] = tokens

    # Compute IDF values across sentences
    idfs = compute_idfs(sentences)

    # Determine top sentence matches
    matches = top_sentences(query, sentences, idfs, n=SENTENCE_MATCHES)
    for match in matches:
        print(match)


def load_files(directory):
    """
    Given a directory name, return a dictionary mapping the filename of each
    `.txt` file inside that directory to the file's contents as a string.
    """
    files = dict()
    path = directory + os.sep + "*"
    for file in glob.glob(path):
        name = file.split(os.sep)[-1]
        with open(file) as f:
            files[name] = f.read()

    return files


def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.
    """
    document = document.lower()
    document = document.translate(str.maketrans('', '', string.punctuation))
    words = nltk.word_tokenize(document)
    stopwords = nltk.corpus.stopwords.words("english")
    result = [i for i in words if i not in stopwords]

    return result

def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """
    words = set()
    idfs = dict()
    for file in documents:
        for word in documents[file]:
            words.add(word)

    for word in words:
        f = sum(word in documents[filename] for filename in documents)
        idf = math.log(len(documents) / f)
        idfs[word] = idf

    return idfs


def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """
    files_score = dict()

    for file in files:
        files_score[file] = 0
        for word in query:
            idf = 0
            if word in idfs:
                idf = idfs[word]
            files_score[file] += files[file].count(word) * idf

    rank = sorted(files_score.keys(),key = lambda x: files_score[x],reverse = True)

    rank = list(rank)
    return rank[:n]


def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """
    sentence_scores = dict()
    for sent in sentences:
        s = 0
        words = sentences[sent]
        word_count = len(words)
        count = 0
        for word in query:
            if word in words:
                s += idfs[word]
                count += 1

        sentence_scores[sent] = (s,float(count/word_count))

    sentence = sorted(sentence_scores.keys(),key = lambda x:sentence_scores[x],reverse = True)
    sentence = list(sentence)

    return sentence[:n]


if __name__ == "__main__":
    main()

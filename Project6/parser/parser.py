import nltk
import sys

TERMINALS = """
Adj -> "country" | "dreadful" | "enigmatical" | "little" | "moist" | "red"
Adv -> "down" | "here" | "never"
Conj -> "and"
Det -> "a" | "an" | "his" | "my" | "the"
N -> "armchair" | "companion" | "day" | "door" | "hand" | "he" | "himself"
N -> "holmes" | "home" | "i" | "mess" | "paint" | "palm" | "pipe" | "she"
N -> "smile" | "thursday" | "walk" | "we" | "word"
P -> "at" | "before" | "in" | "of" | "on" | "to" | "until"
V -> "arrived" | "came" | "chuckled" | "had" | "lit" | "said" | "sat"
V -> "smiled" | "tell" | "were"
"""

NONTERMINALS = """

S -> NP VP | NP VP CP

VP -> V | V NP | VP Adv | Adv VP | VP NP | VP PP
NP -> N | Adj N | Adj NP | Det NP | N PP | N P S | N Adv
PP -> P NP
CP -> Conj S | Conj VP


"""
test = """
    S -> NP VP

    AP -> A | A AP
    NP -> N | D NP | AP NP | N PP
    PP -> P NP | P N
    VP -> V | V NP | V NP PP

    A -> "big" | "blue" | "small" | "dry" | "wide"
    D -> "the" | "a" | "an"
    N -> "she" | "city" | "car" | "street" | "dog" | "binoculars"
    P -> "on" | "over" | "before" | "below" | "with"
    V -> "saw" | "walked"
"""
grammar = nltk.CFG.fromstring(NONTERMINALS + TERMINALS)
# grammar = nltk.CFG.fromstring(test)
parser = nltk.ChartParser(grammar)


def main():

    # If filename specified, read sentence from file
    if len(sys.argv) == 2:
        with open(sys.argv[1]) as f:
            s = f.read()

    # Otherwise, get sentence as input
    else:
        s = input("Sentence: ")

    # Convert input into list of words
    s = preprocess(s)

    # Attempt to parse sentence
    try:
        trees = list(parser.parse(s))
    except ValueError as e:
        print(e)
        return
    if not trees:
        print("Could not parse sentence.")
        return

    # Print each tree with noun phrase chunks
    for tree in trees:
        tree.pretty_print()

        print("Noun Phrase Chunks")
        for np in np_chunk(tree):
            print(" ".join(np.flatten()))


def preprocess(sentence):
    """
    Convert `sentence` to a list of its words.
    Pre-process sentence by converting all characters to lowercase
    and removing any word that does not contain at least one alphabetic
    character.
    """
    l = []
    sentence = sentence.lower()
    tokenized = nltk.word_tokenize(sentence)
    if tokenized[-1] == '.':
        tokenized = tokenized[:-1]
    return tokenized


def np_chunk(tree):
    """
    Return a list of all noun phrase chunks in the sentence tree.
    A noun phrase chunk is defined as any subtree of the sentence
    whose label is "NP" that does not itself contain any other
    noun phrases as subtrees.
    """
    chunks = []
    for subtree in tree.subtrees():
        if subtree.label() == 'NP':
            t = subtree.subtrees()
            labels = []
            for s in t:
                labels.append(s.label())
            labels = labels[1:]
            if 'NP' not in labels:
                chunks.append(subtree)
    return chunks
    

if __name__ == "__main__":
    main()
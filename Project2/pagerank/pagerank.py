import os
import random
import re
import sys

from pomegranate import *
import copy


DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    pages = corpus.keys()
    distribution = dict()
    
    for p in pages:
        distribution[p] = (1-damping_factor)/len(pages)

    direct = list(corpus[page])

    if len(direct) == 0:
        direct = pages

    for p in direct:
        distribution[p] += damping_factor/len(direct)

    return distribution


# def sample_pagerank(corpus, damping_factor, n):  #Using BayesianNetwork()
    # pagerank = dict()
    # pages = list(corpus.keys())

    # for page in pages:
    #     pagerank[page] = 0
    # l = len(pages)
    # curr_page = pages[random.randrange(l)]
    # pagerank[curr_page] += 1

    # for i in range(1,n):
    #     trm = transition_model(corpus,curr_page,damping_factor)

        # page = Node(DiscreteDistribution(trm), name="page")
        # model = BayesianNetwork()
        # model.add_states(page)
        # model.bake()

        # for state in model.states:
        #     curr_page = state.distribution.sample()

        # pagerank[curr_page] += 1


    # for page in pages:
    #     pagerank[page] = pagerank[page]/n
    # return pagerank

def sample_pagerank(corpus, damping_factor, n):  #Using MarkovChain()

    pagerank = dict()
    pages = list(corpus.keys())

    start = dict()
    table = []
    for page in pages:
        pagerank[page] = 0
        start[page] = 1.0/len(pages)
        trm = transition_model(corpus,page,damping_factor)
        key = list(trm.keys())
        for k in key:
            table.append([page,k,trm[k]])

    start = DiscreteDistribution(start)
    transitions = ConditionalProbabilityTable(table,[start])
    model = MarkovChain([start, transitions])

    samples = model.sample(n)

    for s in samples:
        pagerank[s] += 1

    for page in pages:
        pagerank[page] = pagerank[page]/n

    return pagerank


def find_links(corpus,find):

    l = []
    pages = list(corpus.keys())

    for page in pages:
        if find in corpus[page]:
            l.append(page)

    return l



def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    pagerank = dict()
    pages = list(corpus.keys())

    for page in pages:
        pagerank[page] = 1/len(pages)

    
    flag = True

    while flag:
        c = (1 - damping_factor)/len(pages)
        flag = False
        for page in pages:
            s = 0
            links = find_links(corpus,page)
            for link in links:
                s = s + pagerank[link]/len(corpus[link])

            s = s * damping_factor
            updation = abs(pagerank[page] - c - s)
            if updation > 0.001:
                flag = True
            pagerank[page] = c + s

    return pagerank


if __name__ == "__main__":
    main()

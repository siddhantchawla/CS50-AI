import csv
import itertools
import sys
from pomegranate import *

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def trait_conditional():
    prob = []

    keys = list(PROBS["trait"].keys())

    for key in keys:
        prob.append([key,True,PROBS["trait"][key][True]])
        prob.append([key,False,PROBS["trait"][key][False]])

    return prob



def child_conditional():

    prob = []
 
    giving = [0.01,0.50,0.99] #calculated using PROBS["mutation"]
    not_giving = [0.99,0.50,0.01]

    for i in range(3):
        for j in range(3):
            for k in range(3):
                if k == 0:
                    prob.append([i,j,k,not_giving[i]*not_giving[j]])
                elif k == 2:
                    prob.append([i,j,k,giving[i]*giving[j]])
                else:
                    prob.append([i,j,k,(giving[i]*not_giving[j] + not_giving[i]*giving[j])])
    return prob

def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """

    #create the conditional probablity table using discrete probablity table

    trait_prob = trait_conditional()
    child_prob = child_conditional()

    # Create BayesianNetwork Model from people

    model = BayesianNetwork()
    persons = list(people.keys())
    node = dict()
    conditions = [] #list to store given conditions of the people

    for person in persons:   #Adding Nodes representing people who do not have parents.
        if people[person]['mother'] is None and people[person]['father'] is None:
            node[person] = Node(DiscreteDistribution(PROBS["gene"]),name = person)
            trait = person+"_Trait"
            node[trait] = Node(ConditionalProbabilityTable(trait_prob,[node[person].distribution]),name = trait)
            model.add_states(node[person],node[trait])
            model.add_edge(node[person],node[trait])


            if person in one_gene:
                conditions.append(1)
            elif person in two_genes:
                conditions.append(2)
            else:
                conditions.append(0)

            if person in have_trait:
                conditions.append(True)
            else:
                conditions.append(False)

    for person in persons: #Adding Nodes representing people who do have parents.
        if people[person]['mother'] and people[person]['father']:
            node[person] = Node(ConditionalProbabilityTable(child_prob,[node[people[person]['father']].distribution,node[people[person]['mother']].distribution]),name = person)
            trait = person+"_Trait"
            node[trait] = Node(ConditionalProbabilityTable(trait_prob,[node[person].distribution]),name = trait)
            model.add_states(node[person],node[trait])
            model.add_edge(node[person],node[trait])
            model.add_edge(node[people[person]['father']],node[person])
            model.add_edge(node[people[person]['mother']],node[person])

            
            if person in one_gene:
                conditions.append(1)
            elif person in two_genes:
                conditions.append(2)
            else:
                conditions.append(0)

            if person in have_trait:
                conditions.append(True)
            else:
                conditions.append(False)

    #calculate the probablity using the model

    model.bake()
    probability = model.probability([conditions])
    return probability


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    persons = list(probabilities.keys())

    for person in persons:
        if person in one_gene:
            probabilities[person]["gene"][1] += p
        elif person in two_genes:
            probabilities[person]["gene"][2] += p
        else:
            probabilities[person]["gene"][0] += p

        if person in have_trait:
            probabilities[person]["trait"][True] += p
        else:
            probabilities[person]["trait"][False] += p

    return True


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    persons = list(probabilities.keys())

    for person in persons:
        s = 0
        for i in range(3):
            s = s + probabilities[person]["gene"][i]

        for i in range(3):
            probabilities[person]["gene"][i] = probabilities[person]["gene"][i]/s


        s = probabilities[person]["trait"][True] + probabilities[person]["trait"][False]

        probabilities[person]["trait"][True] = probabilities[person]["trait"][True]/s
        probabilities[person]["trait"][False] = probabilities[person]["trait"][False]/s


    return True


if __name__ == "__main__":
    main()

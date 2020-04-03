from logic import *

AKnight = Symbol("A is a Knight")
AKnave = Symbol("A is a Knave")

BKnight = Symbol("B is a Knight")
BKnave = Symbol("B is a Knave")

CKnight = Symbol("C is a Knight")
CKnave = Symbol("C is a Knave")

# Puzzle 0
# A says "I am both a knight and a knave."
knowledge0 = And(
    Implication(And(AKnight,AKnave),AKnight),
    Implication(Not(And(AKnight,AKnave)),AKnave),

    Or(AKnight,AKnave),
    Not(And(AKnave,AKnight)),

)

# Puzzle 1
# A says "We are both knaves."
# B says nothing.
knowledge1 = And(
    Implication(And(AKnave,BKnave),And(AKnave,BKnave,AKnight)),
    Implication(Not(And(BKnave,AKnave)),And(AKnave,Or(BKnave,BKnight))),

    Or(AKnight,AKnave),
    Not(And(AKnave,AKnight)),
    Or(BKnight,BKnave),
    Not(And(BKnave,BKnight)),
)

# Puzzle 2
# A says "We are the same kind."
# B says "We are of different kinds."
knowledge2 = And(
    Implication(Or(And(AKnight,BKnight),And(AKnave,BKnave)),And(AKnight,BKnight)),
    Implication(Or(And(AKnight,BKnave),And(AKnave,BKnight)),And(AKnave,BKnight)),
    Implication(Not(Or(And(AKnight,BKnave),And(AKnave,BKnight))),And(Or(AKnave,AKnight),BKnave)),
    
    Or(AKnight,AKnave),
    Not(And(AKnave,AKnight)),
    Or(BKnight,BKnave),
    Not(And(BKnave,BKnight)),
)

# Puzzle 3
# A says either "I am a knight." or "I am a knave.", but you don't know which.
# B says "A said 'I am a knave'."
# B says "C is a knave."
# C says "A is a knight."
knowledge3 = And(
    Biconditional(CKnave,BKnight),
    
    Biconditional(CKnight,AKnight),
    

    Implication(BKnight,Biconditional(AKnave,AKnight)),


    Or(AKnight,AKnave),
    Not(And(AKnave,AKnight)),
    Or(BKnight,BKnave),
    Not(And(BKnave,BKnight)),
    Or(CKnight,CKnave),
    Not(And(CKnave,CKnight)),

)


def main():
    symbols = [AKnight, AKnave, BKnight, BKnave, CKnight, CKnave]
    puzzles = [
        ("Puzzle 0", knowledge0),
        ("Puzzle 1", knowledge1),
        ("Puzzle 2", knowledge2),
        ("Puzzle 3", knowledge3)
    ]
    for puzzle, knowledge in puzzles:
        print(puzzle)
        if len(knowledge.conjuncts) == 0:
            print("    Not yet implemented.")
        else:
            for symbol in symbols:
                if model_check(knowledge, symbol):
                    print(f"    {symbol}")


if __name__ == "__main__":
    main()

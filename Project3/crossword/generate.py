import sys
import copy

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        variables = list(self.domains.keys())
        for var in variables:
            length = var.length
            domain = list(self.domains[var])
            for word in domain:
                if len(word) != length:
                    self.domains[var].remove(word)
        return True

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revised = False
        if self.crossword.overlaps[x,y]:
            i,j = self.crossword.overlaps[x,y][0],self.crossword.overlaps[x,y][1]
            domain_x = list(self.domains[x])
            domain_y = self.domains[y]
            for word in domain_x:
                flag = True
                for w in domain_y:
                    if w[j] == word[i]:
                        flag = False
                        break
                if flag: 
                    self.domains[x].remove(word)
        return revised

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs is None:
            arcs = []
            variables = list(self.domains.keys())
            for var in variables:
                neighbors = self.crossword.neighbors(var)
                for neighbor in neighbors:
                    if (var,neighbor) not in arcs and (neighbor,var) not in arcs:
                        arcs.append((var,neighbor))

        while len(arcs) > 0:
            (x,y) = arcs[0]
            arcs.pop(0)
            if self.revise(x,y):
                if len(self.domains[x]) == 0:
                    return False
                neighbors = self.crossword.neighbors(x)
                neighbors.remove(y)
                for neighbor in neighbors:
                    if (x,neighbor) not in arcs and (neighbor,x) not in arcs:
                        arcs.append((x,neighbor))
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        variables = list(self.domains.keys())
        for var in variables:
            if not var in assignment:
                return False
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        values = set()
        variables = list(self.domains.keys())
        for var in variables:
            if var in assignment:
                if assignment[var] in values:
                    return False
                values.add(assignment[var])
                if len(assignment[var]) != var.length:
                    return False
                neighbors = self.crossword.neighbors(var)
                for neighbor in neighbors:
                    if neighbor in assignment:
                        (x,y) = self.crossword.overlaps[var,neighbor]
                        if assignment[var][x] != assignment[neighbor][y]:
                            return False
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        domain = list(self.domains[var])
        cal = []
        neighbors = self.crossword.neighbors(var)
        for value in domain:
            num = 0
            for neighbor in neighbors:
                if neighbor not in assignment:
                    (x,y) = self.crossword.overlaps[var,neighbor]
                    neighbor_domain = self.domains[neighbor]
                    for word in neighbor_domain:
                        if word[y] != value[x]:
                            num += 1
            cal.append((num,value))

        cal.sort()
        result = []
        for c in cal:
            result.append(c[1])
        return domain #Basic Version

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        ans = 0
        degree = 0
        rem_value = 10000
        variables = list(self.domains.keys())
        for var in variables:
            if not var in assignment:
                d = len(list(self.crossword.neighbors(var)))
                v = len(list(self.domains[var]))
                if (v < rem_value) or (v == rem_value and d > degree):
                    rem_value = v
                    degree = d
                    ans = var
        return ans

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment
        var = self.select_unassigned_variable(assignment)
        values = self.order_domain_values(var,assignment)
        for value in values:
            new_assignment = copy.deepcopy(assignment)
            new_assignment[var] = value
            if self.consistent(new_assignment):
                arcs = []    # ensuring arc consistency 
                neighbors = self.crossword.neighbors(var)
                for neighbor in neighbors:
                    if (var,neighbor) not in arcs and (neighbor,var) not in arcs:
                        arcs.append((var,neighbor))
                inf = self.ac3(arcs)
                if inf == False:
                    return None
                result = self.backtrack(new_assignment)
                if result is not None:
                    return result
        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()

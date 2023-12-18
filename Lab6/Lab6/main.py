class Grammar:
    EPSILON = "epsilon"

    def __init__(self):
        self.N = []
        self.E = []
        self.S = ""
        self.P = {}

    def __processLine(self, line: str):
        # Get what comes after the '='
        return line.strip().split(' ')[2:]

    def readFromFile(self, file_name: str):
        with open(file_name) as file:
            try:
                N = self.__processLine(file.readline())
                E = self.__processLine(file.readline())
                S = self.__processLine(file.readline())[0]

                file.readline()  # P =

                # Get all transitions
                P = {}
                for line in file:
                    line = line.strip()
                    if not line:
                        continue  # Skip empty lines

                    split = line.split('->')
                    if len(split) != 2:
                        print(f"Invalid production format: {line}")
                        continue

                    source = split[0].strip()
                    sequence = split[1].strip()

                    if source not in P:
                        P[source] = []

                    if sequence:
                        sequence_list = [token.strip() for token in sequence.split(' ')]
                        P[source].append(sequence_list)
                    else:
                        # Handle epsilon productions
                        P[source].append([self.EPSILON])

            except Exception as e:
                print(f"Error while processing the file: {e}")
                return

            self.N = N
            self.E = E
            self.S = S
            self.P = P

    def eliminate_left_recursion(self):
        for i, A in enumerate(self.N):
            for j in range(i):
                B = self.N[j]
                for alpha in self.P[A]:
                    if alpha[0] == B:
                        self.P[A].remove(alpha)
                        for beta in self.P[B]:
                            self.P.setdefault(A + "'", []).append(beta + alpha[1:] if alpha[1:] else [self.EPSILON])

    def factorize(self):
        for A in self.N:
            prods = self.P.get(A, [])
            i = 0
            while i < len(prods):
                current_prod = prods[i]
                if len(current_prod) > 1:
                    for j in range(1, len(current_prod)):
                        new_nonterminal = f"{A}factored{j}"
                        if new_nonterminal not in self.N:
                            self.N.append(new_nonterminal)
                        if A not in self.P:
                            self.P[A] = []

                        if new_nonterminal not in self.P:
                            self.P[new_nonterminal] = [current_prod[j]]
                        prods[i][j] = new_nonterminal
                i += 1

    def calculate_first(self):
        first = {}
        for A in self.N:
            first[A] = set()

        for a in self.E:
            first[a] = set([a])

        print("Initializing First sets:")
        print("Non-terminals:", self.N)
        print("Terminals:", self.E)
        print("Epsilon:", self.EPSILON)
        print("Initial First sets:")
        print(first)

        for A in self.N:
            for alpha in self.P[A]:
                i = 0
                print(f"\nProcessing production: {A} -> {alpha}")
                while i < len(alpha):
                    B = alpha[i]
                    if B not in first:
                        first[B] = set()
                    print(f"Checking First({B})")
                    first[A] |= first[B]
                    print(f"First({A}) now includes First({B}): {first[A]}")
                    if self.EPSILON not in first[B]:
                        break
                    i += 1
                else:
                    first[A].add(self.EPSILON)
                    print(f"First({A}) now includes Epsilon: {first[A]}")

        print("\nFinal First sets:")
        print(first)
        return first

    def calculate_follow(self, first):
        follow = {}
        for A in self.N:
            follow[A] = set()
        follow[self.S].add('$')

        print("\nInitializing Follow sets:")
        print("Non-terminals:", self.N)
        print("Terminals:", self.E)
        print("Epsilon:", self.EPSILON)
        print("Initial Follow sets:")
        print(follow)

        changed = True
        while changed:
            changed = False
            for A in self.N:
                for alpha in self.P[A]:
                    print(f"\nProcessing production: {A} -> {alpha}")
                    for i in range(len(alpha)):
                        B = alpha[i]
                        if B not in follow:
                            follow[B] = set()
                        if B in self.N:
                            rest = alpha[i + 1:]
                            if i == len(alpha) - 1 or self.EPSILON in first.get(alpha[i + 1], set()):
                                print(f"Updating Follow({B}) with Follow({A}): {follow[B]}")
                                follow[B] |= follow[A]
                                print(f"Follow({B}): {follow[B]}")
                            for j in range(len(rest)):
                                if self.EPSILON not in first.get(rest[j], set()):
                                    break
                                print(
                                    f"Updating Follow({B}) with First({rest[j]}) - Epsilon: {first.get(rest[j], set()) - {self.EPSILON} }")
                                follow[B] |= first.get(rest[j], set()) - {self.EPSILON}
                                print(f"Follow({B}): {follow[B]}")
                                if j == len(rest) - 1:
                                    print(f"Updating Follow({B}) with Follow({A}): {follow[B]}")
                                    follow[B] |= follow[A]
                                    print(f"Follow({B}): {follow[B]}")
                                    follow[B] -= {self.EPSILON}
                                    print(f"Removing Epsilon from Follow({B}): {follow[B]}")
                                    changed = True

        print("\nFinal Follow sets:")
        print(follow)
        return follow

    def build_ll1_table(self):
        ll1_table = {}

        first = self.calculate_first()
        follow = self.calculate_follow(first)

        for A in self.N:
            ll1_table[A] = {}
            for terminal in self.E + [self.EPSILON]:
                ll1_table[A][terminal] = None

        for A in self.N:
            for alpha in self.P[A]:
                first_alpha = set()
                i = 0
                while i < len(alpha):
                    B = alpha[i]
                    first_alpha |= first[B]
                    if self.EPSILON not in first[B]:
                        break
                    i += 1
                else:
                    first_alpha.add(self.EPSILON)

                for terminal in first_alpha:
                    if terminal != self.EPSILON:
                        ll1_table[A][terminal] = alpha

                if self.EPSILON in first_alpha:
                    for terminal in follow[A]:
                        ll1_table[A][terminal] = alpha

        return ll1_table

    def check_ll1(self):
        ll1_table = self.build_ll1_table()
        for key in ll1_table:
            if ll1_table[key] != [self.EPSILON]:
                return False
        return True

    def checkCFG(self):
        hasStartingSymbol = False
        for key in self.P.keys():
            if key == self.S:
                hasStartingSymbol = True
            if key not in self.N:
                return False
        if not hasStartingSymbol:
            return False
        for A in self.N:
            if not self.isCFG(A):
                return False
        return True

    def isCFG(self, A):
        for alpha in self.P[A]:
            for symbol in alpha:
                if symbol not in self.N and symbol not in self.E and symbol != self.EPSILON:
                    return False
        return True

    def __str__(self):
        result = "N = " + str(self.N) + "\n"
        result += "E = " + str(self.E) + "\n"
        result += "S = " + str(self.S) + "\n"
        result += "P = " + str(self.P) + "\n"
        return result


if __name__ == '__main__':
    # Create an instance of the Grammar class
    grammar = Grammar()

    # Read the grammar from a file
    grammar.readFromFile("g1.in")

    # Print the initial state of the grammar
    print("Initial Grammar:")
    print("Is CFG:", grammar.checkCFG())

    # Eliminate left recursion and factorize the grammar
    grammar.eliminate_left_recursion()
    print(grammar)
    grammar.factorize()

    # Print the grammar after left recursion elimination and factorization
    print("\nGrammar after Left Recursion Elimination and Factorization:")
    print(grammar)

    # Calculate and print the First sets
    first_sets = grammar.calculate_first()
    print("\nFirst Sets:")
    for non_terminal, first_set in first_sets.items():
        print(f"First({non_terminal}): {first_set}")

    # Calculate and print the Follow sets
    follow_sets = grammar.calculate_follow(first_sets)
    print("\nFollow Sets:")
    for non_terminal, follow_set in follow_sets.items():
        print(f"Follow({non_terminal}): {follow_set}")

    # Build and print the LL(1) parsing table
    ll1_table = grammar.build_ll1_table()
    print("\nLL(1) Parsing Table:")
    for non_terminal, row in ll1_table.items():
        print(f"{non_terminal}: {row}")
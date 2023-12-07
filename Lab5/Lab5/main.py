
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
            N = self.__processLine(file.readline())
            E = self.__processLine(file.readline())
            S = self.__processLine(file.readline())[0]

            file.readline()  # P =

            # Get all transitions
            P = {}
            for line in file:
                split = line.strip().split('->')
                source = split[0].strip()
                sequence = split[1].lstrip(' ')
                sequence_list = []
                for c in sequence.split(' '):
                    sequence_list.append(c)

                if source in P.keys():
                    P[source].append(sequence_list)
                else:
                    P[source] = [sequence_list]

            self.N = N
            self.E = E
            self.S = S
            self.P = P

    def eliminate_left_recursion(self):
        for A in self.N:
            for i in range(self.N.index(A)):
                B = self.N[i]
                if (A, B) in self.P:
                    alpha = self.P[(A, B)]
                    self.P.pop((A, B))
                    for beta in self.P[B]:
                        self.P.setdefault(A, []).extend(beta + alpha if beta != [self.EPSILON] else alpha)

    def factorize(self):
        for A in self.N:
            prods = self.P[A]
            i = 0
            while i < len(prods):
                current_prod = prods[i]
                if len(current_prod) > 1:
                    for j in range(1, len(current_prod)):
                        new_nonterminal = f"{A}factored{j}"
                        if (new_nonterminal, current_prod[j]) not in self.P:
                            self.P[(new_nonterminal, current_prod[j])] = [current_prod[j]]
                        prods[i][j] = new_nonterminal
                        A = new_nonterminal
            i += 1

    def calculate_first(self):
        first = {}
        for A in self.N:
            first[A] = set()
        for a in self.E:
            first[a] = set([a])
        for A in self.N:
            for alpha in self.P[A]:
                i = 0
                while i < len(alpha):
                    B = alpha[i]
                    first[A] |= first[B]
                    if self.EPSILON not in first[B]:
                        break
                    i += 1
                else:
                    first[A].add(self.EPSILON)
        return first

    def calculate_follow(self, first):
        follow = {}
        for A in self.N:
            follow[A] = set()
        follow[self.S].add('$')
        changed = True
        while changed:
            changed = False
            for A in self.N:
                for alpha in self.P[A]:
                    for i in range(len(alpha)):
                        B = alpha[i]
                        if B in self.N:
                            rest = alpha[i + 1:]
                            if i == len(alpha) - 1 or self.EPSILON in first[alpha[i + 1]]:
                                follow[B] |= follow[A]
                            for j in range(len(rest)):
                                if self.EPSILON not in first[rest[j]]:
                                    break
                                if j == len(rest) - 1:
                                    follow[B] |= follow[A]
                                    follow[B] -= {self.EPSILON}
                            follow[B] |= first[rest[j]] - {self.EPSILON}
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


g = Grammar()
g.readFromFile("g2.txt")
print(str(g))
if g.checkCFG():
    print("The grammar is a CFG")
else:
    print("The grammar is not a CFG")
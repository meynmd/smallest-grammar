class Production:
    RuleNum = 1

    def __init__(self, name, num = None, rhs = ()):
        self.name = name
        self.rhs = rhs
        self.number = Production.RuleNum
        Production.RuleNum += 1

    def __str__(self):
        return 'R' + str(self.number)


class Separator:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return str(self.name)


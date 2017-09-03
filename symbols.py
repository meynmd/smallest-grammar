class Production:
    RuleNum = 1

    def __init__(self, name, num, rhs):
        self.name = name
        self.rhs = rhs
        self.number = num
        Production.RuleNum += 1

    def __str__(self):
        return 'R' + str(self.number)

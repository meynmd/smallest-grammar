import sys
from copy import deepcopy
from maxrepeat import *
from symbols import *

D_MAX = 3
WIDTH = 10  # more than 10 might take a long time...

"""
compressGrammar(startRHS, rules, depth)

startRHS    list    the stuff on the right hand side of the start symbol
rules       list    a list of Productions (not including from start symbol) 
depth       int     current depth in search tree

returns (new startRHS, new rules)
"""
def compressGrammar(rules, depth):
    log = ''
    finalLog = ''

    while True:
        # look for any max repeats to replace
        candidates = maxrepeat(rules)
        if len(candidates) > WIDTH:
            candidates = candidates[: WIDTH]
        if len(candidates) < 1:
            return rules, ''

        if depth > D_MAX:
            # depth limit exceeded: make greedy substitution
            newGram, log = replace(
                rules, candidates[0][0], candidates[0][1], log
            )
            resRule, resLog = compressGrammar(newGram, depth + 1)
            return resRule, log + resLog
        else:
            # descend the tree
            minLen = sys.maxint
            for c in candidates:
                newGram, log = replace(rules, c[0], c[1], log)
                candRules, endLog = compressGrammar(
                    newGram, depth + 1
                )
                if gramLength(candRules) < minLen:
                    minLen = gramLength(candRules)
                    minGram = candRules
                    finalLog = log + endLog
            return minGram, finalLog


def gramLength(rules):
    # return len(start) + \
    #        sum([len(r.rhs) for r in rules]) + \
    #        len(rules) + 1
    s = []
    return len(rules)


"""
replace(fullstr, substr, locations, ruleNum)

fullstr     the string on which we are operating
substr      substring to be replaced
locations   indices where that substring can be found
ruleNum     what number should we give the resulting rule?

returns (new string, new rule)
"""
def replace(fullstr, substr, locations, log=None):
    g = deepcopy(fullstr)
    newRule = Production('R', rhs=substr)
    for start, end in locations:
        for i in range(start, end):
            g[i] = None
        g[start] = 'R{}'.format(newRule.number)

    while None in g:
        g.remove(None)

    g.append(Separator('R{}'.format(newRule.number)))
    g += substr


    if log is None:
        return g
    else:
        log = 'S -> ' + str([str(s) for s in fullstr]) + '\n'
        log += 'replacing ' + str([str(s) for s in substr]) + '\n\twith R{}\n\n'.format(newRule.number)
        return g, log


# not using this anymore
def grammarToList(grammarDictionary):
    grammarList = []
    count = 0
    for key, val in grammarDictionary.items():
        count += 1
        grammarList.append(key)
        grammarList += val

    return grammarList


def stringify(rules):
    gramList = []
    for rule in rules:
        gramList += [s for s in rule]
        gramList.append(Separator())
    return gramList


def listToDict(gramList):
    rules = {}
    lhs = None
    rhs = []
    for sym in gramList:
        if isinstance(sym, Separator):
            if lhs is not None:
                rules[lhs.name] = rhs
                lhs = sym.name
                rhs = []
            lhs = sym
        else:
            rhs.append(sym)
    rules[lhs.name] = rhs
    return rules


def printRule(rule):
    print '{0}{1} ->'.format(rule.name, rule.number),
    for s in rule.rhs:
        if type(s) is str or type(s) is int:
            print '{}'.format(s),
        else:
            print 'R{}'.format(s.number),
    print


# replace rule numbers with nicer, small numbers
def cleanupRuleNums(rules):
    count = 0
    for r in rules:
        count += 1
        r.number = count

    return rules


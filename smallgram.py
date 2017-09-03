import sys
from copy import deepcopy
from maxrepeat import *
from symbols import *

D_MAX = 3
WIDTH = 5  # more than 10 might take a long time...

"""
compressGrammar(startRHS, rules, depth)

startRHS    list    the stuff on the right hand side of the start symbol
rules       list    a list of Productions (not including from start symbol) 
depth       int     current depth in search tree

returns (new startRHS, new rules)
"""
def compressGrammar(startRHS, rules, depth):
    log = ''
    finalLog = ''
    # choose the next available rule number
    if len(rules) == 0:
        nextRule = 1
    else:
        nextRule = max(r.number for r in rules) + 1

    while True:
        # look for any max repeats to replace
        candidates = maxrepeat(startRHS)
        if len(candidates) > WIDTH:
            candidates = candidates[: WIDTH]
        if len(candidates) < 1:
            return startRHS, rules, ''

        if depth > D_MAX:
            # depth limit exceeded: make greedy substitution
            newStart, newRule, log = replace(
                startRHS, candidates[0][0], candidates[0][1], nextRule, log
            )
            rules.append(newRule)
            resStart, resRule, resLog = compressGrammar(newStart, rules, depth + 1)
            return resStart, resRule, log + resLog
        else:
            # descend the tree
            minLen = sys.maxint
            for c in candidates:
                newStart, newRule, log = replace(startRHS, c[0], c[1], nextRule, log)

                newRules = rules + [newRule]
                candStart, candRules, endLog = compressGrammar(
                    newStart, newRules, depth + 1
                )
                if gramLength(candStart, candRules) < minLen:
                    minLen = gramLength(candStart, candRules)
                    minGram = candStart, candRules
                    finalLog = log + endLog
            return minGram[0], minGram[1], finalLog


def gramLength(start, rules):
    return len(start) + \
           sum([len(r.rhs) for r in rules]) + \
           len(rules) + 1


"""
replace(fullstr, substr, locations, ruleNum)

fullstr     the string on which we are operating
substr      substring to be replaced
locations   indices where that substring can be found
ruleNum     what number should we give the resulting rule?

returns (new string, new rule)
"""
def replace(fullstr, substr, locations, ruleNum, log=None):
    if log is not None:
        log = 'S -> ' + str([str(s) for s in fullstr]) + '\n'
        log += 'replacing ' + str([str(s) for s in substr]) + '\nwith R{}\n'.format(ruleNum)

    g = deepcopy(fullstr)
    newRule = Production('R', ruleNum, substr)
    for start, end in locations:
        for i in range(start, end):
            g[i] = None
        g[start] = newRule

    while None in g:
        g.remove(None)

    if log is None:
        return g, newRule
    else:
        return g, newRule, log


# not using this anymore
def grammarToList(grammarDictionary):
    grammarList = []
    count = 0
    for key, val in grammarDictionary.items():
        count += 1
        grammarList.append(key)
        grammarList += val

    return grammarList


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


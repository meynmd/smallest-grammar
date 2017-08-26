#!/bin/python

import sys
import music21
from copy import deepcopy
from multiprocessing import Process, Queue
import time
from maxrepeat import *
from symbols import *

D_MAX = 3
WIDTH = 25  # more than 10 might take a long time...

"""
compressGrammar(startRHS, rules, depth)

startRHS    list    the stuff on the right hand side of the start symbol
rules       list    a list of Productions (not including from start symbol) 
depth       int     current depth in search tree

returns (new startRHS, new rules)
"""
def compressGrammar(startRHS, rules, depth):
    if len(rules) == 0:
        nextRule = 1
    else:
        nextRule = max(r.number for r in rules) + 1

    while True:
        candidates = maxrepeat(startRHS)
        if len(candidates) > WIDTH:
            candidates = candidates[: WIDTH]
        if len(candidates) < 1:
            return startRHS, rules

        if depth > D_MAX:
            newStart, newRule = replace(
                startRHS, candidates[0][0], candidates[0][1], nextRule
            )
            rules.append(newRule)
            return compressGrammar(newStart, rules, depth + 1)
        else:
            # descend the tree
            minLen = sys.maxint
            for c in candidates:
                newStart, newRule = replace(startRHS, c[0], c[1], nextRule)

                newRules = rules + [newRule]
                candStart, candRules = compressGrammar(
                    newStart, newRules, depth + 1
                )
                if gramLength(candStart, candRules) < minLen:
                    minLen = gramLength(candStart, candRules)
                    minGram = candStart, candRules
            return minGram


# in progress: try to parallelize compressGrammar
def compressGrammar_mp(startRHS, rules, depth, outQueue):
    myQueue = Queue()
    if len(rules) == 0:
        nextRule = 1
    else:
        nextRule = max(r.number for r in rules) + 1

    while True:
        candidates = maxrepeat(startRHS)
        if len(candidates) > WIDTH:
            candidates = candidates[: WIDTH]
        if len(candidates) < 1:
            outQueue.put(startRHS, rules)

        if depth > D_MAX:
            newStart, newRule = replace(
                startRHS, candidates[0][0], candidates[0][1], nextRule
            )
            rules.append(newRule)
            outQueue.put(compressGrammar_mp(newStart, rules, depth + 1, myQueue))
        else:
            # descend the tree
            minLen = sys.maxint
            for c in candidates:
                newStart, newRule = replace(startRHS, c[0], c[1], nextRule)
                newRules = rules + [newRule]
                candStart, candRules = compressGrammar(
                    newStart, newRules, depth + 1
                )
                if gramLength(candStart, candRules) < minLen:
                    minLen = gramLength(candStart, candRules)
                    minGram = candStart, candRules
            return minGram


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
def replace(fullstr, substr, locations, ruleNum):
    g = deepcopy(fullstr)
    newRule = Production('R', ruleNum, substr)
    for start, end in locations:
        for i in range(start, end):
            g[i] = None
        g[start] = newRule

    while None in g:
        g.remove(None)

    return g, newRule


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


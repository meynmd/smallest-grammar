#!/bin/python

import sys
import music21
from copy import deepcopy
from maxrepeat import *
from symbols import *

D_MAX = 3
WIDTH = 50

RuleNum = 1

"""
startRHS    list    the stuff on the right hand side of the start symbol
depth       int     current depth in search tree
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


def gramLength(start, rules):
    return len(start) + \
           sum([len(r.rhs) for r in rules]) + \
           len(rules) + 1


def replace(fullstr, substr, locations, ruleNum):
    g = deepcopy(fullstr)
    newRule = Production('R', ruleNum, substr)
    for start, end in locations:
        for i in range(start, end):
            g[i] = None
        g[start] = newRule

    while None in g:
        g.remove(None)

    # g.append(newLHS)
    # g += list(substr)

    return g, newRule


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


def cleanupRuleNums(rules):
    # count = 0
    # for q in rules:
    #     count += 1
    #     for r in rules:
    #         for s in r.rhs:
    #             if type(s) is not str and type(s) is not int:
    #                 if
    count = 0
    for r in rules:
        count += 1
        r.number = count

    return rules


################################################################################
# script
################################################################################
s = music21.converter.parse('bf10i.krn')
prevNote = None
notes = []
for i, n in enumerate(s.parts[0].flat.notes):
    if type(n) == music21.note.Note:
        if prevNote is None:
            prevNote = n
        else:
            notes.append(
                music21.interval.notesToGeneric(prevNote, n).simpleDirected
            )
            prevNote = n

print 'input: {}'.format(notes)

initRHS, rules = compressGrammar(notes, [], 0)
rules = cleanupRuleNums(rules)


startRule = Production('S', 0, initRHS)
rules.insert(0, startRule)
for r in rules:
    printRule(r)

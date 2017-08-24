#!/bin/python

from maxrepeat import *
from symbols import *

D_MAX = 3

def compressGrammar(grammar, depth):
    grammar = grammarToList(grammar)
    # while True:
    #
    # return

def grammarToList(grammarDictionary):
    grammarList = []
    count = 0
    for key, val in grammarDictionary.items():
        count += 1
        grammarList.append(key)
        grammarList += val

    return grammarList


teststr = list("fabcdeabcgabcfeab")

print maxrepeat(teststr)

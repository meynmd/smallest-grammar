from sys import argv
from collections import defaultdict
import music21
from reexpand import *

if len(argv) != 2:
    print 'usage: countrules.py GRAMMAR_FILE'
    exit(1)
with open(argv[1], 'r') as fp:
    grammar = readGram(fp.readlines())

startSymbols = [s for s in grammar.keys() if s[0] == 'S']
derived = [
    ['({}'.format(ss)] + reexpand(ss, music21.note.Note(), grammar)[0] + ['{})'.format(ss)]
           for ss in startSymbols
]
ruleCountDict = defaultdict(lambda: defaultdict(int))
ruleOccurDict = defaultdict(list)


def enumRule(rhs, name):
    out = []
    for i, sym in enumerate(rhs):
        if sym[0] == '(':
            if sym[1:] not in ruleOccurDict:

                # inner = enumRule(rhs[i + 1:], sym[1:])

                enumRule(rhs[i + 1:], sym[1:])

                # ruleOccurDict[sym[1:]] = inner
        elif sym[-1] == ')':
            if sym[:-1] == name:
                ruleOccurDict[sym[:-1]] = out
                return
                # return out
        else:
            out.append(sym)



for ss in derived:
    enumRule(ss[1:], ss[0])

cleaned = []
for d in derived:
    cleaned.append([s.strip('(').strip(')') for s in d])
for i, line in enumerate(cleaned):
    label = line[0]
    for s in line:
        if s[0] == 'R':
            ruleCountDict[s][label] += 1

for r, lhs_count in ruleCountDict.items():
    print '{}:\t'.format(r),
    print ruleOccurDict[r]
    total = 0
    occurrences = []
    for lhs, count in lhs_count.items():
        occurrences.append('{}:\t{}'.format(lhs, count))
        total += count
    for occ in occurrences:
        print '\t{}'.format(occ)
    if total > 10 and len(lhs_count.keys()) > 4 and len(lhs) > 3:
        frag = music21.stream.Stream()
        for n in ruleOccurDict[r]:
            frag.append(music21.note.Note(n))
        occurString = '\n'.join(occurrences)
        frag.metadata = music21.metadata.Metadata(title='{}\n{}'.format(r, occurString))
        frag.show(app='~/MuseScore-2.1-x86_64.AppImage')

    print
